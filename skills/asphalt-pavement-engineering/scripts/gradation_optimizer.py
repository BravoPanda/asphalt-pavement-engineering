# -*- coding: utf-8 -*-
"""
沥青混合料自动配仓与级配优化求解器
(Zero-Dependency Gradation Blending Optimizer & Bailey Method Evaluator)

功能：
1. 输入多档冷/热料仓（含矿粉）实测筛分通过率，自动反算最贴近 JTG 规范中值（或自定义目标）的最优仓比
2. 采用单纯形投影梯度算法（Simplex Projected Gradient Descent），保证非负且总和严格等于 100%，零第三方依赖
3. 自动校核全筛孔上下限合规性、计算集料总比表面积 SA 与贝雷法关键比值 (CA / FAc / FAf)
4. 支持直接读取 examples/*.json 算例一键运行并衔接 oac_recommender.py
"""

import argparse
import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from oac_recommender import calc_surface_area, load_genome


def _project_simplex(v: List[float], target_sum: float = 1.0) -> List[float]:
    """将向量投影到概率单纯形 {x >= 0, sum(x) = target_sum} (Duchi et al. 2008)。"""
    n = len(v)
    u = sorted(v, reverse=True)
    cssv = 0.0
    rho = -1
    for i in range(n):
        cssv += u[i]
        t = (cssv - target_sum) / (i + 1)
        if u[i] - t > 0:
            rho = i
    theta = (sum(u[: rho + 1]) - target_sum) / (rho + 1)
    return [max(x - theta, 0.0) for x in v]


def optimize_blend(
    mix_type: str,
    bins: List[Dict[str, object]],
    target_passing: Optional[Dict[str, float]] = None,
    sieve_weights: Optional[Dict[str, float]] = None,
    max_iter: int = 4000,
) -> dict:
    """
    自动求解最优各仓配比。
    bins: [{"name": "1#仓(10-15mm)", "passing": {"16.0": 100, "13.2": 95, ...}, "min_pct": 0, "max_pct": 100}, ...]
    """
    genome = load_genome()
    grads = genome["gradations"]["gradations"]
    if mix_type not in grads:
        raise ValueError(f"未知混合料类型 '{mix_type}'，可选: {', '.join(grads.keys())}")

    g_mix = grads[mix_type]
    bounds = g_mix["passing_bounds"]
    sieves = list(bounds.keys())
    m = len(bins)
    if m < 2:
        raise ValueError("至少需要 2 档集料仓才能进行级配优化。")

    # 目标通过率：默认取规范上下限中值
    targets = []
    for s in sieves:
        if target_passing and s in target_passing:
            targets.append(float(target_passing[s]))
        else:
            lo, hi = bounds[s]
            targets.append((lo + hi) / 2.0)

    # 关键筛孔加权（4.75mm, 2.36mm, 0.075mm 对体积指标与骨架影响最大）
    default_weights = {"4.75": 2.0, "2.36": 2.0, "0.075": 3.5}
    weights = []
    for s in sieves:
        if sieve_weights and s in sieve_weights:
            weights.append(float(sieve_weights[s]))
        else:
            weights.append(default_weights.get(s, 1.0))

    # 构造矩阵 A (len(sieves) x m)
    A: List[List[float]] = []
    for s in sieves:
        row = []
        for b in bins:
            p_map = {str(float(k)): float(v) for k, v in b["passing"].items()}
            row.append(p_map.get(str(float(s)), 100.0))
        A.append(row)

    # Lipschitz 步长估算
    l_est = 0.0
    for j in range(len(sieves)):
        row_norm_sq = sum(a * a for a in A[j])
        l_est += 2.0 * weights[j] * row_norm_sq
    lr = 1.0 / max(l_est, 1.0)

    # 初始化均匀比例并执行带上下界约束的投影梯度下降
    x = [1.0 / m] * m
    min_bounds = [float(b.get("min_pct", 0.0)) / 100.0 for b in bins]
    max_bounds = [float(b.get("max_pct", 100.0)) / 100.0 for b in bins]

    for _ in range(max_iter):
        grad = [0.0] * m
        for j in range(len(sieves)):
            pred = sum(A[j][i] * x[i] for i in range(m))
            err = pred - targets[j]
            w2 = 2.0 * weights[j] * err
            for i in range(m):
                grad[i] += w2 * A[j][i]

        x_next = [x[i] - lr * grad[i] for i in range(m)]
        # 先截断单仓上下界，再投影回单纯形
        x_next = [max(min_bounds[i], min(max_bounds[i], x_next[i])) for i in range(m)]
        x_next = _project_simplex(x_next, 1.0)
        # 再次微调确保单仓上下界满足
        for _fix in range(3):
            x_next = [max(min_bounds[i], min(max_bounds[i], x_next[i])) for i in range(m)]
            s_val = sum(x_next)
            if abs(s_val - 1.0) > 1e-9:
                x_next = _project_simplex(x_next, 1.0)
        if sum(abs(x_next[i] - x[i]) for i in range(m)) < 1e-9:
            x = x_next
            break
        x = x_next

    # 整理百分比（保留 1 位小数，并校正尾差使总和严格为 100.0）
    pcts = [round(v * 100.0, 1) for v in x]
    diff_sum = round(100.0 - sum(pcts), 1)
    if abs(diff_sum) > 0:
        max_idx = pcts.index(max(pcts))
        pcts[max_idx] = round(pcts[max_idx] + diff_sum, 1)

    # 计算最终合成级配与规范校核
    blended: Dict[str, float] = {}
    sieve_checks = []
    sq_err = 0.0
    out_of_spec = []

    for j, s in enumerate(sieves):
        val = round(sum(A[j][i] * pcts[i] / 100.0 for i in range(m)), 2)
        blended[s] = val
        lo, hi = bounds[s]
        mid = (lo + hi) / 2.0
        ok = lo <= val <= hi
        if not ok:
            out_of_spec.append(f"{s}mm({val}% 超出 [{lo}, {hi}])")
        sq_err += (val - mid) ** 2
        sieve_checks.append({
            "sieve_mm": s,
            "blended_pct": val,
            "lower_pct": lo,
            "upper_pct": hi,
            "mid_pct": round(mid, 1),
            "deviation_from_mid": round(val - mid, 2),
            "in_spec": ok,
        })

    rmse = round(math.sqrt(sq_err / len(sieves)), 2)
    sa = round(calc_surface_area(blended), 2)
    bailey = evaluate_bailey_ratios(g_mix["nmas_mm"], blended)

    return {
        "mix_type": mix_type,
        "mix_name": g_mix["name"],
        "optimal_ratios": [
            {"bin": bins[i]["name"], "ratio_pct": pcts[i]} for i in range(m)
        ],
        "blended_passing": blended,
        "sieve_checks": sieve_checks,
        "all_in_spec": len(out_of_spec) == 0,
        "out_of_spec_sieves": out_of_spec,
        "rmse_vs_mid_pct": rmse,
        "surface_area_m2_per_kg": sa,
        "bailey_ratios": bailey,
    }


def _interp_passing(passing: Dict[str, float], target_sieve: float) -> float:
    """在标准筛孔对数坐标下线性插值任意粒径通过率（用于贝雷法控制筛孔计算）。"""
    pts = sorted([(float(k), float(v)) for k, v in passing.items()])
    if target_sieve <= pts[0][0]:
        return pts[0][1]
    if target_sieve >= pts[-1][0]:
        return pts[-1][1]
    for i in range(len(pts) - 1):
        s1, p1 = pts[i]
        s2, p2 = pts[i + 1]
        if s1 <= target_sieve <= s2:
            if abs(s2 - s1) < 1e-9:
                return p1
            ratio = (math.log(target_sieve) - math.log(s1)) / (math.log(s2) - math.log(s1))
            return p1 + ratio * (p2 - p1)
    return 0.0


def evaluate_bailey_ratios(nmas_mm: float, passing: Dict[str, float]) -> dict:
    """
    计算贝雷法 (Bailey Method) 粗细集料骨架评价比值：
    - PCS (第一控制筛孔) = 0.22 * NMAS
    - HS  (半筛孔)       = 0.50 * NMAS
    - SCS (第二控制筛孔) = 0.22 * PCS
    - TCS (第三控制筛孔) = 0.22 * SCS
    """
    pcs = round(0.22 * nmas_mm, 2)
    hs = round(0.50 * nmas_mm, 2)
    scs = round(0.22 * pcs, 2)
    tcs = round(0.22 * scs, 2)

    p_pcs = _interp_passing(passing, pcs)
    p_hs = _interp_passing(passing, hs)
    p_scs = _interp_passing(passing, scs)
    p_tcs = _interp_passing(passing, tcs)

    ca = round((p_hs - p_pcs) / max(100.0 - p_hs, 1e-6), 2)
    fa_c = round(p_scs / max(p_pcs, 1e-6), 2)
    fa_f = round(p_tcs / max(p_scs, 1e-6), 2)

    return {
        "PCS_mm": pcs,
        "CA": ca,
        "FAc": fa_c,
        "FAf": fa_f,
        "note": "密级配典型推荐: CA=0.50~0.75 (SMA 0.25~0.50), FAc=0.35~0.50, FAf=0.35~0.50",
    }


def format_blend_report(res: dict) -> str:
    lines = [
        "================ 沥青混合料自动配仓与级配优化报告 ================",
        f"混合料类型 : {res['mix_type']} ({res['mix_name']})",
        f"合规判定   : {'PASS (全筛孔满足规范)' if res['all_in_spec'] else 'FAIL (' + ', '.join(res['out_of_spec_sieves']) + ')'}",
        f"中值均方根偏差 RMSE : {res['rmse_vs_mid_pct']}% | 集料比表面积 SA : {res['surface_area_m2_per_kg']} m²/kg",
        "------------------------------------------------------------------",
        "【最优各仓配比】",
    ]
    for item in res["optimal_ratios"]:
        lines.append(f"  {item['bin']:22s} : {item['ratio_pct']:5.1f}%")
    lines.append("------------------------------------------------------------------")
    lines.append(f"{'筛孔(mm)':>8s} | {'合成(%)':>8s} | {'下限':>6s} | {'中值':>6s} | {'上限':>6s} | {'偏差':>7s} | 判定")
    for row in res["sieve_checks"]:
        flag = "OK" if row["in_spec"] else "OUT"
        lines.append(
            f"{row['sieve_mm']:>8s} | {row['blended_pct']:8.2f} | {row['lower_pct']:6.1f} | "
            f"{row['mid_pct']:6.1f} | {row['upper_pct']:6.1f} | {row['deviation_from_mid']:+7.2f} | {flag}"
        )
    b = res["bailey_ratios"]
    lines.append("------------------------------------------------------------------")
    lines.append(f"【贝雷法骨架比值】PCS={b['PCS_mm']}mm | CA={b['CA']} | FAc={b['FAc']} | FAf={b['FAf']}")
    lines.append(f"  参考说明: {b['note']}")
    lines.append("==================================================================")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="沥青混合料自动配仓与级配优化求解器")
    parser.add_argument("input_file", help="包含 mix_type 与 bins 筛分数据的 JSON 文件路径")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出结果")
    args = parser.parse_args()

    with open(args.input_file, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    res = optimize_blend(
        mix_type=cfg["mix_type"],
        bins=cfg["bins"],
        target_passing=cfg.get("target_passing"),
        sieve_weights=cfg.get("sieve_weights"),
    )

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(format_blend_report(res))


if __name__ == "__main__":
    main()
