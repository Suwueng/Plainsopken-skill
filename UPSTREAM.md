# 来源与人工移植记录

本项目独立初始化 Git 历史，维护个人技能 Plainspoken（`plainspoken`）；不与上游建立 fork 关系，不自动合并更新。

现阶段开发由 Peng Cheng 与 Codex 协作完成；维护者公开身份为 Peng Cheng <chengpengsmc@qq.com>。上游通用技能作者为 MrGeDiao，天文词库及其他引用材料仍归各自作者，适用各自的许可或使用约定。

## 初始来源

- 上游仓库：https://github.com/MrGeDiao/shuorenhua
- 参考基线：`bddfc58eaaf3b98a7a0a0b558c934dd9b7dcce7e`
- 固定版本：https://github.com/MrGeDiao/shuorenhua/tree/bddfc58eaaf3b98a7a0a0b558c934dd9b7dcce7e
- 本次迁移来源：维护者已安装的 `shuorenhua` 运行副本
- 迁移日期：2026-09-10
- 本地基线提交：`81d17c1`（隐私清理及词库历史清理后；相对 `663c0b3` 仅移除词库数据和原始说明，见[提交映射](docs/plans/dictionary-history-cleanup.md)）
- 项目于 2026-09-10 更名为 Plainspoken；上游仓库名称和历史来源记录保留原样。

基线不是上游原版：它已经包含本地修正、独立编辑参考、天文资料和 Codex UI 元数据。具体修正见 [历史交接记录](docs/plans/initialization.md#迁入前的安装与验收历史)。词库历史清理前，首次提交的 18 个运行文件与迁移时的全局安装版逐字节一致；清理后的基线保留其余 16 个文件的原字节。

## 处理上游更新

1. 阅读上游提交或 PR，确定是否符合个人版的目标。
2. 比较对应文件及语义，保留本项目已有修正；按需手动移植，不用上游整包覆盖。
3. 为改动补充或复用用例，检查事实保留、误杀和编辑范围。
4. 验证后提交，并在下表或提交说明中记录具体来源、取舍和验证结果。

上游自己的评测结果不代表本项目通过了评测。来源基线只说明初始材料出处，不代表本项目追踪到了上游最新版本。

首次本地历史隐私清理只更新维护者邮箱、机器路径和必要的提交引用，旧至新提交映射见[清理记录](docs/plans/privacy-cleanup.md)。该阶段不属于上游移植，也未更改上游 commit、作者署名或词库资料；后续词库历史清理另行记录。

## 当前分发与许可

根 [LICENSE](LICENSE) 保留 Copyright (c) 2026 MrGeDiao，并为 Peng Cheng 有权授权的新增和修改贡献列出 Copyright (c) 2026 Peng Cheng；防御性表述规则另保留 Copyright (c) 2026 Kiterlin。2026-09-28 核验后另保留 Siqi Chen、Hardik Pandya 和 Conor Bronsdon 的 MIT 版权行，早期引用的片段对应及版本不确定处见第三方声明。MIT 正文保持标准文本；“Peng Cheng 与 Codex 协作开发”记录开发过程，不改变上游或第三方材料的权利归属。

根 `LICENSE` 是唯一人工维护来源，`skills/plainspoken/LICENSE` 是通过 `python3 scripts/manage.py sync-license` 显式同步、纳入版本控制的完整普通文件副本；检查、评测准备和安装要求字节一致。随技能分发的 [第三方声明](skills/plainspoken/THIRD_PARTY_NOTICES.md)说明具体来源和许可边界。

当前技能包已将天文词库数据与原始说明移出，改用[官方查询站点](https://nadc.china-vo.org/astrodict/)和[官方获取页面与使用约定](https://nadc.china-vo.org/astrodict/article/download)，也可使用用户已有的本机资料。词库仍归原权利方，适用独立条款，不改授为 MIT，不自动下载或再发布。

初始来源及旧验收记录保留当时事实。三个旧提交及辅助引用、索引中的词库数据和原始说明已按授权清理，见[历史词库清理](docs/plans/dictionary-history-cleanup.md)。仓库外私有备份和被忽略的旧评测快照仍含原件，不作为公开附件。当时的历史清理未改动上游来源与署名，也未执行推送或全局安装。项目随后已首次公开并安装，见[发布记录](docs/releases.md)。

## 移植记录

| 日期 | 上游来源 | 本项目处理 | 验证 |
|---|---|---|---|
| 2026-09-10 | 固定基线 `bddfc58…` 及其本地修订 | 原样迁入现有安装版，建立独立项目 | 18 个文件逐字节一致；未在本次迁移中引入上游新提交 |
| 2026-09-22 | [Kiterlin/anti-defensive-writing `2d4f9bf…`](https://github.com/Kiterlin/anti-defensive-writing/tree/2d4f9bf471677741721319771a21caed7a74e1cf)，MIT | 改编防御性表述的功能判断；保留必要限定，沿用本项目的保真与编辑范围；另写合成示例 | 本机来源入口及代理元数据与固定版本逐字节一致，MIT 正文一致；行为验证见[改进计划](docs/plans/anti-defensive-writing.md) |

2026-09-28 对早期来源重新核验，记录“来源 → 对应片段 → 已知采用或本次对照版本 → 许可”，见[完整对应表](skills/plainspoken/THIRD_PARTY_NOTICES.md#早期参考来源核验2026-09-28)。三个外部参考确认为 MIT；另两个未找到明确许可，随后按维护者决定[撤下已识别的待核采用组](skills/plainspoken/THIRD_PARTY_NOTICES.md#待核采用内容撤下2026-09-28)。保留历史署名与版本不确定记录；撤下不等于取得许可，也不改变先前发布的授权状态。
