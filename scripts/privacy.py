#!/usr/bin/env python3
"""本地隐私门禁：默认扫描 Git 候选工作树；--staged 仅索引；--history 仅全部 refs 可达历史。

输出 JSON，仅含定位与规则名；退出 0 表示所选范围未命中，1 表示命中或无法检查。
忽略文件不属于工作树候选；历史不包括 reflog、悬空对象或未获取的远端内容。
work/private-patterns.txt 可逐行提供精确禁传字符串，必须被 Git 忽略且未跟踪。
通用规则无法识别所有个人信息；缺少本地字符串时，coverage 为 generic_only。
"""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess


ROOT = Path(__file__).resolve().parents[1]
LICENSED_PATHS = (
    "references/astrodict/astrodict241020_ec.txt",  # Retained for old index entries and history.
    "skills/plainspoken/references/astrodict/astrodict241020_ec.txt",
)
LICENSED_SHA256 = "7e2ef2b022961b3b5a7b84028b105366950bb33b05795420cbb4d2af91705699"
LOCAL_PATTERNS = "work/private-patterns.txt"
EMAIL = re.compile(r"[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@(?:[A-Z0-9-]+\.)+[A-Z]{2,}", re.I)
USER_PATH = re.compile(r"(?:/(?:Users|home)/|[A-Z]:[\\/]+Users[\\/]+)([A-Z0-9_.-]+)", re.I)
TOKEN = re.compile(
    r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}"
    r"|sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}|(?:AKIA|ASIA)[A-Z0-9]{16}"
    r"|xox[baprs]-[A-Za-z0-9-]{10,})\b"
)
KEY = re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----")
ASSIGNMENT = re.compile(
    r"(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)\s*[:=]\s*['\"]?"
    r"([A-Za-z0-9_./+=-]{16,})", re.I
)
SAFE_DOMAINS = {"example.invalid", "example.com", "users.noreply.github.com"}
SAFE_NAMES = {"test", "test user", "fixture", "example", "anonymous", "plainspoken", "github", "codex"}
PUBLIC_NAME, PUBLIC_EMAIL = "Peng Cheng", "chengpengsmc@qq.com"
PUBLIC_TEXT = re.compile(
    r"(?<![\w.!#$%&'*+/=?^`{|}~@\\-])(?:"
    + "|".join(re.escape(value) for value in (f"{PUBLIC_NAME} <{PUBLIC_EMAIL}>", PUBLIC_NAME, PUBLIC_EMAIL))
    + r")(?![\w.!#$%&'*+/=?^`{|}~@\\-])"
)


def content_rules(text, patterns):
    rules = set()
    public_spans = [match.span() for match in PUBLIC_TEXT.finditer(text)]

    def is_public(start, end):
        return any(left <= start and end <= right for left, right in public_spans)

    if any(match.group(1).lower() not in {"user", "username", "example"} for match in USER_PATH.finditer(text)):
        rules.add("user-path")
    if any(match[0].rsplit("@", 1)[1].lower() not in SAFE_DOMAINS and match[0].lower() != "noreply@github.com"
           and not (match[0] == PUBLIC_EMAIL and is_public(*match.span()))
           for match in EMAIL.finditer(text)):
        rules.add("email")
    if TOKEN.search(text) or ASSIGNMENT.search(text):
        rules.add("token")
    if KEY.search(text):
        rules.add("private-key")
    for pattern in patterns:
        offset = text.find(pattern)
        while offset >= 0:
            if not is_public(offset, offset + len(pattern)):
                rules.add("local-private-pattern")
                break
            offset = text.find(pattern, offset + 1)
    return rules


def private_path(path):
    parts = PurePosixPath(path).parts
    return any(part in {"work", ".ssh", ".aws", ".secrets", ".git", ".installation.json", "id_rsa", "id_ed25519"}
               or (part.startswith(".env") and part != ".env.example") for part in parts)


def git(root, *args):
    return subprocess.check_output(["git", "--no-replace-objects", "-C", str(root), *args], stderr=subprocess.DEVNULL)


def has_symlink(root, path):
    current = root
    for part in PurePosixPath(path).parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def scan(root, scope="worktree"):
    if scope not in {"worktree", "staged", "history"}:
        raise ValueError("unknown scope")
    root = Path(root)
    report = {"scope": scope, "checked": 0, "findings": [], "coverage": "generic_only",
              "notice": "通用规则不能识别全部个人信息；本地禁传字符串未启用。"}
    patterns = []
    findings = set()

    def add(location, rule):
        if content_rules(location, patterns):
            location = "redacted-path:" + hashlib.sha256(location.encode("utf-8", "surrogateescape")).hexdigest()[:12]
        findings.add((location, rule))

    def inspect(path, data, location):
        report["checked"] += 1
        for rule in content_rules(path, patterns):
            add(location, rule)
        if private_path(path):
            add(location, "private-path")
        if path in LICENSED_PATHS:
            if hashlib.sha256(data).hexdigest() == LICENSED_SHA256:
                return
            add(location, "licensed-data-changed")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            add(location, "binary")
            return
        if any(ord(char) < 32 and char not in "\n\r\t" for char in text):
            add(location, "binary")
            return
        for rule in content_rules(text, patterns):
            add(location, rule)

    def entry(path, mode, data, location):
        if mode == "120000":
            add(location, "symlink")
        elif mode not in {"100644", "100755"}:
            add(location, "unsupported-entry")
        else:
            inspect(path, data(), location)

    def metadata(oid, kind):
        data = git(root, "cat-file", kind, oid)
        report["checked"] += 1
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            add(f"{kind}:{oid}", "binary")
            return
        headers, _, message = text.partition("\n\n")
        for line in headers.splitlines():
            field, _, value = line.partition(" ")
            if field in {"author", "committer", "tagger"}:
                location = f"{kind}:{oid}:{field}"
                identity = re.fullmatch(r"(.+) <([^<>]+)> -?\d+ [+-]\d{4}", value)
                name, email = identity.group(1, 2) if identity else ("", "")
                if (name, email) != (PUBLIC_NAME, PUBLIC_EMAIL) and (name.lower() not in SAFE_NAMES or email == PUBLIC_EMAIL):
                    add(location, "identity")
                for rule in content_rules(value, patterns):
                    add(location, rule)
            elif field not in {"tree", "parent", "object", "type"}:
                for rule in content_rules(value, patterns):
                    add(f"{kind}:{oid}:metadata", rule)
        for rule in content_rules(message, patterns):
            add(f"{kind}:{oid}:message", rule)

    try:
        # A shared local list applies to every scan, but must never become a publication candidate.
        local = root / LOCAL_PATTERNS
        if has_symlink(root, LOCAL_PATTERNS):
            add(LOCAL_PATTERNS, "symlink")
        elif local.exists():
            tracked = git(root, "ls-files", "--", LOCAL_PATTERNS).strip()
            ignored = subprocess.run(["git", "-C", str(root), "check-ignore", "-q", LOCAL_PATTERNS],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
            if tracked or not ignored:
                add(LOCAL_PATTERNS, "local-patterns-not-private")
            else:
                try:
                    patterns = [line for line in local.read_text(encoding="utf-8").splitlines() if line]
                    if patterns:
                        report["coverage"] = "generic_and_local"
                        report["notice"] = "已启用通用规则与本地精确禁传字符串；仍需人工隐私审查。"
                except (OSError, UnicodeError):
                    add(LOCAL_PATTERNS, "unreadable-local-patterns")

        if scope == "worktree":
            paths = git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
            for raw in sorted(set(paths.split(b"\0")) - {b""}):
                path = raw.decode("utf-8", "surrogateescape")
                location = f"worktree:{path}"
                target = root / path
                if has_symlink(root, path):
                    add(location, "symlink")
                elif target.exists():
                    if not stat.S_ISREG(target.stat().st_mode):
                        add(location, "unsupported-entry")
                    else:
                        inspect(path, target.read_bytes(), location)
        elif scope == "staged":
            for item in git(root, "ls-files", "--stage", "-z").split(b"\0"):
                if not item:
                    continue
                header, raw = item.split(b"\t", 1)
                mode, oid, stage = header.decode("ascii").split()
                path = raw.decode("utf-8", "surrogateescape")
                location = f"index:{path}"
                if stage != "0":
                    add(location, "unmerged-index")
                entry(path, mode, lambda: git(root, "cat-file", "blob", oid), location)
        else:
            objects = git(root, "rev-list", "--objects", "--all", "--no-object-names").decode("ascii").splitlines()
            refs = git(root, "for-each-ref", "--format=%(objectname) %(refname)").decode("utf-8", "surrogateescape").splitlines()
            ref_roots = set()
            for ref in refs:
                oid, name = ref.split(" ", 1)
                report["checked"] += 1
                for rule in content_rules(name, patterns):
                    add(f"ref:{name}", rule)
                ref_roots.add(git(root, "rev-parse", oid + "^{}").decode("ascii").strip())
            seen_entries, seen_blobs, blobs = set(), set(), []
            for oid in objects:
                kind = git(root, "cat-file", "-t", oid).decode("ascii").strip()
                if kind in {"commit", "tag"}:
                    metadata(oid, kind)
                if kind == "commit" or (kind == "tree" and oid in ref_roots):
                    for item in git(root, "ls-tree", "-r", "-z", oid).split(b"\0"):
                        if not item:
                            continue
                        header, raw = item.split(b"\t", 1)
                        mode, object_kind, blob = header.decode("ascii").split()
                        path = raw.decode("utf-8", "surrogateescape")
                        key = (mode, blob, path)
                        if key in seen_entries:
                            continue
                        seen_entries.add(key)
                        if object_kind == "blob":
                            seen_blobs.add(blob)
                        entry(path, mode, lambda: git(root, "cat-file", "blob", blob), f"{kind}:{oid}:{path}")
                elif kind == "blob":
                    blobs.append(oid)
            for oid in blobs:
                if oid not in seen_blobs:
                    inspect("", git(root, "cat-file", "blob", oid), f"blob:{oid}")
    except (OSError, UnicodeError, ValueError, subprocess.CalledProcessError):
        add("repository", "scan-error")
    report["findings"] = [{"location": location, "rule": rule} for location, rule in sorted(findings)]
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--history", action="store_true")
    group.add_argument("--staged", action="store_true")
    args = parser.parse_args()
    report = scan(ROOT, "history" if args.history else "staged" if args.staged else "worktree")
    print(json.dumps(report, ensure_ascii=True, indent=2))
    raise SystemExit(1 if report["findings"] else 0)


if __name__ == "__main__":
    main()
