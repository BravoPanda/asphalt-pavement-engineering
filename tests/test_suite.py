# -*- coding: utf-8 -*-
"""
asphalt-pavement-engineering 仓库自动化测试套件
覆盖：
1. 四维材料基因库 JSON 结构与物理合理性校验
2. 初始油石比推荐引擎 (不同沥青、集料岩性、密度/吸水率修正、RAP、风险预警)
3. 自动配仓与级配优化求解器 (3 个经典算例全筛孔合规校验 + 贝雷法)
4. 体积指标核算脚本与六维数据防伪核验脚本回归测试
5. SKILL.md 同步一致性检查
"""

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "asphalt-pavement-engineering"
SCRIPTS_DIR = SKILL_DIR / "scripts"
EXAMPLES_DIR = SKILL_DIR / "examples"

sys.path.insert(0, str(SCRIPTS_DIR))

from data_verification_audit import check_arithmetic_progression, grubbs_test, verify_sample_group
from gradation_optimizer import optimize_blend
from oac_recommender import calc_surface_area, load_genome, recommend_oac
from volumetric_calculator import calc_gamma_sb, calc_volumetrics


class TestGenomeDatabase(unittest.TestCase):
    def test_genome_schema_and_physical_bounds(self):
        genome = load_genome()
        for key in ("binders", "aggregates", "gradations", "environments"):
            self.assertIn(key, genome)

        for name, b in genome["binders"]["binders"].items():
            self.assertTrue(0.98 <= b["gamma_b"] <= 1.15, f"异常沥青密度: {name}")
            self.assertLess(b["mixing_temp_c"][0], b["mixing_temp_c"][1])
            self.assertLess(b["compaction_temp_c"][0], b["compaction_temp_c"][1])

        for name, a in genome["aggregates"]["aggregates"].items():
            self.assertTrue(2.40 <= a["gamma_sb"] <= 3.60, f"异常集料毛体积密度: {name}")
            self.assertGreaterEqual(a["gamma_sa"], a["gamma_sb"], f"表观密度应不小于毛体积密度: {name}")
            self.assertGreaterEqual(a["water_absorption_pct"], 0.0)

        for name, g in genome["gradations"]["gradations"].items():
            self.assertTrue(3.0 <= g["base_pa_pct"] <= 7.5, f"异常基准油石比: {name}")
            for sieve, (lo, hi) in g["passing_bounds"].items():
                self.assertLessEqual(lo, hi, f"{name} 筛孔 {sieve} 下限大于上限")


class TestOACRecommender(unittest.TestCase):
    def test_density_equivalence_effect(self):
        # 高密度钢渣 vs 普通石灰岩：相同级配下，高密度集料质量法油石比应显著低于石灰岩（即使叠加吸水率补偿也应体现密度折减差异）
        r_limestone = recommend_oac("AC-13", "SBS_I-D", "limestone", climate="temperate", traffic="heavy", layer="middle")
        r_basalt = recommend_oac("AC-13", "SBS_I-D", "basalt", climate="temperate", traffic="heavy", layer="surface")
        self.assertLess(
            r_basalt["breakdown_pct"]["density_equivalence_adj"],
            r_limestone["breakdown_pct"]["density_equivalence_adj"],
        )

    def test_porous_aggregate_absorption_compensation(self):
        # 多孔玄武岩吸水率远高于致密玄武岩，吸油补偿应更大
        r_dense = recommend_oac("SMA-13", "SBS_I-D", "basalt")
        r_porous = recommend_oac("SMA-13", "SBS_I-D", "porous_basalt")
        self.assertGreater(
            r_porous["breakdown_pct"]["absorption_compensation_adj"],
            r_dense["breakdown_pct"]["absorption_compensation_adj"],
        )

    def test_binder_type_differences(self):
        # 橡胶沥青 AR 初始油石比应显著高于 70# 基质沥青
        r_70 = recommend_oac("AC-13", "70#", "basalt")
        r_ar = recommend_oac("AC-13", "AR", "basalt")
        self.assertGreater(r_ar["recommendation"]["initial_pa_pct"], r_70["recommendation"]["initial_pa_pct"] + 1.0)

    def test_acidic_aggregate_and_surface_warnings(self):
        r_granite = recommend_oac("AC-25", "70#", "granite", climate="heavy_rain", layer="bottom")
        joined = " ".join(r_granite["warnings"])
        self.assertIn("酸性", joined)

        r_limestone_surf = recommend_oac("AC-13", "SBS_I-D", "limestone", layer="surface")
        self.assertTrue(any("抗滑" in w for w in r_limestone_surf["warnings"]))

    def test_rap_deduction(self):
        r_rap = recommend_oac("AC-20", "70#", "limestone", rap_pct=30.0, layer="middle")
        self.assertIsNotNone(r_rap["rap_adjustment"])
        self.assertLess(
            r_rap["rap_adjustment"]["estimated_new_binder_pb_pct"],
            r_rap["recommendation"]["initial_pb_pct"],
        )
        self.assertTrue(any("大掺量再生" in w for w in r_rap["warnings"]))

    def test_surface_area_calculation(self):
        sa = calc_surface_area({"4.75": 50, "2.36": 35, "1.18": 25, "0.6": 18, "0.3": 12, "0.15": 9, "0.075": 6})
        self.assertTrue(4.0 <= sa <= 8.0, f"典型 AC-13 比表面积应在 4~8 m2/kg，实得 {sa}")


class TestGradationOptimizerAndExamples(unittest.TestCase):
    def test_all_example_cases_blend_in_spec_and_chain_to_oac(self):
        example_files = sorted(EXAMPLES_DIR.glob("*.json"))
        self.assertGreaterEqual(len(example_files), 3)

        for ex_path in example_files:
            with open(ex_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            blend = optimize_blend(cfg["mix_type"], cfg["bins"])
            ratio_sum = sum(item["ratio_pct"] for item in blend["optimal_ratios"])
            self.assertAlmostEqual(ratio_sum, 100.0, places=1, msg=f"{ex_path.name} 仓比和不为100%")
            self.assertTrue(blend["all_in_spec"], msg=f"{ex_path.name} 存在超标筛孔: {blend['out_of_spec_sieves']}")

            oac = recommend_oac(
                mix_type=cfg["mix_type"],
                binder_type=cfg["binder_type"],
                coarse_agg=cfg["coarse_agg"],
                fine_agg=cfg.get("fine_agg"),
                coarse_ratio=cfg.get("coarse_ratio", 0.65),
                climate=cfg.get("climate", "temperate"),
                traffic=cfg.get("traffic", "heavy"),
                fiber_pct=cfg.get("fiber_pct"),
                passing=blend["blended_passing"],
                layer=cfg.get("layer", "surface"),
            )
            self.assertEqual(len(oac["recommendation"]["marshall_trial_pa_gradient_pct"]), 5)


class TestVolumetricsAndAudit(unittest.TestCase):
    def test_volumetrics_formulas(self):
        gsb = calc_gamma_sb([60, 35, 5], [2.88, 2.69, 2.71])
        self.assertTrue(2.75 < gsb < 2.85)
        vol = calc_volumetrics(gamma_f=2.455, gamma_t=2.555, gamma_sb=2.712, Pb=4.5)
        self.assertAlmostEqual(vol["VV (%)"], 3.91, places=2)
        self.assertGreater(vol["VMA (%)"], vol["VV (%)"])
        self.assertTrue(60.0 < vol["VFA (%)"] < 85.0)

    def test_audit_fingerprints(self):
        self.assertTrue(check_arithmetic_progression([2.451, 2.453, 2.455, 2.457]))
        self.assertFalse(check_arithmetic_progression([2.453, 2.457, 2.452, 2.459]))
        is_out, val, _, _ = grubbs_test([10.2, 10.5, 10.3, 14.8])
        self.assertTrue(is_out)
        self.assertEqual(val, 14.8)
        summary = verify_sample_group("测试组", [2.451, 2.453, 2.455, 2.457])
        self.assertEqual(summary["等差造假指纹"], "疑似等差编造")


class TestRepoConsistency(unittest.TestCase):
    def test_root_and_nested_skill_md_match(self):
        root_md = (REPO_ROOT / "SKILL.md").read_text(encoding="utf-8")
        nested_md = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(root_md, nested_md, "根目录 SKILL.md 与 skills/ 下 SKILL.md 必须保持一致")


if __name__ == "__main__":
    unittest.main(verbosity=2)
