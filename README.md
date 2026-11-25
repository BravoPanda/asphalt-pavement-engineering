# asphalt-pavement-engineering

> 沥青路面工程全流程专业技能（配合比设计、施工工艺与内业数据核验一体化）
> An Agent Skill for Asphalt Pavement Engineering: Mix Design, Field Construction QC, and Documentation Audit.

[![Skills](https://img.shields.io/badge/skills.sh-asphalt--pavement--engineering-blue)](https://skills.sh)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 技能简介

本技能针对高速公路及高等级公路沥青路面工程全流程，提供结构化、规程化的人工智能辅助能力。全面涵盖：
1. **配合比设计全流程**：目标配合比、生产配合比与验证设计，集料筛分加权合成，马歇尔试验参数及体积指标（$VV$、$VMA$、$VFA$、$\gamma_{sb}$、$\gamma_t$）精细核算，最佳沥青用量（$OAC$）确定与路用性能检验（高温车辙、低温抗裂、水稳定性、渗水与抗滑）。
2. **现场施工工艺与质控**：透层/粘层/封层油控制，拌和楼生产温度体系（出料、运输、摊铺、压实、终压），两台梯队联合摊铺与非接触式平衡梁基准控制，双钢轮与重型胶轮压路机碾压组合，纵横向平接缝工艺，现场交竣工检测（压实度理论/马歇尔双控、平整度 IRI、构造深度 TD、渗水系数）。
3. **内业资料与数据防伪核验**：六维审核方法论（完整性、物理规律合理性、公式自洽勾稽、跨表一致性、统计离散性与防伪指纹识别、综合评级归档），支持 Grubbs 格拉布斯异常值检验与编造数据指纹检测（零方差、等差数列等）。

## 📚 遵循行业标准与规范
- 《公路沥青路面施工技术规范》 (JTG F40-2004)
- 《公路工程质量检验评定标准 第一册 土建工程》 (JTG F80/1-2017)
- 《公路工程沥青及沥青混合料试验规程》 (JTG E20-2011 / JTG 3410-2025)
- 《公路沥青路面设计规范》 (JTG D50-2017)
- 《公路路基路面现场测试规程》 (JTG 3450-2019)

## 🚀 安装方法

使用开源 Agent Skills CLI 安装：

```bash
# 全局安装
npx skills add BravoPanda/asphalt-pavement-engineering -g -y

# 或在项目内安装
npx skills add BravoPanda/asphalt-pavement-engineering -y
```

在 Antigravity、Claude Code、Codex、Cursor、Gemini CLI 等支持 Agent Skills 的智能体环境中均可直接调用。

## 🛠️ 目录结构

```text
asphalt-pavement-engineering/
├── SKILL.md                              # 核心技能说明与流程定义
├── skills/
│   └── asphalt-pavement-engineering/
│       ├── SKILL.md
│       ├── scripts/
│       │   ├── volumetric_calculator.py  # 体积指标与级配快速核算脚本
│       │   └── data_verification_audit.py# 试验数据六维自洽与防伪核验工具
│       └── references/
│           ├── specifications_jtg.md     # 行业规范关键指标速查手册
│           ├── field_qc_guide.md         # 施工温控与现场工艺操作规程
│           └── data_audit_guide.md       # 试验数据防伪与六维核验审计指南
├── README.md
└── LICENSE
```

## 📄 开源许可证

本项目采用 [MIT License](LICENSE) 授权许可。
