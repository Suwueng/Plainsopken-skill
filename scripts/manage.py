#!/usr/bin/env python3
"""检查、安装或回滚本项目的运行文件；不执行模型评测。"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ("SKILL.md", "LICENSE", "agents", "references")
RECORD = ".installation.json"


def runtime_files(source):
    files = []
    for name in RUNTIME:
        path = source / name
        if not path.exists():
            raise ValueError(f"缺少运行内容：{path}")
        entries = [path, *path.rglob("*")] if path.is_dir() else [path]
        for entry in entries:
            if entry.is_symlink():
                raise ValueError(f"运行内容不接受符号链接：{entry}")
            if entry.is_file():
                files.append(entry)
    return sorted(files)


def check(source):
    files = runtime_files(source)
    text = (source / "SKILL.md").read_text()
    header = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
    if not header or not re.search(r"^name: plainspoken\s*$", header[1], re.M):
        raise ValueError("SKILL.md 缺少有效的 plainspoken 名称")
    if not re.search(r"^description: \S.*$", header[1], re.M):
        raise ValueError("SKILL.md 缺少 description")
    for file in files:
        if file.suffix != ".md":
            continue
        for link in re.findall(r"\]\(([^\s)]+)\)", file.read_text()):
            url = urlsplit(link.strip("<>"))
            if url.scheme or url.netloc or not url.path:
                continue
            target = (file.parent / unquote(url.path)).resolve()
            if not target.is_relative_to(source.resolve()) or not target.exists():
                raise ValueError(f"无效本地链接：{file.relative_to(source)} -> {link}")
    return files


def install(source, destination, commit=None):
    files = check(source)
    if destination.is_symlink():
        raise ValueError("目标是符号链接，请先人工处理，避免覆盖开发源")
    src, dst = source.resolve(), destination.resolve()
    if src.is_relative_to(dst) or dst.is_relative_to(src):
        raise ValueError("安装源和目标不能重叠")
    if destination.exists() and not destination.is_dir():
        raise ValueError("安装目标必须是目录")
    backup_root = destination.parent.parent / "skill-backups" / destination.name
    backup_root.mkdir(parents=True, exist_ok=True)
    destination.parent.mkdir(parents=True, exist_ok=True)
    backup = None
    with tempfile.TemporaryDirectory(prefix=".stage-", dir=backup_root) as temporary:
        stage = Path(temporary) / "package"
        stage.mkdir()
        for file in files:
            target = stage / file.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, target)
        if (source / RECORD).is_file() and commit is None:
            shutil.copy2(source / RECORD, stage / RECORD)
        else:
            record = {
                "source_commit": commit,
                "source_path": str(src),
                "installed_at": datetime.now(timezone.utc).isoformat(),
                "sha256": {str(f.relative_to(source)): hashlib.sha256(f.read_bytes()).hexdigest() for f in files},
            }
            (stage / RECORD).write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
        check(stage)
        if destination.exists():
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
            backup = backup_root / stamp
            destination.rename(backup)
        try:
            stage.rename(destination)
        except OSError:
            if backup is not None:
                backup.rename(destination)
            raise
    return backup


def committed_source(source):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(source), *args], text=True).strip()
    if git("status", "--porcelain", "--untracked-files=all"):
        raise ValueError("工作区有未提交改动，请先完成验证并提交，再安装")
    tracked = set(git("ls-files", "-z", "--", *RUNTIME).split("\0")) - {""}
    if tracked != {str(f.relative_to(source)) for f in runtime_files(source)}:
        raise ValueError("运行目录存在未纳入 Git 的文件，请清理后再安装")
    return git("rev-parse", "HEAD")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "install", "rollback"))
    parser.add_argument("backup", nargs="?", type=Path)
    codex_root = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    parser.add_argument("--dest", type=Path, default=codex_root / "skills" / "plainspoken")
    args = parser.parse_args()
    if (args.action == "rollback") != (args.backup is not None):
        parser.error("只有 rollback 需要且必须提供备份路径")
    try:
        if args.action == "check":
            print(f"静态检查通过：{len(check(ROOT))} 个运行文件；未执行模型评测")
            return
        source = args.backup.expanduser().absolute() if args.backup else ROOT
        commit = committed_source(ROOT) if args.action == "install" else None
        destination = args.dest.expanduser().absolute()
        backup = install(source, destination, commit)
        print(f"已安装：{destination}")
        if backup:
            print(f"旧版备份：{backup}")
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"错误：{error}\n")


if __name__ == "__main__":
    main()
