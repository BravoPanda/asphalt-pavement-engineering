---
name: asphalt-pavement-engineering
description: 融合“沥青材料基因组（MGE）”正向设计思路的沥青路面工程全流程专业技能。涵盖四维材料基因库（结合料/集料岩性/级配骨架/气候交通）、多因素初始油石比智能推荐与配伍预警、自动配仓级配优化求解（含贝雷法）、目标/生产/验证三级配合比设计及体积指标（VV/VMA/VFA）核算、路用性能检验、高速公路全温控施工工艺与平接缝规程，以及内业试验数据六维自洽与防伪指纹核验，符合 JTG F40-2004、JTG F80/1-2017、JTG E20-2011/JTG 3410-2025 与 JTG D50-2017 标准规范。
---

# 沥青路面工程全流程专业技能 (Asphalt Pavement Engineering Skill)

本技能面向高速公路及高等级公路沥青路面工程，打通 **“材料基因组正向设计 → 三级配合比与自动配仓 → 现场全温控施工 → 内业数据六维防伪核验”** 全生命周期工作流。

---

## 一、标准与规范体系
- **《公路沥青路面施工技术规范》 (JTG F40-2004)**
- **《公路工程质量检验评定标准 第一册 土建工程》 (JTG F80/1-2017)**
- **《公路工程沥青及沥青混合料试验规程》 (JTG E20-2011 / JTG 3410-2025)**
- **《公路沥青路面设计规范》 (JTG D50-2017)**
- **《公路路基路面现场测试规程》 (JTG 3450-2019)**

---

## 二、第一板块：沥青材料基因组正向设计（初始油石比与自动配仓）

本技能内置四维结构化材料基因库（`genome/`），支持室内试验前的正向虚拟筛选与参数推荐，详述见 [materials_genome_guide.md](references/materials_genome_guide.md)：
- **结合料基因 (`genome/binders.json`)**：50#/70#/90# 基质沥青、SBS I-C/I-D、高粘改性（HVA）、橡胶沥青（AR）、高模量（HMA）、温拌 SBS（WMA_SBS）。
- **集料岩性基因 (`genome/aggregates.json`)**：致密玄武岩、多孔玄武岩、辉绿岩、石灰岩、花岗岩、安山岩、钢渣、机制砂、RAP 回收料（含密度、吸水率、酸碱性、磨光值 PSV 及配伍风险标签）。
- **级配骨架基因 (`genome/gradations.json`)**：AC-13/16/20/25、SMA-13/16、SUP-13/20、OGFC-13、ATB-25。
- **环境与荷载基因 (`genome/environments.json`)**：夏炎热/温和/冬寒/冬严寒/潮湿多雨区 + 轻/中/重/特重交通等级。

### 核心正向设计工具
1. **初始油石比智能推荐与风险预警 (`scripts/oac_recommender.py`)**：
   融合集料比表面积膜厚机理、集料密度体积等效修正（如高密度玄武岩/钢渣 vs 石灰岩）、集料吸水率沥青吸收补偿、结合料/纤维/RAP 修正与气候荷载微调，一键输出推荐初始油石比 $P_{a0}$、5 组马歇尔试拌梯度与岩性-沥青配伍风险预警。
2. **自动配仓与级配优化求解器 (`scripts/gradation_optimizer.py`)**：
   输入多档冷/热料仓（含矿粉）实测筛分，自动反算最贴近 JTG 规范中值的各仓最优比例，并校核全筛孔合规性、比表面积 $SA$ 及贝雷法参数（$CA / FA_c / FA_f$）。

---

## 三、第二板块：三级配合比设计与体积指标核算

### 1. 三阶段配合比设计流程
1. **目标配合比设计**：优选原材料 → 自动配仓与初始油石比推荐 → 5 组梯度马歇尔试件确定最佳沥青用量 $OAC$ → 检验高低温、水稳定与渗水性能。
2. **生产配合比设计**：拌和楼二次筛分各热料仓取样 → 确定热料仓供料比例与最佳油石比。
3. **生产配合比验证**：试拌试铺试验段（$100 \sim 200\text{ m}$），复核抽提级配、体积指标并确定标准压实密度。

### 2. 体积指标核心公式（对应工具 `scripts/volumetric_calculator.py`）
- **集料合成毛体积相对密度**：$\gamma_{sb} = \frac{100}{\sum (P_i / \gamma_{sbi})}$
- **理论最大相对密度**：$\gamma_t = \frac{100}{P_s / \gamma_{se} + P_b / \gamma_b}$
- **空隙率**：$VV = (1 - \gamma_f / \gamma_t) \times 100\%$
- **矿料间隙率**：$VMA = \left(1 - \frac{\gamma_f}{\gamma_{sb}} \times \frac{P_s}{100}\right) \times 100\%$
- **沥青有效饱和度**：$VFA = \frac{VMA - VV}{VMA} \times 100\%$

### 3. 路用性能关键门槛（详见 [specifications_jtg.md](references/specifications_jtg.md)）
- **高温稳定性**：60℃ 车辙动稳定度 $DS \ge 2800 \sim 3000\text{ 轮/mm}$（改性沥青/重载交通可提高至 $\ge 5000\text{ 轮/mm}$）。
- **水稳定性**：48h 浸水马歇尔残留稳定度 $MS_0 \ge 85\%$；冻融劈裂强度比 $TSR \ge 80\%$。
- **低温抗裂**：-10℃ 小梁弯曲破坏应变 $\varepsilon_B \ge 2500 \sim 2800\,\mu\varepsilon$。
- **防渗与析漏飞散**：AC 渗水系数 $\le 120\text{ mL/min}$；SMA 谢伦堡析漏 $\le 0.1\%$，肯塔堡飞散 $\le 15\%$。

---

## 四、第三板块：高速公路现场施工工艺与质量控制

详见现场工艺手册 [field_qc_guide.md](references/field_qc_guide.md)：

| 施工阶段 | 普通石油沥青 (AC) | SBS 改性沥青 (AC/SMA) | 关键控制要点 |
| :--- | :--- | :--- | :--- |
| **沥青加热温度** | 150℃ ~ 160℃ | 160℃ ~ 170℃ | 严防局部过热老化 |
| **矿料加热温度** | 160℃ ~ 180℃ | 185℃ ~ 195℃ | 高于沥青温度 10~15℃ |
| **混合料出料温度** | 140℃ ~ 165℃ | 170℃ ~ 185℃ | 超过 195℃ 必须废弃 |
| **运抵现场温度** | $\ge 140$℃ | $\ge 165$℃ | 双层保温帆布严密覆盖 |
| **开始摊铺温度** | $\ge 135$℃ | $\ge 160$℃ | 低温施工要求 $\ge 165$℃ |
| **初压 / 复压 / 终压** | 130~140 / 100~120 / $\ge 70$℃ | 150~165 / 130~140 / $\ge 90$℃ | 高频低幅紧跟慢压，SMA 严禁胶轮 |

- **摊铺与接缝**：双机梯队热接缝（搭接 3~6cm），表面层采用非接触式平衡梁；横向接缝全部采用垂直锯缝平接缝并先横向起压。
- **交竣工验收 (JTG F80/1-2017)**：马歇尔压实度 $\ge 96\%$（改性 $\ge 98\%$）、理论密度压实度 $\ge 93\%$（改性 $\ge 94\%$）；激光平整度 $IRI \le 1.0 \sim 1.2\text{ m/km}$；构造深度 $TD \ge 0.55 \sim 0.8\text{ mm}$。

---

## 五、第四板块：内业资料与试验数据六维防伪核验

详见审核指南 [data_audit_guide.md](references/data_audit_guide.md)（对应工具 `scripts/data_verification_audit.py`）：

1. **完整性闭环**：委托单、原始记录、平行试件数（马歇尔 $\ge 4$、车辙板 $\ge 3$）及签字日期齐全。
2. **物理可行性**：严格校验 $\gamma_t > \gamma_f$、$VMA > VV > 0$、通过率单调递增。
3. **表内公式勾稽**：密度偏差 $\le 0.004$、空隙率/VMA 偏差 $\le 0.15\%$、VFA 偏差 $\le 0.35\%$。
4. **跨表协同一致**：原材料批次密度与配合比汇总表、时间逻辑链一致。
5. **统计离散与造假指纹**：检测变异系数 $CV$ 异常（零方差）、Grubbs 极值离群点与人为等差数列指纹。
6. **结论评级归档**：输出 `PASS` / `WARN` / `CRITICAL` 三级核验结论。

---

## 六、内置工程脚本快速调用

```bash
# 1. 查看材料基因库支持的所有结合料/集料/级配类型
python scripts/oac_recommender.py --list

# 2. 基于材料基因组推荐初始油石比、5组马歇尔试拌梯度及配伍风险预警
python scripts/oac_recommender.py --mix SMA-13 --binder SBS_I-D --agg basalt --fine-agg limestone --climate hot_summer --traffic extra_heavy

# 3. 多档集料自动配仓与贝雷法骨架校核（支持 examples/ 算例）
python scripts/gradation_optimizer.py examples/sma13_basalt_sbs.json

# 4. 体积指标快速核算与试验数据防伪指纹演示
python scripts/volumetric_calculator.py --gf 2.455 --gt 2.555 --gsb 2.712 --pb 4.5
python scripts/data_verification_audit.py
```
