# asphalt-pavement-engineering

> 开放共建的沥青路面工程材料基因组与辅助核验工具集
> An Open-Source Community Skill for Asphalt Pavement Engineering: Materials-Genome Mix Design, Auto-Blending, Field QC, and Data Forensics Audit.

[![CI Verification](https://github.com/BravoPanda/asphalt-pavement-engineering/actions/workflows/ci.yml/badge.svg)](https://github.com/BravoPanda/asphalt-pavement-engineering/actions/workflows/ci.yml)
[![Skills](https://img.shields.io/badge/skills.sh-asphalt--pavement--engineering-blue)](https://skills.sh)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## 💡 项目理念与初衷

公路工程路面施工与室内试验涉及繁杂的技术规范、严格的体积指标与严谨的内业数据链条。

本项目旨在构建一个**开放、透明、互助共建的公路路面工程 AI 技能与工具库**，将 **“沥青材料基因组（Materials Genome Engineering）”** 的正向设计思路与传统 JTG 规范核验相结合——不仅能在试验后核查数据自洽，还能在试验前根据**沥青类型、集料岩性、级配骨架与气候荷载**智能推荐初始油石比、自动反算最优仓比并提前发出配伍风险预警。

> **欢迎共同维护与优化**：各地地材岩性与气候差异极大，本项目面向所有公路同行开放，热烈欢迎提交 Pull Request 贡献地方材料基因卡片、规范勘误或算法改进。每次 PR 均会触发 GitHub Actions 自动测试，经维护者审阅后合并发布。详情见 [贡献指南 (CONTRIBUTING.md)](CONTRIBUTING.md)。

---

## ✨ 核心能力模块

1. **🧬 沥青材料基因组库 (`genome/`) 与初始油石比推荐引擎 (`oac_recommender.py`)**
   - 内置 **4 维可计算基因库**：9 种沥青结合料（50#/70#/90#、SBS I-C/I-D、高粘 HVA、橡胶沥青 AR、高模量 HMA、温拌 WMA）、9 种集料岩性（玄武岩、多孔玄武岩、辉绿岩、石灰岩、花岗岩、安山岩、钢渣、机制砂、RAP）、10 种标准级配骨架（AC/SMA/SUP/OGFC/ATB）及气候荷载基因。
   - **机理 + 经验双驱动**：综合比表面积膜厚机理、集料密度体积等效修正（解决高密度玄武岩/钢渣 vs 石灰岩差异）、集料吸水率吸油补偿、结合料/纤维/RAP 修正与气候荷载微调。
   - 自动输出**推荐初始油石比 $P_{a0}$**、**5 组马歇尔试拌梯度**、**温控窗口**及**岩性-结合料配伍风险预警**（如酸性花岗岩水稳预警、钢渣游离氧化钙预警、表面层石灰岩抗滑预警等）。
2. **⚖️ 自动配仓与级配优化求解器 (`gradation_optimizer.py`)**
   - 零第三方依赖，输入多档冷/热料仓与矿粉实测筛分，自动反算最贴近 JTG 规范中值的各仓最优配比，并自动输出全筛孔合规判定、集料比表面积 $SA$ 及**贝雷法骨架比值 ($CA / FA_c / FA_f$)**。
3. **📐 体积指标核算与现场施工工艺指导 (`volumetric_calculator.py` & `references/`)**
   - 完整覆盖目标/生产/验证三阶段配合比体积参数核算（$VV$、$VMA$、$VFA$、$\gamma_{sb}$、$\gamma_t$）及高速公路全温控施工与平接缝工艺规程。
4. **🔍 内业资料六维自洽与防伪指纹核验 (`data_verification_audit.py`)**
   - 完整性闭环、物理可行性、表内公式勾稽、跨表协同、Grubbs 格拉布斯极值离群检验与等差数列/零方差造假指纹识别。

---

## 🚀 快速安装与体验

### 1. 作为 AI Agent 技能安装
支持 Antigravity、Claude Code、Codex、Cursor、Gemini CLI 等：
```bash
npx skills add BravoPanda/asphalt-pavement-engineering -g -y
```

### 2. 直接运行内置工程工具（纯 Python 标准库，零外部依赖）
```bash
# 查看材料基因库支持的所有结合料、集料与级配
python skills/asphalt-pavement-engineering/scripts/oac_recommender.py --list

# 推荐“玄武岩 + 石灰岩细料 + SBS I-D + SMA-13 + 夏炎热特重交通”的初始油石比
python skills/asphalt-pavement-engineering/scripts/oac_recommender.py \
  --mix SMA-13 --binder SBS_I-D --agg basalt --fine-agg limestone \
  --coarse-ratio 0.76 --climate hot_summer --traffic extra_heavy

# 一键运行经典算例自动配仓求解
python skills/asphalt-pavement-engineering/scripts/gradation_optimizer.py \
  skills/asphalt-pavement-engineering/examples/sma13_basalt_sbs.json

# 运行全量自动化单元测试
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## 🛠️ 项目目录结构

```text
asphalt-pavement-engineering/
├── SKILL.md                                    # 根目录技能入口（与 skills/ 下保持同步）
├── skills/asphalt-pavement-engineering/
│   ├── SKILL.md                                # 技能主说明与全流程工作流
│   ├── genome/                                 # 四维可计算材料基因库 (JSON)
│   │   ├── binders.json                        # 结合料基因库
│   │   ├── aggregates.json                     # 集料岩性基因库
│   │   ├── gradations.json                     # 级配骨架基因库
│   │   └── environments.json                   # 气候与交通荷载基因库
│   ├── scripts/                                # 零依赖 Python 工程计算与核验工具
│   │   ├── oac_recommender.py                  # 材料基因组初始油石比推荐与风险预警引擎
│   │   ├── gradation_optimizer.py              # 自动配仓与贝雷法级配优化求解器
│   │   ├── volumetric_calculator.py            # 马歇尔体积指标快速核算工具
│   │   └── data_verification_audit.py          # 试验数据六维自洽与防伪指纹核验工具
│   ├── references/                             # 行业标准与专业参考手册
│   │   ├── materials_genome_guide.md           # 沥青材料基因组设计原理与油石比推导
│   │   ├── specifications_jtg.md               # JTG 规范关键指标速查表
│   │   ├── field_qc_guide.md                   # 现场施工温控与接缝工艺规程
│   │   └── data_audit_guide.md                 # 内业资料六维防伪审计指南
│   └── examples/                               # 脱敏经典工程算例 (SMA-13 / AC-20 / AC-25)
├── tests/test_suite.py                         # 自动化单元测试套件
├── .github/workflows/ci.yml                    # GitHub Actions 自动化 CI 校验
├── CONTRIBUTING.md                             # 社区贡献与材料基因卡片提交流程
└── LICENSE                                     # MIT 开源许可证
```

---

## 📚 遵循行业标准与规范
- 《公路沥青路面施工技术规范》 (JTG F40-2004)
- 《公路工程质量检验评定标准 第一册 土建工程》 (JTG F80/1-2017)
- 《公路工程沥青及沥青混合料试验规程》 (JTG E20-2011 / JTG 3410-2025)
- 《公路沥青路面设计规范》 (JTG D50-2017)
- 《公路路基路面现场测试规程》 (JTG 3450-2019)

---

## 📄 开源许可证

本项目基于 [MIT License](LICENSE) 开源，欢迎自由交流学习与共建。
