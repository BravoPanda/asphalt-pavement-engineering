# 贡献指南 (Contributing Guide)

感谢您对 **asphalt-pavement-engineering** 开源技能库的关注与支持！

公路工程规范与现场实践博大精深，各地地材特性、气候条件与施工经验各有差异。我们发起本项目的初衷，是希望为广大道路工程师、一线试验技术人员及科研师生提供一个**开放、规范、自洽的 AI 辅助工具库**。

无论是一处公式符号勘误、新版规范更新，还是核验算法的改进，我们都热烈欢迎您的贡献！

---

## 🤝 协作模式与流程

本项目采用 GitHub 标准的 **Fork & Pull Request (PR)** 协作流程：

1. **Fork 本仓库**：点击右上角 `Fork` 按钮，将项目复制到您的个人 GitHub 空间。
2. **克隆到本地并创建分支**：
   ```bash
   git clone https://github.com/<您的用户名>/asphalt-pavement-engineering.git
   cd asphalt-pavement-engineering
   git checkout -b feature/your-improvement
   ```
3. **进行修改与完善**：
   - 保持内容符合中国公路交通行业现行权威规范（如 JTG 系列标准）。
   - 代码工具（Python）应保持自洽、无多余复杂外部依赖。
   - 严禁提交包含个人真实私隐、具体商业项目标段的敏感非脱敏数据。
4. **提交并推送到您的分支**：
   ```bash
   git commit -m "docs: 补充某规范最新试验指标说明"
   git push origin feature/your-improvement
   ```
5. **发起 Pull Request (PR)**：
   - 在 GitHub 界面向本项目 `main` 分支发起 PR。
   - 简要描述修改内容、相关规范条款或算法逻辑。
   - **由维护者（Maintainer）审阅与验证无误后合并发布**。

---

## 💡 欢迎贡献的方向

- **行业标准勘误与更新**：交通运输部最新发布的试验规程（如 JTG 3410）、施工规范、地方标准差异对比。
- **配合比算法优化**：如 Superpave、SMA 等级配设计辅助算法、马歇尔试验体积指标精细计算。
- **内业数据审核逻辑**：提供更精准的异常值检验、数据合理性边界与统计分析方法。
- **施工工艺与通病防治**：针对离析、平整度衰减、早期破损等现场问题的技术预防与控制要点。

---

再次感谢每一位致力于提升公路工程数字化与规范化水平的同行！
