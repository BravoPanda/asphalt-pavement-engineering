# -*- coding: utf-8 -*-
"""
沥青混合料材料基因组初始油石比智能推荐引擎
(Materials-Genome-Driven Initial OAC & Trial Gradient Recommender)

融合四维材料基因库 (结合料 / 集料岩性 / 级配骨架 / 气候交通)：
1. 基于比表面积与目标沥青膜厚度的机理估算（支持输入实测合成级配或仅选级配类型）
2. 基于体积等效原则的集料密度修正（如玄武岩/钢渣 vs 石灰岩）
3. 基于 JTG 吸收系数的集料吸水率沥青吸收补偿
4. 结合料类型、木质素纤维、RAP 回收料与气候荷载多因素修正
5. 自动输出 5 组马歇尔试拌油石比梯度、施工温控窗口与配伍风险预警

零第三方依赖，仅使用 Python 标准库。
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple


GENOME_DIR = Path(__file__).resolve().parent.parent / "genome"


def load_genome() -> Dict[str, dict]:
    """加载四维材料基因库 JSON 文件。"""
    files = {
        "binders": GENOME_DIR / "binders.json",
        "aggregates": GENOME_DIR / "aggregates.json",
        "gradations": GENOME_DIR / "gradations.json",
        "environments": GENOME_DIR / "environments.json",
    }
    data = {}
    for key, path in files.items():
        with open(path, "r", encoding="utf-8") as f:
            data[key] = json.load(f)
    return data


def calc_surface_area(passing: Dict[str, float]) -> float:
    """
    按 JTG F40-2004 附录 B 表面积系数法计算集料总比表面积 SA (m^2/kg)。
    passing: 筛孔(mm字符串或浮点) -> 通过率(%) 字典
    """
    norm = {str(float(k)): float(v) for k, v in passing.items()}
    coeffs = [
        ("4.75", 0.41),
        ("2.36", 0.82),
        ("1.18", 1.64),
        ("0.6", 2.87),
        ("0.3", 6.14),
        ("0.15", 12.29),
        ("0.075", 32.77),
    ]
    sa_times_100 = 0.41
    for sieve, c in coeffs:
        sa_times_100 += c * norm.get(sieve, 0.0)
    return sa_times_100 / 100.0


def calc_absorption_coeff(wx_pct: float) -> float:
    """JTG F40 沥青吸收系数 C（基于集料吸水率 wx, %）。"""
    c = 0.033 * (wx_pct ** 2) - 0.2936 * wx_pct + 0.9339
    return max(0.35, min(0.90, c))


def recommend_oac(
    mix_type: str,
    binder_type: str,
    coarse_agg: str,
    fine_agg: Optional[str] = None,
    coarse_ratio: float = 0.65,
    climate: str = "temperate",
    traffic: str = "heavy",
    fiber_pct: Optional[float] = None,
    rap_pct: float = 0.0,
    passing: Optional[Dict[str, float]] = None,
    gamma_sb_override: Optional[float] = None,
    water_abs_override: Optional[float] = None,
    layer: str = "surface",
) -> dict:
    """
    执行基于材料基因组的初始油石比推荐与风险评估。
    """
    genome = load_genome()
    binders = genome["binders"]["binders"]
    aggs = genome["aggregates"]["aggregates"]
    grads = genome["gradations"]["gradations"]
    climates = genome["environments"]["climates"]
    traffics = genome["environments"]["traffic_levels"]

    if mix_type not in grads:
        raise ValueError(f"未知混合料类型 '{mix_type}'，可选: {', '.join(grads.keys())}")
    if binder_type not in binders:
        raise ValueError(f"未知结合料类型 '{binder_type}'，可选: {', '.join(binders.keys())}")
    if coarse_agg not in aggs:
        raise ValueError(f"未知粗集料岩性 '{coarse_agg}'，可选: {', '.join(aggs.keys())}")
    if fine_agg is not None and fine_agg not in aggs:
        raise ValueError(f"未知细集料岩性 '{fine_agg}'，可选: {', '.join(aggs.keys())}")
    if climate not in climates:
        raise ValueError(f"未知气候分区 '{climate}'，可选: {', '.join(climates.keys())}")
    if traffic not in traffics:
        raise ValueError(f"未知交通等级 '{traffic}'，可选: {', '.join(traffics.keys())}")

    g_mix = grads[mix_type]
    g_binder = binders[binder_type]
    g_coarse = aggs[coarse_agg]
    g_fine = aggs[fine_agg] if fine_agg else g_coarse
    g_climate = climates[climate]
    g_traffic = traffics[traffic]

    ref_gamma_sb = genome["aggregates"]["reference_gamma_sb"]  # 2.70
    ref_gamma_b = binders[genome["binders"]["reference_binder"]]["gamma_b"]  # 1.030
    ref_wx = 0.55  # 基准致密石灰岩吸水率 (%)

    # 1. 合成集料毛体积密度与吸水率
    cr = max(0.0, min(1.0, coarse_ratio))
    fr = 1.0 - cr
    if gamma_sb_override is not None:
        eff_gamma_sb = float(gamma_sb_override)
    else:
        eff_gamma_sb = 1.0 / (cr / g_coarse["gamma_sb"] + fr / g_fine["gamma_sb"])

    if water_abs_override is not None:
        eff_wx = float(water_abs_override)
    else:
        eff_wx = cr * g_coarse["water_absorption_pct"] + fr * g_fine["water_absorption_pct"]

    # 2. 基准有效油石比（若提供实测级配则融合比表面积膜厚机理模型）
    base_pa = g_mix["base_pa_pct"]
    sa_value = None
    sa_adj = 0.0
    if passing:
        sa_value = calc_surface_area(passing)
        # 基准中值级配比表面积
        mid_passing = {k: (v[0] + v[1]) / 2.0 for k, v in g_mix["passing_bounds"].items()}
        sa_mid = calc_surface_area(mid_passing)
        # 按目标有效沥青膜厚度 DA (um) 计算比表面积偏离引起的油石比微调
        da_um = g_mix["target_film_um"]
        delta_pbe_sa = (sa_value - sa_mid) * da_um * g_binder["gamma_b"] / 10.0
        sa_adj = max(-0.45, min(0.45, delta_pbe_sa * 0.65))

    pa_after_sa = base_pa + sa_adj

    # 3. 集料密度体积等效修正
    density_factor = (ref_gamma_sb / eff_gamma_sb) * (g_binder["gamma_b"] / ref_gamma_b)
    pa_after_dens = pa_after_sa * density_factor
    density_adj = pa_after_dens - pa_after_sa

    # 4. 集料吸水率与沥青吸收补偿 (相对基准石灰岩 0.55%)
    c_abs = calc_absorption_coeff(eff_wx)
    pba_eff = c_abs * eff_wx * g_binder["gamma_b"]
    pba_ref = calc_absorption_coeff(ref_wx) * ref_wx * ref_gamma_b
    abs_adj = max(-0.15, min(0.85, (pba_eff - pba_ref) * 0.80))

    # 5. 结合料类型修正
    binder_adj = g_binder["oac_offset_pct"]
    # SMA / OGFC 基准已按改性沥青习惯考虑一部分，避免重复放大
    if g_mix["structure_type"] in ("gap_graded_skeleton", "open_graded_porous") and binder_type in ("SBS_I-C", "SBS_I-D"):
        binder_adj = round(binder_adj * 0.5, 2)

    # 6. 纤维吸油修正（SMA/OGFC 基准已含默认纤维，仅对偏离默认掺量部分修正）
    actual_fiber = g_mix["fiber_default_pct"] if fiber_pct is None else float(fiber_pct)
    fiber_adj = (actual_fiber - g_mix["fiber_default_pct"]) * 0.85

    # 7. 气候与交通荷载微调
    climate_adj = g_climate["oac_offset_pct"]
    traffic_adj = g_traffic["oac_offset_pct"]

    total_pa = pa_after_dens + abs_adj + binder_adj + fiber_adj + climate_adj + traffic_adj
    total_pa = round(max(3.0, min(8.5, total_pa)), 2)
    total_pb = round(total_pa / (100.0 + total_pa) * 100.0, 2)

    # 8. RAP 回收料新沥青折减估算
    rap_info = None
    if rap_pct > 0:
        rap_res_binder = aggs["rap"]["residual_binder_pct"]
        # 默认旧沥青有效利用率 0.75
        effective_old_pb = (rap_pct / 100.0) * rap_res_binder * 0.75
        new_pb_needed = round(max(1.5, total_pb - effective_old_pb), 2)
        rap_info = {
            "rap_pct": rap_pct,
            "assumed_old_binder_pct": rap_res_binder,
            "effective_old_binder_contribution_pct": round(effective_old_pb, 2),
            "estimated_new_binder_pb_pct": new_pb_needed,
        }

    # 9. 5 组马歇尔试拌油石比梯度
    step = 0.3 if g_mix["structure_type"] in ("gap_graded_skeleton", "open_graded_porous") else 0.5
    trial_gradient = [round(total_pa + i * step, 2) for i in (-2, -1, 0, 1, 2)]

    # 10. 岩性-结合料-结构配伍风险预警
    warnings: List[str] = []
    warnings.extend(g_coarse.get("warnings", []))
    if fine_agg and fine_agg != coarse_agg:
        for w in g_fine.get("warnings", []):
            if w not in warnings:
                warnings.append(w)

    if layer == "surface" and coarse_agg == "limestone":
        warnings.append("【抗滑预警】高速公路表面层采用石灰岩粗集料易导致后期磨光抗滑不足（PSV偏低），建议更换玄武岩/辉绿岩。")
    if g_mix["structure_type"] == "gap_graded_skeleton" and g_binder["category"] == "neat":
        warnings.append("【结构配伍预警】SMA 骨架密实混合料通常要求采用 SBS 改性沥青，使用基质沥青易发生析漏与高温车辙。")
    if g_mix["structure_type"] == "open_graded_porous" and binder_type != "HVA":
        warnings.append("【结构配伍预警】OGFC 大空隙排水路面强烈建议使用高粘改性沥青(HVA)，以保障飞散损失与抗松散耐久性。")
    if g_coarse["acidity"] == "acidic" and climate == "heavy_rain":
        warnings.append("【水损叠加高危预警】酸性集料叠加多雨潮湿气候，必须强制执行消石灰+抗剥落剂双保险并复核冻融劈裂 TSR。")
    if rap_pct >= 25.0:
        warnings.append("【大掺量再生预警】RAP 掺量≥25%，必须检测旧沥青老化程度并配套再生剂，防止低温开裂。")
    if actual_fiber < 0.25 and g_mix["structure_type"] == "gap_graded_skeleton":
        warnings.append("【析漏风险预警】SMA 木质素纤维掺量低于 0.25%，务必重点验证谢伦堡析漏损失（≤0.1%）。")

    return {
        "inputs": {
            "mix_type": mix_type,
            "mix_name": g_mix["name"],
            "binder_type": binder_type,
            "binder_name": g_binder["name"],
            "coarse_agg": g_coarse["name"],
            "fine_agg": g_fine["name"],
            "coarse_ratio": cr,
            "climate": g_climate["name"],
            "traffic": g_traffic["name"],
            "fiber_pct": actual_fiber,
            "layer": layer,
        },
        "effective_aggregate_properties": {
            "gamma_sb": round(eff_gamma_sb, 3),
            "water_absorption_pct": round(eff_wx, 2),
            "surface_area_m2_per_kg": round(sa_value, 2) if sa_value is not None else None,
        },
        "recommendation": {
            "initial_pa_pct": total_pa,
            "initial_pb_pct": total_pb,
            "marshall_trial_pa_gradient_pct": trial_gradient,
            "gradient_step_pct": step,
        },
        "breakdown_pct": {
            "base_pa": round(base_pa, 2),
            "surface_area_adj": round(sa_adj, 2),
            "density_equivalence_adj": round(density_adj, 2),
            "absorption_compensation_adj": round(abs_adj, 2),
            "binder_type_adj": round(binder_adj, 2),
            "fiber_adj": round(fiber_adj, 2),
            "climate_adj": round(climate_adj, 2),
            "traffic_adj": round(traffic_adj, 2),
        },
        "process_and_spec_targets": {
            "mixing_temp_c": g_binder["mixing_temp_c"],
            "compaction_temp_c": g_binder["compaction_temp_c"],
            "vv_range_pct": g_mix["vv_range"],
            "vma_min_pct": g_mix["vma_min"],
            "vfa_range_pct": g_mix["vfa_range"],
            "min_ds_modified": g_climate["min_ds_modified"],
            "min_low_temp_strain_ue": g_climate["min_strain_ue"],
        },
        "rap_adjustment": rap_info,
        "warnings": warnings,
    }


def format_report(res: dict) -> str:
    """格式化输出中文工程推荐报告。"""
    inp = res["inputs"]
    rec = res["recommendation"]
    brk = res["breakdown_pct"]
    agg = res["effective_aggregate_properties"]
    tgt = res["process_and_spec_targets"]

    lines = [
        "================ 沥青材料基因组 · 初始油石比推荐报告 ================",
        f"混合料类型 : {inp['mix_type']} ({inp['mix_name']})",
        f"结合料类型 : {inp['binder_type']} ({inp['binder_name']})",
        f"集料组合   : 粗集料={inp['coarse_agg']} ({inp['coarse_ratio']*100:.0f}%) + 细集料={inp['fine_agg']} ({(1-inp['coarse_ratio'])*100:.0f}%)",
        f"合成特征   : 合成毛体积密度 γsb={agg['gamma_sb']} | 综合吸水率={agg['water_absorption_pct']}%"
        + (f" | 比表面积 SA={agg['surface_area_m2_per_kg']} m²/kg" if agg["surface_area_m2_per_kg"] is not None else ""),
        f"服役环境   : {inp['climate']} | {inp['traffic']} | 纤维掺量={inp['fiber_pct']}%",
        "---------------------------------------------------------------------",
        f"★ 推荐初始油石比 (Pa0) : {rec['initial_pa_pct']:.2f}%  (对应沥青用量 Pb0 = {rec['initial_pb_pct']:.2f}%)",
        f"★ 马歇尔 5 组试拌梯度  : {', '.join(f'{v:.2f}%' for v in rec['marshall_trial_pa_gradient_pct'])}  (步长 {rec['gradient_step_pct']}%)",
        "---------------------------------------------------------------------",
        "【机理与经验分项拆解】",
        f"  1. 级配基准有效油石比   :  {brk['base_pa']:+.2f}%",
        f"  2. 实测级配比表面积微调 :  {brk['surface_area_adj']:+.2f}%",
        f"  3. 集料密度体积等效修正 :  {brk['density_equivalence_adj']:+.2f}%",
        f"  4. 集料吸水率吸油补偿   :  {brk['absorption_compensation_adj']:+.2f}%",
        f"  5. 结合料类型/黏度修正  :  {brk['binder_type_adj']:+.2f}%",
        f"  6. 纤维吸油修正         :  {brk['fiber_adj']:+.2f}%",
        f"  7. 气候与交通荷载微调   :  {brk['climate_adj'] + brk['traffic_adj']:+.2f}% (气候 {brk['climate_adj']:+.2f}%, 交通 {brk['traffic_adj']:+.2f}%)",
        "---------------------------------------------------------------------",
        "【推荐工艺温控与体积目标】",
        f"  拌和出料温度: {tgt['mixing_temp_c'][0]}~{tgt['mixing_temp_c'][1]}℃ | 压实温度: {tgt['compaction_temp_c'][0]}~{tgt['compaction_temp_c'][1]}℃",
        f"  目标空隙率 VV: {tgt['vv_range_pct'][0]}~{tgt['vv_range_pct'][1]}% | VMA ≥ {tgt['vma_min_pct']}% | VFA: {tgt['vfa_range_pct'][0]}~{tgt['vfa_range_pct'][1]}%",
        f"  建议路用门槛: 改性动稳定度 DS ≥ {tgt['min_ds_modified']} 轮/mm | 低温弯曲应变 ≥ {tgt['min_low_temp_strain_ue']} με",
    ]

    if res["rap_adjustment"]:
        rap = res["rap_adjustment"]
        lines.append("---------------------------------------------------------------------")
        lines.append(
            f"【RAP 再生折减】掺量 {rap['rap_pct']}% → 旧沥青有效贡献约 {rap['effective_old_binder_contribution_pct']}%，"
            f"预估新沥青添加量 Pb_new ≈ {rap['estimated_new_binder_pb_pct']}%"
        )

    if res["warnings"]:
        lines.append("---------------------------------------------------------------------")
        lines.append("【材料配伍与工程风险预警】")
        for idx, w in enumerate(res["warnings"], 1):
            lines.append(f"  {idx}. {w}")

    lines.append("=====================================================================")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="沥青材料基因组 · 初始油石比智能推荐工具")
    parser.add_argument("--list", action="store_true", help="列出基因库支持的所有级配、结合料、集料与气候类型")
    parser.add_argument("--mix", default="AC-20", help="混合料级配类型，如 AC-13, AC-20, SMA-13, SUP-20, OGFC-13")
    parser.add_argument("--binder", default="SBS_I-D", help="结合料类型，如 70#, SBS_I-D, HVA, AR, HMA, WMA_SBS")
    parser.add_argument("--agg", default="limestone", help="粗集料岩性，如 basalt, porous_basalt, diabase, limestone, granite, steel_slag")
    parser.add_argument("--fine-agg", default=None, help="细集料岩性（默认与粗集料相同）")
    parser.add_argument("--coarse-ratio", type=float, default=0.65, help="粗集料质量占比 (0~1)")
    parser.add_argument("--climate", default="temperate", help="气候分区: hot_summer, temperate, cold_winter, severe_cold, heavy_rain")
    parser.add_argument("--traffic", default="heavy", help="交通荷载等级: light, medium, heavy, extra_heavy")
    parser.add_argument("--fiber", type=float, default=None, help="木质素/玄武岩纤维掺量 (%%)")
    parser.add_argument("--rap", type=float, default=0.0, help="RAP 回收料掺量 (%%)")
    parser.add_argument("--layer", default="surface", choices=["surface", "middle", "bottom", "base"], help="路面结构层位")
    parser.add_argument("--gamma-sb", type=float, default=None, help="实测合成毛体积相对密度（覆盖基因库默认值）")
    parser.add_argument("--water-abs", type=float, default=None, help="实测综合吸水率 %%（覆盖基因库默认值）")
    parser.add_argument("--passing-file", default=None, help="包含实测合成级配通过率 JSON 的算例文件路径")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出结果")

    args = parser.parse_args()
    if args.list:
        g = load_genome()
        print("支持混合料级配 :", ", ".join(g["gradations"]["gradations"].keys()))
        print("支持结合料类型 :", ", ".join(g["binders"]["binders"].keys()))
        print("支持集料岩性   :", ", ".join(g["aggregates"]["aggregates"].keys()))
        print("支持气候分区   :", ", ".join(g["environments"]["climates"].keys()))
        print("支持交通等级   :", ", ".join(g["environments"]["traffic_levels"].keys()))
        return

    passing = None
    if args.passing_file:
        with open(args.passing_file, "r", encoding="utf-8") as f:
            raw = json.load(f)
            passing = raw.get("passing", raw)

    res = recommend_oac(
        mix_type=args.mix,
        binder_type=args.binder,
        coarse_agg=args.agg,
        fine_agg=args.fine_agg,
        coarse_ratio=args.coarse_ratio,
        climate=args.climate,
        traffic=args.traffic,
        fiber_pct=args.fiber,
        rap_pct=args.rap,
        passing=passing,
        gamma_sb_override=args.gamma_sb,
        water_abs_override=args.water_abs,
        layer=args.layer,
    )

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(format_report(res))


if __name__ == "__main__":
    main()
