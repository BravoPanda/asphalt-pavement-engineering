# 贡献指南 (Contributing Guide)

感谢您对 **asphalt-pavement-engineering** 开源技能库的关注与支持！

公路工程规范与现场实践博大精深，各地地材特性、气候条件与施工经验各有差异。我们发起本项目的初衷，是希望为广大道路工程师、一线试验技术人员及科研师生提供一个**开放、规范、可计算的 AI 辅助工具库**。

---

## 🤝 协作模式与流程

本项目采用 GitHub 标准的 **Fork & Pull Request (PR)** 协作流程，并已配置 **GitHub Actions 自动化测试**：

1. **Fork 本仓库**：点击右上角 `Fork` 按钮，将项目复制到您的个人 GitHub 空间。
2. **克隆到本地并创建分支**：
   ```bash
   git clone https://github.com/<您的用户名>/asphalt-pavement-engineering.git
   cd asphalt-pavement-engineering
   git checkout -b feature/your-improvement
   ```
3. **进行修改与本地自测**：
   - 保持内容符合中国公路交通行业现行权威规范（JTG 系列标准）。
   - Python 工具保持纯标准库、零复杂外部依赖。
   - 若修改了 `skills/asphalt-pavement-engineering/SKILL.md`，请同步复制到根目录 `SKILL.md`。
   - 严禁提交包含个人真实隐私、具体商业项目标段的敏感非脱敏数据。
   - 提交前在仓库根目录运行全量单元测试确保通过：
     ```bash
     python -m unittest discover -s tests -p "test_*.py" -v
     ```
4. **发起 Pull Request (PR)**：
   - 向本项目 `main` 分支发起 PR，GitHub Actions 将自动运行全套验证。
   - **CI 全部通过并经维护者（Maintainer）审阅批准后合并发布**。

---

## 🧬 特别欢迎：共建“材料基因卡片”

您无需改动复杂代码，只需向 `skills/asphalt-pavement-engineering/genome/` 下的 JSON 文件提交一条脱敏的地方材料或新型结合料参数，即可直接增强整个技能库的推荐能力：

- **结合料基因 (`genome/binders.json`)**：如高弹改性沥青、生物沥青、特种桥面铺装结合料等。
- **集料岩性基因 (`genome/aggregates.json`)**：如凝灰岩、石英岩、闪长岩、再生混凝土骨料等地方典型石料。
- **级配骨架基因 (`genome/gradations.json`)**：如高模量 HMAC、超薄磨耗层 UTC-10、冷再生级配等。
- 也可直接通过仓库的 **`[材料基因]` Issue 模板** 提交参数建议！

---

## 💡 其他欢迎贡献的方向

- **行业标准勘误与更新**：交通运输部最新试验规程（如 JTG 3410）、施工规范、地方标准差异对比。
- **算法优化**：初始油石比机理模型校准、贝雷法与 SMA 骨架嵌挤（$VCA_{\text{mix}} \le VCA_{\text{DRC}}$）校核增强。
- **内业数据审核逻辑**：更精准的异常值检验、数据合理性边界与统计防伪特征。
- **脱敏工程算例**：补充更多典型气候区与结构层的 `examples/*.json` 算例。
