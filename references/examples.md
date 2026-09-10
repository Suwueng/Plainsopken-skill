# 改写示例

> 本文件是解释、示例与操作细则；行为合同的单源是 `SKILL.md`，两处表述不一致时以 `SKILL.md` 为准。

> 以下例句是合成编辑材料，数字、机构、功能与命令不代表真实测量或本 skill 能力；只能在例句给出的范围内改写，不能套入用户材料。

> 每个示例展示同一段内容的 AI 版和人话版。

## 中文示例

### 示例 1：项目介绍

**AI 版：**
> 该项目是一个创新性的解决方案，旨在通过深度整合多种前沿技术，为用户提供全方位、一站式的智能化体验。它不仅能够显著提升工作效率，还能有效降低运营成本，实现真正的降本增效。

**人话版：**
> 这个项目整合多种技术，提供智能化体验，提高工作效率，降低运营成本。

**改了什么：**
- 保留输入的技术整合、体验、效率与成本主张；未给出具体技术、功能或数据，不补产品能力和使用指标。

---

### 示例 2：技术总结

**AI 版：**
> 综上所述，通过对系统架构的全面优化和持续迭代，我们在性能、安全性和可维护性等方面均取得了显著提升。这一成果充分体现了团队在技术创新方面的不懈追求和卓越实力。

**人话版：**
> 我们优化并持续调整了系统架构，提升了性能、安全性和可维护性。

**改了什么：**
- 去掉总结铺垫和团队自夸，保留改造对象及三个改善方面；具体改动和量化依据原文未给出。

---

### 示例 3：消息回复

**AI 版：**
> 好问题！这确实是一个值得深入探讨的话题。让我来为你详细解释一下。首先，我们需要了解的是，这个问题的本质在于……

**人话版：**
> 原文只有回应铺垫，没有给出原因或解决办法。

**改了什么：**
- 不从空泛开场推导缓存原因、TTL 或修复命令。材料不足时说明缺口。

---

### 示例 4：新闻摘要

**AI 版：**
> 在当今快速发展的人工智能领域，OpenAI 近日发布了其最新的大语言模型，引发了业界的广泛关注和热烈讨论。该模型在多个关键指标上实现了显著突破，标志着人工智能技术迈入了一个全新的发展阶段。

**人话版：**
> OpenAI 近日发布了新的大语言模型，受到业界关注和讨论。原文称模型在多个指标上有突破，但未给出型号、具体指标或出处。

**改了什么：**
- 保留原文消息与主张，去掉时代拔高；不补型号、跑分、窗口或价格。此为合成改写材料，不是新闻核实结果。

---

### 示例 5：工程师腔 / 调试腔

**AI 版：**
> 我先拆开看了一下，发现根因偏硬，不太好直接打掉。目前已经把差异收窄了，和刚抓到的现象也对上了。接下来稳稳兜住，落盘之后就能收口。

**人话版：**
> 我先检查了一下，发现原因还不好直接处理。目前已缩小差异，和刚发现的现象一致。接下来怎么处理、记录什么，原文没有写清。

**改了什么：**
- 保留已有动作与不明确之处，不把“偏硬”猜成配置写死，不新增排查数量和方案。

---

### 示例 6：小红书 AI 腔

**AI 版：**
> 姐妹们！今天给大家拆解一个保姆级避坑攻略！这个工具真的绝绝子，狠狠提升了效率！建议收藏！划重点：免费！

**人话版：**
> 这个工具免费，能提高效率。

**改了什么：**
- 保留免费和效率主张，不补工具品牌、使用经历、插件能力或省时数字。

---

### 示例 7：语域混搭

**AI 版：**
> 诚然，这个 bug 的修复确实存在一定的技术复杂度。不过说白了就是绝绝子的体验！我们需要进一步深入探讨其底层逻辑，稳稳把核心链路兜住。综上所述，未来可期。

**人话版：**
> 这个 bug 修起来有些复杂，还需要弄清原理并处理关键流程。

**改了什么：**
- 统一为技术语体，不新增服务数量、超时配置或观察期限。

---

## English Examples

### Example 1: Product description

**AI version:**
> Our groundbreaking platform serves as a testament to the transformative potential of AI, empowering teams to navigate complex challenges and unlock unprecedented levels of productivity. Nestled at the intersection of innovation and practicality, it showcases how cutting-edge technology can foster meaningful collaboration.

**Human version:**
> The platform helps teams work through complex challenges, improve productivity, and collaborate.

**What changed:**
- Removed promotional framing while retaining the stated purposes. No ticket routing feature or performance figure was provided.

---

### Example 2: Technical update

**AI version:**
> We're excited to announce a comprehensive update that significantly enhances performance, bolsters security, and streamlines the developer experience. This pivotal release underscores our commitment to delivering robust, scalable solutions.

**Human version:**
> This update improves performance, strengthens security, and simplifies the developer experience. We remain committed to robust, scalable solutions.

**What changed:**
- Preserved the stated improvements and commitment without adding a CVE, a percentage, configuration counts, or an upgrade guide.

---

### Example 3: Analysis (two-pass demo)

**AI version:**
> The landscape of remote work has undergone a profound transformation. It's not just about working from home — it's about reimagining the very fabric of how we collaborate. Companies that fail to navigate this paradigm shift risk being left behind in an increasingly competitive ecosystem.

**First pass:**
> Remote work has changed how we collaborate, beyond working from home. Companies that do not adapt risk falling behind.

**Second pass:** Keep the first pass. The input does not identify particular companies, communication methods, or measured outcomes; another pass must not invent them.

---

## Two-pass examples | Residual Audit

### 示例 A：公开写作里的一遍 vs 两遍

**原文：**
> 这次把 onboarding 流程改了一遍，新用户从注册到完成首次导入少走了两步。更重要的是，这也说明我们开始真正理解用户在第一天最容易卡住的地方。

**第一遍：**
> 这次把 onboarding 流程改了一遍，新用户从注册到完成首次导入少走了两步。我们也更清楚用户第一天最容易卡在哪里。

**第二遍：**
> 这次把 onboarding 流程改了一遍，新用户从注册到完成首次导入少走了两步。我们也更清楚用户第一天最容易卡在哪里。

**第二遍改了什么：**
- 去掉了 `更重要的是 / 这也说明我们开始真正理解` 这层 narrator 话术
- 保留原文已有判断；不能把最易卡住的位置推断为首次导入
- 没有补新事实，也没有重写整段

### 示例 B：status 场景里的克制 second pass

**原文：**
> 4 月 13 日把重试次数从 2 次调到 5 次。支付超时从 1.9% 降到 0.7%。这次调整也进一步验证了我们的优化方向是正确的。明天继续看晚高峰数据。

**第一遍：**
> 4 月 13 日把重试次数从 2 次调到 5 次。支付超时从 1.9% 降到 0.7%。这次调整说明方向是对的。明天继续看晚高峰数据。

**第二遍：**
> 4 月 13 日把重试次数从 2 次调到 5 次。支付超时从 1.9% 降到 0.7%。明天继续看晚高峰数据。

**第二遍改了什么：**
- 只删掉 `方向是对的` 这种空判断
- 保留日期、数字和下一步，不往更口语的方向抛光
- `status` 场景如果第一遍已经够直接，第二遍就到这里停

---

## Bounded 双合同示例 | Bounded Scope Example

> bounded 的输出分两部分：句内洗过的正文，和一份交用户确认的删除清单。示例（合成文本）：

**原文**

> 在数字化浪潮席卷各行各业的今天，提效工具层出不穷。我们团队过去三个月把周报流程从手填 Excel 改成了机器人自动汇总，每周大约省出两小时。研究表明，重复性事务的自动化能显著提升组织效能。具体做法是：机器人每周五拉取任务系统的状态变更，生成草稿，负责人只补一句风险说明。这不仅仅是一次流程优化，更是一种工作方式的革新。下个月我们准备把例会纪要也接进来。

**正文（句内洗后）**

> 提效工具很多。我们团队过去三个月把周报流程从手填 Excel 改成了机器人自动汇总，每周大约省出两小时。研究表明，重复性事务的自动化能显著提升组织效能。具体做法是：机器人每周五拉取任务系统的状态变更，生成草稿，负责人只补一句风险说明。这不仅仅是一次流程优化，更是一种工作方式的革新。下个月我们准备把例会纪要也接进来。

**建议删除（待确认）**

1. 「研究表明，重复性事务的自动化能显著提升组织效能。」——无源权威铺垫；删掉后该段信息点不变（前后句已经给出做法和收益），也不承担过渡。不建议改写成「听说 / 据说」，那只是把无源说法换个壳。
2. 「这不仅仅是一次流程优化，更是一种工作方式的革新。」——价值拔高收尾；剥掉句式后没有剩余信息，前句（具体做法）和后句（下月计划）直接相接不断裂。

第一句「在数字化浪潮……层出不穷」没有进清单：剥掉铺垫后还剩「提效工具很多」这个实质判断，所以走句内洗，不删整句。

---

## 标注模式示例 | Annotation Mode Examples

> 下面这几组展示同一段文本在 `annotation mode` 和默认改写模式下的区别。

### 示例 A：公开文案里的无源引用

**原文：**
> 研究表明，采用 AI 协作开发的团队交付效率显著提升。业内人士认为，这一趋势将在未来十年持续加速。

**Annotation mode：**
- `问题族`：无源引用
- `触发点`：`研究表明`、`业内人士认为`
- `建议动作`：补具体来源；没有来源且按 rewrite-safe 改写时，删除整条依赖该来源的论断，不只删权威铺垫
- `是否建议改写`：是

**默认改写：**
> 两条论断均缺来源；按 rewrite-safe 删除后，没有可独立保留的正文。

### 示例 B：status 场景里的保守处理

**原文：**
> 数据显示，这次改版显著提升了留存率。业内人士认为，这个方向已经验证可行。

**Annotation mode：**
- `问题族`：无源引用
- `触发点`：`数据显示`、`业内人士认为`
- `建议动作`：在 `status` 场景优先补数据来源和归属，不要改写成像已证实的事实
- `是否建议改写`：是

**默认改写：**
> 这段缺数据来源和观点归属。作为 status，同步时应补具体报表、时间范围或负责人；在补齐之前，不建议把它写成已经证实的结论。

### 示例 C：抽象观点撑成长段（材料不足）

**原文：**
> 语音输入正在成为越来越重要的交互方式。它的价值不仅在于输入效率的提升，更在于它重新定义了人与设备之间的关系。随着技术不断成熟，这一趋势将在更多场景中得到验证，并最终重塑我们的表达习惯。

**Annotation mode：**
- `问题族`：材料不足 + 价值拔高骨架
- `触发点`：`不仅在于……更在于`、`重新定义`、`重塑我们的表达习惯`；原文说的是交互方式的重要性，不是使用人数；其效率、关系和未来趋势主张缺少具体依据
- `建议动作`：清掉拔高和预测。同时说明这段缺的是材料不是措辞——未给具体产品、测量或经历；不估算压缩比例，不把重要性改成人数增长
- `是否建议改写`：是

**默认改写：**
> 语音输入作为交互方式正变得更重要。原文认为，它能提高输入效率、改变人与设备的关系，并预测技术成熟后这种影响会扩展到更多场景、改变表达习惯；这些判断和预测未附依据。

（保留原文的观点和预测范围并指出依据缺口，不将它们改成已经验证的结论。）

### 示例 D：技术文档里的不改案例

**原文：**
> 网关在请求超时后返回 504。缓存服务每 5 分钟刷新一次热点 key。负载均衡器将流量按权重分配到三个后端节点。

**Annotation mode：**
- `问题族`：无明显问题
- `触发点`：系统主语和技术术语都属于正常文档写法
- `建议动作`：保持不动
- `是否建议改写`：否

**默认改写：**
> 网关在请求超时后返回 504。缓存服务每 5 分钟刷新一次热点 key。负载均衡器将流量按权重分配到三个后端节点。
