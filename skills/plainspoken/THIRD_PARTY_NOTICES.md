# 许可与第三方资料声明

## 本技能的 MIT 材料

Plainspoken 基于 MrGeDiao 的 [shuorenhua](https://github.com/MrGeDiao/shuorenhua) 通用技能材料独立维护，参考基线为 [bddfc58eaaf3b98a7a0a0b558c934dd9b7dcce7e](https://github.com/MrGeDiao/shuorenhua/tree/bddfc58eaaf3b98a7a0a0b558c934dd9b7dcce7e)。保留 Copyright (c) 2026 MrGeDiao；Peng Cheng 有权授权的新增和修改贡献按 MIT 提供，并列出 Copyright (c) 2026 Peng Cheng。完整许可见同目录 [LICENSE](./LICENSE)。

项目现阶段由 Peng Cheng 与 Codex 协作开发。此说明记录开发过程，不改变上游及其他第三方材料的作者归属或许可。

## 防御性表述规则的来源

防御性表述的功能判断改编自 Kiterlin 的 [anti-defensive-writing](https://github.com/Kiterlin/anti-defensive-writing)，固定版本为 [2d4f9bf471677741721319771a21caed7a74e1cf](https://github.com/Kiterlin/anti-defensive-writing/tree/2d4f9bf471677741721319771a21caed7a74e1cf)，适用 [MIT 许可](https://github.com/Kiterlin/anti-defensive-writing/blob/2d4f9bf471677741721319771a21caed7a74e1cf/LICENSE)。保留 Copyright (c) 2026 Kiterlin；完整许可声明见同目录 [LICENSE](./LICENSE)。

改编范围为识别多余防御、按句子功能判断必要限定，以及用原文已有信息直接表达。Plainspoken 将其纳入现有保真、scope 与回读规则；示例为本项目另写的合成材料，未移植上游新增事实或加强结论的改写。该来源不覆盖其他既有规则，也不表示本项目沿用上游评测结论。

## 已保留的来源说明

[编辑参考](./references/editing-guide.md#来源与维护交接)记录了固定上游版本的场景样本与提炼范围，包括 [real-samples.md](https://github.com/MrGeDiao/shuorenhua/blob/bddfc58eaaf3b98a7a0a0b558c934dd9b7dcce7e/evals/real-samples.md)、[benchmark-tiers.md](https://github.com/MrGeDiao/shuorenhua/blob/bddfc58eaaf3b98a7a0a0b558c934dd9b7dcce7e/evals/benchmark-tiers.md) 和 [benchmark.md](https://github.com/MrGeDiao/shuorenhua/blob/bddfc58eaaf3b98a7a0a0b558c934dd9b7dcce7e/evals/benchmark.md)。这些出处不代表本项目沿用上游评测结果。

## 早期参考来源核验（2026-09-28）

下表区分已知采用版本与本次对照版本。早期词表随 shuorenhua 本地修订版迁入，缺少逐条导入记录；内容对应只能证明相关，不能据此倒推出当年的具体 commit。链接均固定到本次实际检查的文件。

| 来源 | 本项目中的对应材料 | 版本与可确认程度 | 许可 |
|---|---|---|---|
| MrGeDiao/shuorenhua | 技能入口、场景、编辑范围及通用参考的初始框架 | 已知参考基线 `bddfc58…`，迁入副本另含本地修订；见上文 | [MIT](https://github.com/MrGeDiao/shuorenhua/blob/bddfc58eaaf3b98a7a0a0b558c934dd9b7dcce7e/LICENSE)，MrGeDiao |
| Kiterlin/anti-defensive-writing | `SKILL.md` 防御性表述判断、`operation-manual.md` §16、相应保护与回读规则 | 已知采用 `2d4f9bf…`；未自动跟进后来版本 | MIT，Kiterlin；固定许可见上文 |
| [blader/humanizer](https://github.com/blader/humanizer/blob/225a6f39ac85f76ee48dbad772ea4abe4ed6c9d8/SKILL.md) | 英文表中的意义拔高词、系动词回避，以及结构参考中的空泛重要性与排比等分类 | 本次对照 `225a6f3…`；初始逐条采用版本不明 | [MIT](https://github.com/blader/humanizer/blob/225a6f39ac85f76ee48dbad772ea4abe4ed6c9d8/LICENSE)，Copyright (c) 2025 Siqi Chen |
| [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop/tree/8da1f030185bdfe8471220585162991eaeb970e9) | 英文表开场套话、强调拐杖和商业套话；结构参考中的虚假二元对比、碎片排比与元叙述 | 本次对照 `8da1f03…`；初始逐条采用版本不明 | [MIT](https://github.com/hardikpandya/stop-slop/blob/8da1f030185bdfe8471220585162991eaeb970e9/LICENSE)，Copyright (c) 2025 Hardik Pandya |
| [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing/tree/7cd166c32e91573734f6ed37f4aa4d9e23b18400) | 英文表与 severity 中的三级词表、简单词替代和语境保护思路；本项目数量规则独立维护 | 本次对照 `7cd166c…`；初始逐条采用版本不明 | [MIT](https://github.com/conorbronsdon/avoid-ai-writing/blob/7cd166c32e91573734f6ed37f4aa4d9e23b18400/LICENSE)，Copyright (c) 2026 Conor Bronsdon |
| [SHADOWPR0/beautiful_prose](https://github.com/SHADOWPR0/beautiful_prose/tree/bf44efb7f9706f8f563af3b6913a3784c7c52a12) | 历史英文表开场套话有连续顺序重合；上游首次提交还声明借鉴正面风格契约，逐条归属未闭合 | 本次对照 `bf44efb…`；其全部 5 个可达提交早于上游首次引用，但未发现锁定采用版本的记录 | 未找到明确许可；已按下文撤下识别出的待核采用组，保留历史署名 |
| [Leey21/awesome-ai-research-writing](https://github.com/Leey21/awesome-ai-research-writing/tree/df0af726a79109b8760c1b80d5dfc36ed44a6f1f) | 历史中文表的渲染词与长定语、被动句处理可对应 README 中文去 AI 味部分；上游首次提交已声明该来源，具体原始复制范围不明 | 本次对照 `df0af72…`；按首次引用时间得到的历史候选为 `eb80712…`，两版相关章节字节一致；不能据此确认实际采用 commit | 未找到明确许可；已按下文撤下识别出的待核采用组，保留历史署名 |

前三个外部 MIT 参考的版权行已保留在同目录 LICENSE。后两项没有因保留署名而取得授权，本次选择移除待核采用内容，具体范围见下文；不能用上游总许可证替代原作许可。按 [GitHub 许可说明](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)，仓库公开本身不授予一般复制、分发或衍生使用的许可。

继续追溯确认：shuorenhua [首次提交的来源声明](https://github.com/MrGeDiao/shuorenhua/blob/24195faa870986a4f197d8d161dd3edef57541a4/SKILL.md)已列出这两个来源；对应词表经固定基线与本地迁入版保留至本次撤下前。beautiful_prose 的一组开场短语，如 `At its core`、`In today's world`、`What this means is`，在其正文和上游初始英文表中次序对应；部分也见于其他参考，不能仅凭重合判定独占出处。上游随后[删除 README 致谢行](https://github.com/MrGeDiao/shuorenhua/commit/18f14107b5599f57bc085e97e0111c059c479ad1)，该提交没有删除词表或证明许可问题已解决。

awesome-ai-research-writing 的[历史候选版本](https://github.com/Leey21/awesome-ai-research-writing/blob/eb8071248c1c230858f1b739d69aeb03a5a9b831/README.md)只按首次引用日期确定，用于核对当时已存在的内容，不是已证实的导入版本。其中文章节中的渲染词及句式处理与本项目有对应，但常用词、通用编辑方法的重合不等于整段复制，也不证明不存在改编。README 有把提示词复制到聊天框使用的说明，未找到将其改编并随另一技能包再分发的明确条款。此次检查覆盖两仓库公开分支与标签可达的 5 / 46 个提交、5 / 34 个文本版本（含 beautiful_prose 早期无扩展名的测试文件）；检查范围不包含私下授权或已删除的远端历史。

humanizer 还注明其分类参考 Wikipedia 的 AI 写作迹象页面；本项目未在本轮引入该页面正文，humanizer 的 MIT 不重新许可其引用的网页。中文表中日常观察与社区反馈只有原有概括署名，没有可核验的逐条链接或版本，不写成已逐项确认的原创来源。

来源链接和名称用于说明出处，不是对外部网页、论文、原作或数据库重新授予许可。第三方原作仍适用其自身条款；本项目 MIT 仅覆盖有权按此许可提供的材料。

### 待核采用内容撤下（2026-09-28）

维护者确认先移除待核采用内容，不向作者发出授权询问。本次处理范围为：

- beautiful_prose：撤下英文开场词组中对应的五项；撤下继承的正向风格指导及入口摘要、按句长均匀或节奏变化要求继续润色的条目。`positive-style.md` 只保留本项目本轮讨论确认的 status 和 CSV 两个合成示例，不沿用旧正向合同的章节、示例和检查清单。`structures.md` 原第 18 节及入口、微操作手册中的相应导向已移除。
- awesome-ai-research-writing：撤下中文表整组渲染性强调、痛点替换项和翻译腔小节；撤下入口翻译腔规则及 `structures.md` 原第 6 节的被动句改写指导。保真规则中涉及抽象目的的说明改用本项目目的测试中的整合技术场景，不再使用该来源的痛点替换示例。

保留当前任务确认的事实、术语、条件和编辑范围约束，以及必要重复、原有列表和正常专业语体的保护；没有为避开来源而把旧指导换几个同义词继续使用。原章节编号不顺延，便于历史记录对应。已许可的其他来源和历史作者署名保留。

本次关闭的是当前源码中已识别待核采用组的处置，不是补得原作许可，也不能倒推出完整历史复制范围。旧快照、既有提交和先前发布仍保留其历史事实；本地删除不改变过去的授权状态，本轮没有重写历史或修改已发布版本。

## 天文名词库：可选外部资料

“英汉天文学名词数据库”由中国天文学会天文学名词审定委员会编纂和维护，所有权归中国天文学会所有，适用独立的开放使用约定，不适用本项目 MIT 许可。

- [官方查询站点](https://nadc.china-vo.org/astrodict/)
- [官方获取页面与使用约定](https://nadc.china-vo.org/astrodict/article/download)

当前技能包不附词库数据或其原始说明，也不自动下载词库。使用者可以依据官方条款查询或获取资料，或使用已有本机副本；本项目不将上述链接解释为再次公开分发的授权。不得把本项目 MIT 扩展为词库的商业使用、内容修改或混合再发布许可，具体使用条件以权利方约定为准。
