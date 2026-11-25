# -*- coding: utf-8 -*-
"""
沥青混合料体积指标与级配快速核算工具
(Volumetric Calculator for Asphalt Mixtures)
符合 JTG F40-2004 与 JTG E20-2011 标准
"""

import sys
import argparse

def calc_gamma_sb(proportions, gravities):
    """
    计算集料合成毛体积相对密度 gamma_sb
    proportions: 各集料仓所占矿料总质量的百分比列表 [P1, P2, ..., Pn] (和为100)
    gravities: 各集料仓毛体积相对密度列表 [gamma_1, gamma_2, ..., gamma_n]
    """
    denom = sum(p / g for p, g in zip(proportions, gravities))
    return 100.0 / denom

def calc_volumetrics(gamma_f, gamma_t, gamma_sb, Pb):
    """
    计算体积指标 VV, VMA, VFA
    gamma_f: 试件毛体积相对密度
    gamma_t: 混合料理论最大相对密度
    gamma_sb: 集料合成毛体积相对密度
    Pb: 沥青用量 (Asphalt content, %) = 沥青质量 / 混合料总质量 * 100%
    """
    Ps = 100.0 - Pb
    vv = (1.0 - gamma_f / gamma_t) * 100.0
    vma = (1.0 - (gamma_f / gamma_sb) * (Ps / 100.0)) * 100.0
    vfa = ((vma - vv) / vma) * 100.0 if vma > 0 else 0.0
    return {
        "VV (%)": round(vv, 2),
        "VMA (%)": round(vma, 2),
        "VFA (%)": round(vfa, 1),
        "gamma_f": round(gamma_f, 4),
        "gamma_t": round(gamma_t, 4),
        "gamma_sb": round(gamma_sb, 4)
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="沥青混合料体积指标核算工具")
    parser.add_argument("--gf", type=float, default=2.455, help="试件毛体积相对密度 gamma_f")
    parser.add_argument("--gt", type=float, default=2.555, help="理论最大相对密度 gamma_t")
    parser.add_argument("--gsb", type=float, default=2.712, help="合成毛体积相对密度 gamma_sb")
    parser.add_argument("--pb", type=float, default=4.5, help="沥青用量 Pb (%%)")
    
    args = parser.parse_args()
    res = calc_volumetrics(args.gf, args.gt, args.gsb, args.pb)
    print("========== 沥青混合料体积指标核算结果 ==========")
    for k, v in res.items():
        print(f"  {k:15}: {v}")
    print("================================================")
