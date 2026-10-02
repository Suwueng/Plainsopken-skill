# 发布与安装记录

状态核验：2026-10-02。此页记录发布事实；此前整改见[复审计划](plans/review-followup.md)，最新修复与发布交接见[独立审计记录](plans/independent-audit-2026-10-01.md)。

| 日期 | 状态 | 证据与范围 |
|---|---|---|
| 2026-09-28 | 首版提交并公开推送 | [0a4109d](https://github.com/Suwueng/Plainspoken-skill/commit/0a4109d1bd8a42c382b9391ca9dceeb5f2aaaea7)；仓库 [Suwueng/Plainspoken-skill](https://github.com/Suwueng/Plainspoken-skill)，公开，默认分支 main |
| 2026-09-28 | 首版更新到维护者全局安装 | 安装清单记录源提交 `0a4109d`；17 个运行文件与该发布包一致。机器路径与清单只保存在本地 |
| 2026-09-28 | README 补充来源致谢并推送 | [cdd0363](https://github.com/Suwueng/Plainspoken-skill/commit/cdd0363160c1a7deb6f8693eaccf76117aef4cda)；仅文档改动，运行包未变化 |
| 2026-09-28 | 审阅整改在本地实施 | 本轮没有提交、推送或更新全局安装；当前源码不等于已发布版本 |
| 2026-10-02 | 最新版已公开推送 | [604dbfa](https://github.com/Suwueng/Plainspoken-skill/commit/604dbfa5254436377fc2e58877f109c51708d5d4)；维护者授权后正常推送到 `main`，远端提交与本地一致，包含累计整改及 A2–A4 修复；本次未更新全局安装 |
| 2026-10-02 | 仓库名拼写修正 | 按维护者授权将仓库更正为 [Suwueng/Plainspoken-skill](https://github.com/Suwueng/Plainspoken-skill)；同步本地 origin、README 克隆地址和历史文档链接。仅文档与仓库名称变动，运行包未变化 |

本次源码发布包含 17 个运行文件，哈希与受审的最新技能快照一致；68 个工具测试通过，暂存区和本地可达历史隐私扫描无命中。现行题集为 59 题、160 条条件。此前独立执行的 56 题、151 条条件对应其冻结快照；新增三题在最新参考规则修改前后分别完成同会话非盲冒烟，均为 3/3、9/9 通过。本次没有执行最新快照的独立全量评测，完整验证范围见[整改与发布记录](plans/independent-audit-2026-10-01.md#github-发布2026-10-02)。

运行包以 `604dbfa` 为本次源码发布提交；后续发布记录的文档提交补记已核实的事实。

首次公开已完成。初始化、隐私清理和词库清理计划中的“未推送”等语句记录的是当时状态，不表示当前项目仍未公开。每次后续发布仍需维护者审查与明确授权，并核对工程、行为、隐私和第三方许可；本轮发现的两项早期来源许可待核见[第三方声明](../skills/plainspoken/THIRD_PARTY_NOTICES.md)。
