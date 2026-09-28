# 项目约定

这是独立维护的个人技能 Plainspoken，技能标识为 `plainspoken`。上游只作为人工审阅的参考，不自动 pull、merge 或覆盖本项目；来源见 UPSTREAM.md。

现阶段由 Peng Cheng 与 Codex 协作开发。维护者已确认公开身份为 Peng Cheng <chengpengsmc@qq.com>；保留上游作者 MrGeDiao 及引用材料作者的署名和许可。此授权只允许公开上述确切身份，不扩展到其他邮箱、账号或机器路径。

- 使用中文沟通。改动前说明目标和验证方式；存在影响实现的歧义时询问。
- 只修改当前问题涉及的规则或工具，不顺手扩展场景、增加抽象或重排文件。
- 技能源码位于 `skills/plainspoken/`，包含 SKILL.md、references/、agents/、LICENSE 和 THIRD_PARTY_NOTICES.md，是完整技能包。根 LICENSE 是唯一人工维护来源；运行 `python3 scripts/manage.py sync-license` 显式同步技能内的普通文件副本，两份都纳入版本控制。检查、评测准备和安装要求两份逐字节一致，不静默覆盖。README、docs/、evals/、scripts/、tests/ 和本文件用于开发，不随技能安装。
- 改写规则的问题先记录输入和验收条件，再修改规则；事实、术语、数字、限定条件和用户编辑范围优先于风格偏好。
- 测试明确读取当前仓库的 `skills/plainspoken/SKILL.md`；行为评测读取从该源码生成的快照，检查实际使用的路径，避免混用全局已安装版。
- 修改同步工具时运行 `python3 -m unittest discover -s tests -v`；修改规则时运行 `python3 scripts/manage.py check`，并执行相关行为用例。
- 格式检查不能代替行为评测。记录实际使用的模型、技能 commit、输入、输出和判断依据；没有执行的评测标明未执行。
- 临时输入、输出和实验记录放 work/；可复用且已脱敏的用例进入 evals/。
- 全局安装目录只由同步工具更新。日常开发和测试不自动安装、发布或推送；用户要求更新时，从验证通过的干净提交安装。
- 保留上游 MIT 许可与署名，本项目有权授权的新增贡献按 MIT 提供。天文词库是适用独立条款的可选外部资料，当前技能包不附词库数据或原始说明；只提供官方查询与获取链接，可使用用户已有本机资料，私人位置只留 work/。不改词库内容、不混合发布，也不声明为 MIT。

## Harness 导航

- 开发流程、评测记录合同和发布边界：[docs/harness.md](docs/harness.md)。复杂任务在 `docs/plans/` 维护一份计划；小改动使用用例与提交说明。
- 当前规则审计与待验证问题：[docs/audit.md](docs/audit.md)。不要把静态示例问题或结构检查报告当成模型实测结果。
- 用例唯一来源：[evals/cases.json](evals/cases.json)。被测模型只读请求和技能快照，评审者再读验收条件。
- 全部工程检查：`python3 scripts/harness.py check`；行为评测使用 `prepare` / `report`，不会自动调用模型。
- 私人原文、账号、联系方式、机器路径、原始结果只放 `work/`；公开内容优先使用合成材料。提交前扫 `privacy.py --staged`，推送前扫 `privacy.py --history`，不得绕过命中后上传。
- GitHub 推送、历史重写和全局安装须经维护者审查并明确授权；初始化只做本地工作。`.gitignore` 不会清除旧提交中的隐私；三个旧提交、辅助引用和索引中的天文词库已按授权清理，见 [清理记录](docs/plans/dictionary-history-cleanup.md)。仓库外私有备份和被忽略的旧评测快照仍含原件，不得作为公开附件；发布前仍须审查全部拟发布内容与历史。
