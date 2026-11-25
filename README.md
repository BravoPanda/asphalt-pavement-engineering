# asphalt-pavement-engineering

> 开放共建的沥青路面工程知识库与辅助核验工具集
> An Open-Source Community Skill for Asphalt Pavement Engineering: Mix Design, Field Construction QC, and Documentation Audit.

[![Skills](https://img.shields.io/badge/skills.sh-asphalt--pavement--engineering-blue)](https://skills.sh)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## 💡 项目理念与初衷

公路工程路面施工与室内试验涉及繁杂的技术规范、严格的体积指标与严谨的内业数据链条。

本项目旨在构建一个**开放、透明、互助共建的公路路面工程 AI 技能库**。我们希望将繁琐的行业规程转化为规范化、结构化的数字能力，帮助工程师快速查验指标、核算体积参数并进行试验数据自洽性复核。

> **欢迎共同维护与优化**：工程实践永无止境，各地地材特性与经验各具特色。本项目面向所有公路同行开放，热烈欢迎大家提交 Pull Request 纠错、补充地方经验或优化算法，由项目维护者统一测试审阅后合并发布。详情见 [贡献指南 (CONTRIBUTING.md)](CONTRIBUTING.md)。

---

## 📖 技能核心板块

1. **配合比设计辅助**：
   - 目标配合比、生产配合比与验证设计流程；
   - 矿料级配加权合成计算；
   - 马歇尔试验体积参数（$VV$、$VMA$、$VFA$、$\gamma_{sb}$、$\gamma_t$）精细核算；
   - 最佳油石比确定与路用性能检验（高温车辙、低温抗裂、水稳定性、渗水等）。
2. **现场施工工艺与质量控制**：
   - 施工温控红线体系（出料、运输、摊铺、初压、复压与终压全过程温控）；
   - 摊铺机梯队作业与非接触式平衡梁控制要点；
   - 碾压机械组合与横向平接缝垂直锯缝工艺；
   - 现场实测与交竣工质量评定要求。
3. **内业资料与数据防伪核验**：
   - 试验检测台账六维自洽审核（完整性、物理规律合理性、表内公式勾稽、跨表一致性、统计离散性与综合评级）；
   - 平行试件统计离散性检测（$CV$ 变异系数、Grubbs 格拉布斯离群点检验）；
   - 试验数据编造指纹排查（零方差、等差数列等）。

---

## 📚 遵循行业标准与规范
- 《公路沥青路面施工技术规范》 (JTG F40-2004)
- 《公路工程质量检验评定标准 第一册 土建工程》 (JTG F80/1-2017)
- 《公路工程沥青及沥青混合料试验规程》 (JTG E20-2011 / JTG 3410-2025)
- 《公路沥青路面设计规范》 (JTG D50-2017)
- 《公路路基路面现场测试规程》 (JTG 3450-2019)

---

## 🚀 安装与使用

使用开源 Agent Skills CLI 安装本技能：

```bash
# 全局安装 (支持 Antigravity, Claude Code, Codex, Cursor, Gemini CLI 等)
npx skills add BravoPanda/asphalt-pavement-engineering -g -y

# 或在具体项目内安装
npx skills add BravoPanda/asphalt-pavement-engineering -y
```

---

## 🛠️ 项目目录结构

```text
asphalt-pavement-engineering/
├── SKILL.md                              # 技能定义与核心流程指南
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
├── CONTRIBUTING.md                       # 社区贡献与 PR 审核指南
├── README.md                             # 项目说明
└── LICENSE                               # MIT 开源许可证
```

---

## 📄 开源许可证

本项目基于 [MIT License](LICENSE) 开源，欢迎在注明出处的前提下自由交流学习与二次开发。
