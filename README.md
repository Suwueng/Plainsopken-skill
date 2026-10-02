# Plainspoken

清理中英文里的套话、模板句式和多余辩解，保留事实、术语、限定条件与责任主体。技能标识为 `plainspoken`，适用于日常回复、技术说明、状态同步和公开文章。

## 使用

给出原文和编辑要求即可，例如：

- “请用 plainspoken 把这段写自然一点。”
- “只改句内措辞，保留所有句子和段落。”
- “先标问题，不改写。”

默认只交一份推荐稿，保留原有表达形式，默认保留段落顺序。短文可以删除空话、在段内合并句子；确有阅读中断时，可在编辑范围内局部移动段落，恢复原文已有关系。中文长文默认保序，将尚未授权的整句删除列为建议；局部移动须有明确授权。用户要求只做句内修改时进一步收紧范围。格式转换、跨章节搬移和重新设计篇章属于独立编辑任务。原文已经清楚自然，可以保持原样；在授权范围内清理后确实没有正文时，只给一句简短提示。

例如，状态说明：

> 本次优化显著提升了系统整体性能，并有效改善了用户体验。

可以清理为：

> 这次优化提升了系统性能，并改善了用户体验。

没有测量数据时，不补延迟、百分比或具体功能。Plainspoken 是编辑规则，不判断文本作者是否为 AI，也不保证每次改写正确。

## 安装与更新

仓库已于 2026-09-28 首次公开，发布和维护者安装状态见[发布记录](docs/releases.md)。最新规则整改、工具修复及验证范围见[审计记录](docs/plans/independent-audit-2026-10-01.md)。

在 Codex 中安装需要 Python 3.10+ 和 Git，无必需的第三方 Python 包。先获取仓库，在干净提交上检查并安装：

```sh
git clone https://github.com/Suwueng/Plainspoken-skill.git plainspoken
cd plainspoken
python3 scripts/harness.py check
python3 scripts/manage.py install
```

默认安装到 `$CODEX_HOME/skills/plainspoken`；未设置 CODEX_HOME 时使用 `~/.codex/skills/plainspoken`。只安装 `skills/plainspoken/` 中的完整技能包，不安装开发文档、用例或脚本。全局目录由工具更新，不直接修改安装副本。

安装清单记录源提交和文件哈希；旧版备份到技能扫描目录外。需要回滚时，使用安装工具打印的备份路径：

```sh
python3 scripts/manage.py rollback BACKUP_PATH
```

回滚会核对已有清单与运行文件的一致性，发现缺失、增加或修改就拒绝；无清单的旧包会生成新的本地记录，不声称知道原提交。安装和回滚均不得覆盖开发仓库及其子目录或祖先目录；可用 `--dest` 指定仓库外的隔离目标演练。

若从旧名 `shuorenhua` 迁移，先将旧目录完整备份到技能扫描目录外，避免重复触发；工具不自动迁移旧名。工程检查不调用模型，行为验证需另做。

## 来源与贡献

Plainspoken 从 MrGeDiao 的 [shuorenhua](https://github.com/MrGeDiao/shuorenhua) 本地修订版独立维护，上游只作为人工审阅和选择性移植的参考。

防御性表述规则借鉴并改编自 Kiterlin 的 [anti-defensive-writing](https://github.com/Kiterlin/anti-defensive-writing)：按句子作用区分多余辩解与必要限定，保留证据强度、适用范围和责任说明，纳入 Plainspoken 的保真、编辑范围与回读规则。

现阶段由 Peng Cheng 与 Codex 协作开发。维护者公开身份为 Peng Cheng <chengpengsmc@qq.com>。原作者署名、采用范围、固定版本及待核事项见 [UPSTREAM.md](UPSTREAM.md) 和随技能分发的 [THIRD_PARTY_NOTICES.md](skills/plainspoken/THIRD_PARTY_NOTICES.md)。

有权授权的项目内容按 [MIT](LICENSE) 提供。第三方原作适用各自条款；两个早期参考来源尚未找到明确许可，当前源码已撤下识别出的待核采用内容，保留历史署名和版本不确定性，具体范围见第三方声明。此处置不改变旧发布的授权状态。天文词库不随技能分发，可按独立条款访问[官方查询站点](https://nadc.china-vo.org/astrodict/)与[获取页面](https://nadc.china-vo.org/astrodict/article/download)。

## 开发与验证

| 入口 | 内容 |
|---|---|
| [skills/plainspoken](skills/plainspoken/) | 完整运行包：入口、参考、UI 元数据、许可和第三方声明 |
| [docs/harness.md](docs/harness.md) | 开发、隔离评测、隐私及发布流程 |
| [docs/evaluation-design.md](docs/evaluation-design.md) | 长文、默认力度与误杀用例的设计依据 |
| [evals/cases.json](evals/cases.json) | 唯一用例与验收条件来源 |
| [docs/audit.md](docs/audit.md) | 历史问题和当前处理入口 |

```sh
python3 scripts/harness.py check
python3 scripts/harness.py prepare --run work/runs/my-check
```

`check` 检查结构、用例、候选内容隐私及工具测试；`prepare` 固定当前源码，生成给独立执行会话的请求，不自动调用模型。填入真实输出、执行记录和逐项评审后，用 `python3 scripts/harness.py report --run work/runs/my-check` 汇总。

根 `LICENSE` 是唯一人工维护来源；修改后执行 `python3 scripts/manage.py sync-license`，显式更新技能内副本。两份字节不一致会阻止检查和安装。

真实输入、原始输出、机器路径和私人记录只放被忽略的 `work/`。提交前执行 `python3 scripts/privacy.py --staged`，推送前执行 `python3 scripts/privacy.py --history`，另做人工审查。日常开发不自动提交、推送或更新全局安装。
