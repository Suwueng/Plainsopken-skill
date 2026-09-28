# Plainspoken

中文与英文文本的改写和审阅技能，清理模板表达，同时保留事实、术语、范围与责任主体。技能标识为 `plainspoken`。

项目由 shuorenhua 的一个本地修订版独立维护，上游只供人工审阅和选择性移植，不自动合并。来源与基线见 [UPSTREAM.md](UPSTREAM.md)。

防御性表述规则借鉴并改编自 Kiterlin 的 [anti-defensive-writing](https://github.com/Kiterlin/anti-defensive-writing)：按句子功能区分多余辩解与必要限定，清理冗余包装，同时保留证据强度、适用范围和责任说明。改编已纳入 Plainspoken 现有的保真、编辑范围与回读规则。

本项目现阶段由 Peng Cheng 与 Codex 协作开发。维护者公开身份为 Peng Cheng <chengpengsmc@qq.com>。此声明保留 MrGeDiao 的上游作者署名，以及所引用材料各自的作者归属与使用约定。

## 开发入口

需要 Python 3.10+ 和 Git，无必需的第三方 Python 包。在项目根目录执行：

```sh
python3 scripts/harness.py check
```

它检查运行内容、用例结构、候选文件隐私和隔离单元测试。此命令不调用模型、不联网、不安装技能，也不证明改写质量。[开发流程](docs/harness.md)说明行为评测和发布检查；[初始化审计](docs/audit.md)记录已发现的问题与未覆盖范围。

| 内容 | 用途 | 随技能安装 |
|---|---|---|
| `skills/plainspoken/` | 完整技能包：`SKILL.md`、`references/`、`agents/`、`LICENSE`、`THIRD_PARTY_NOTICES.md` | 是 |
| 根 `LICENSE` | 唯一人工维护的 MIT 许可文本 | 技能内保存逐字节一致的普通文件副本 |
| `AGENTS.md`、`docs/` | 开发约定、审计、任务计划 | 否 |
| `evals/cases.json` | 合成输入及独立验收条件 | 否 |
| `scripts/`、`tests/`、`.githooks/` | 本地检查、评测记录、安装与回滚 | 否 |
| `work/` | 真实输入、原始输出、机器路径及私有记录；Git 忽略 | 否 |

仓库根目录用于开发，`skills/plainspoken/` 可以作为完整技能目录分发，包含许可与第三方声明。本机全局更新仍统一使用安装工具，以保留版本记录和回滚能力，不直接复制整个仓库。

## 行为评测

```sh
python3 scripts/harness.py prepare --run work/runs/baseline
```

工具先检查根与技能内 `LICENSE` 一致，再从本仓库的 `skills/plainspoken/` 复制完整运行文件，记录源 commit、工作树状态和每个文件的 SHA-256，生成独立请求。将 `prompts/` 中的请求交给被测会话，按需读取该次 `skill/` 快照；不要只调用全局技能，也不要把验收条件提前交给执行者。

真实输出、执行元数据及逐项评审填入本地运行目录后，执行：

```sh
python3 scripts/harness.py report --run work/runs/baseline
```

`pass` 表示该次输出通过全部已记录条件；不是检测作者是否为 AI，也不是质量保证。没有执行或没有完成评审时会明确报告状态并返回非零。详细文件合同见 [harness](docs/harness.md)。

## 隐私与首次公开

个人经历原文、业务材料、账号、联系方式、本机路径和实验日志只放 `work/`。公开用例优先使用合成材料；脱敏后仍须检查组合信息能否识别个人。

上面已明确确认的维护者姓名与邮箱可以公开。隐私检查仅精确放行这组身份，不放行其他 QQ 邮箱、旧邮箱或个人机器路径。

```sh
python3 scripts/privacy.py
python3 scripts/privacy.py --staged
python3 scripts/privacy.py --history
```

三条命令分别检查工作树候选文件、Git 暂存区、所有本地 refs 可达历史，报告不回显命中原文。通用检测不覆盖所有个人信息；可在被忽略的 `work/private-patterns.txt` 中逐行加入精确禁传字符串，仍须人工审查。`.gitignore` 不能清除旧提交或已经跟踪的文件。

首次本地历史隐私清理按维护者授权进行，记录见[清理计划与验证](docs/plans/privacy-cleanup.md)。公开身份已确认；创建远程仓库及推送须有维护者明确授权。每次发布前仍须检查全部拟发布历史，日常开发不自动重写历史、创建远程仓库或推送。

仓库提供本地 Git hooks，可用 `git config --local core.hooksPath .githooks` 启用。提交前检查暂存区，推送前检查历史；hooks 是额外拦截，不替代发布审查，且不会随 clone 自动启用。

## 更新全局安装

通过工程检查、相关行为评测、隐私审查并提交改动后，维护者明确要求更新时执行：

```sh
python3 scripts/manage.py install
```

默认目标为 `$CODEX_HOME/skills/plainspoken`；未设置 CODEX_HOME 时使用 `~/.codex/skills/plainspoken`。首次由旧名迁移时，先把 `shuorenhua` 完整备份到技能扫描目录之外，再安装，避免两份技能同时触发。工具不自动迁移旧名。

安装要求工作区干净，只复制运行内容；本地 `.installation.json` 记录源 commit、路径和校验值。旧版移入扫描目录之外的 `skill-backups/plainspoken/`。安装失败时尝试恢复；主动回滚使用工具打印的备份路径：

```sh
python3 scripts/manage.py rollback BACKUP_PATH
```

安装和回滚支持 `--dest` 隔离演练。安装后检查实际调用路径及 `.installation.json`，不要直接改已安装副本。`manage.py` 只执行结构与提交状态检查，行为评测和审查需按开发流程先完成。

## 许可与资料来源

源自 MrGeDiao/shuorenhua 的通用技能材料，以及改编自 Kiterlin/anti-defensive-writing 的防御性表述规则，均保留 [MIT 许可](LICENSE) 与原作者署名。Peng Cheng 有权授权的新增和修改贡献也按 MIT 提供；Codex 协作说明用于记录开发过程。第三方材料的作者、出处、固定版本与许可范围见随技能分发的 [THIRD_PARTY_NOTICES.md](skills/plainspoken/THIRD_PARTY_NOTICES.md)。

修改根 `LICENSE` 后，显式同步并检查：

```sh
python3 scripts/manage.py sync-license
python3 scripts/manage.py check
```

技能内的 `LICENSE` 是纳入版本控制的普通文件副本。检查、评测准备和安装发现两份许可不一致时会失败，不会静默覆盖。

天文词库不适用 MIT，当前技能包不附词库数据或原始说明。使用者可查阅[官方查询站点](https://nadc.china-vo.org/astrodict/)及[官方获取页面与使用约定](https://nadc.china-vo.org/astrodict/article/download)，或按其条款使用已有本机资料；本项目不自动下载词库，也不将链接视为再分发授权。

三个旧提交及辅助引用、索引中的词库数据和原始说明已完成本地清理，提交映射与验证见[历史词库清理](docs/plans/dictionary-history-cleanup.md)。仓库外私有备份和被忽略的旧评测快照仍含原件，不作为公开附件。首次公开前仍须审查候选文件与全部拟发布历史；本次清理未推送或更新全局安装。
