# 说人话：个人维护版

中文与英文文本的改写和审阅技能，清理模板表达，同时保留事实、术语、范围与责任主体。

本项目从当前本地安装版独立初始化，保留个人修正和天文术语资料。它不是上游仓库的 fork；上游更新由维护者审阅后选择性移植。来源和基线见 [UPSTREAM.md](UPSTREAM.md)。

## 目录

- `SKILL.md`、`references/`、`agents/`、`LICENSE`：技能运行内容。
- `evals/cases.md`：初始行为用例及验收条件。
- `scripts/manage.py`：静态检查、安装和回滚，仅依赖 Python 3 标准库。
- `tests/`：同步工具的隔离测试，不修改真实全局安装。
- `work/`：本地实验输入、输出和临时记录，Git 忽略。

## 开发与验证

在本项目目录执行：

```sh
python3 scripts/manage.py check
python3 -m unittest discover -s tests -v
```

`check` 检查运行文件、必要元数据和本地文件链接；它不是完整 YAML 校验，也不判断改写质量。修改技能元数据时，可额外用当前 Codex 的 skill-creator 校验器验证。

每次规则修改先从真实问题提炼一个用例：保留输入，写清必须保留的信息、允许的修改范围和不允许的结果，然后对比改动前后输出。初始用例见 [evals/cases.md](evals/cases.md)。

测试会话应明确读取这个工作目录下的 `SKILL.md` 及相关参考文件，并核对实际读取路径。根目录技能源码没有注册为第二份全局技能，不能只说 `$shuorenhua` 就假定测试的是开发版。

用例输出和评审记录放在 `work/`，记录技能 commit、模型、日期、原始输入及实际输出。评审先检查事实和范围，再评价风格；不要求和一份推荐稿逐字一致。评审用的预期条件不要提前提供给被测模型。

## 更新全局安装

先完成静态检查、相关行为用例和工具测试，再提交改动。确认需要切换日常使用版本时执行：

```sh
python3 scripts/manage.py install
```

默认安装到 `$CODEX_HOME/skills/shuorenhua`；未设置 CODEX_HOME 时使用当前用户的 `.codex/skills/shuorenhua`。

安装要求 Git 工作区干净，导出上述运行内容并写入 `.installation.json`，记录源 commit 和文件校验值。旧安装移动到技能目录之外的 `skill-backups/shuorenhua/`，命令会打印完整备份路径。安装不依赖 GitHub，也不会读取或修改上游仓库。

失败时工具尝试恢复旧目录。需要主动回滚时，把以下 BACKUP_PATH 替换为安装时打印的完整路径：

```sh
python3 scripts/manage.py rollback BACKUP_PATH
```

回滚也会备份被替换的版本。备份不会自动删除。`install` 和 `rollback` 支持 `--dest` 指定隔离目标，用于演练。不要直接修改已安装副本；下次同步会整体替换它。

Codex 通常自动发现技能变化；若界面没有显示更新，重新启动后再检查。安装完成后应在业务项目中做一次实际调用，核对读取路径及 `.installation.json` 里的 commit。

## GitHub 与上游

当前只初始化本地 Git，尚未配置远程仓库。以后创建独立 GitHub 仓库并设置为 `origin` 即可；如主要服务于个人工作，可以使用私有仓库。上游地址记录在 UPSTREAM.md 中，没有配置可自动合并的 upstream remote。

查看上游更新时，将有用改动作为本项目的一次普通修改：记录上游 commit/PR、移植理由，补充或复用验收用例，通过后提交。详见 [UPSTREAM.md](UPSTREAM.md)。

## 许可与资料来源

源自 MrGeDiao/shuorenhua 的通用技能材料保留 [MIT 许可](LICENSE)。本项目原创的维护代码与文档亦按 MIT 许可提供。

`references/astrodict/` 是独立第三方资料，适用目录中的 [原始使用约定](references/astrodict/readme.txt)，不适用 MIT。本次本地迁移保持原文件不变；公开分发前按该约定处理，不能把它和其他词库混合后重新发布或声明为可任意商用。
