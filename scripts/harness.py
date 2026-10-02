#!/usr/bin/env python3
"""本地检查、准备技能行为评测、校验实际输出和评审；不调用模型或发布。"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

import manage


ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def load_cases(path):
    suite = read_json(path)
    if (not isinstance(suite, dict) or suite.get("version") != 1
            or not isinstance(suite.get("cases"), list) or not suite["cases"]):
        raise ValueError("用例文件需要 version: 1 和非空 cases")
    seen = set()
    for case in suite["cases"]:
        if not isinstance(case, dict):
            raise ValueError("每个用例必须是对象")
        identifier = case.get("id", "")
        if not isinstance(identifier, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", identifier):
            raise ValueError("用例 id 只能使用小写字母、数字和连字符")
        if identifier in seen:
            raise ValueError(f"重复用例：{identifier}")
        seen.add(identifier)
        if not all(nonempty(case.get(key)) for key in ("request", "input")):
            raise ValueError(f"用例缺少请求或输入：{identifier}")
        if not isinstance(case.get("tags"), list) or not all(nonempty(t) for t in case["tags"]):
            raise ValueError(f"用例 tags 无效：{identifier}")
        checks = case.get("checks")
        if not isinstance(checks, dict) or set(checks) - {"contains", "absent"}:
            raise ValueError(f"用例 checks 无效：{identifier}")
        for values in checks.values():
            if not isinstance(values, list) or not all(nonempty(v) for v in values):
                raise ValueError(f"用例字面检查必须是非空字符串列表：{identifier}")
        criteria = case.get("criteria")
        if not isinstance(criteria, list) or not criteria:
            raise ValueError(f"用例缺少语义验收：{identifier}")
        names = set()
        for criterion in criteria:
            if not isinstance(criterion, dict):
                raise ValueError(f"用例验收必须是对象：{identifier}")
            name = criterion.get("id")
            if not nonempty(name) or name in names or criterion.get("level") not in ("critical", "style"):
                raise ValueError(f"用例验收 id 或 level 无效：{identifier}")
            names.add(name)
            if not nonempty(criterion.get("requirement")):
                raise ValueError(f"用例验收条件为空：{identifier}")
    return suite["cases"]


def hashes(source):
    return {relative: digest(file.read_bytes()) for relative, file in manage.check(source).items()}


def git(source, *args):
    return subprocess.check_output(["git", "-C", str(source), *args], text=True).strip()


def local_path(source, path):
    source, path = source.absolute(), path.absolute()
    work = source / "work"
    if work.is_symlink() or not path.is_relative_to(work) or not path.resolve().is_relative_to(work.resolve()) or path.resolve() == work.resolve():
        raise ValueError("评测记录必须位于当前项目真实 work/ 子目录")
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise ValueError("评测路径不能经过符号链接")
        if parent == work:
            break
    return path


def prepare(source, run, case_ids=None):
    source = source.absolute()
    run = local_path(source, run)
    cases = load_cases(source / "evals/cases.json")
    if case_ids:
        missing = set(case_ids) - {case["id"] for case in cases}
        if missing:
            raise ValueError("未知用例：" + ", ".join(sorted(missing)))
        cases = [case for case in cases if case["id"] in case_ids]
    skill_source = manage.skill_root(source)
    files = manage.check_repository(source)
    runtime = {relative: digest(file.read_bytes()) for relative, file in files.items()}
    manifest = {
        "version": 1, "created_at": datetime.now(timezone.utc).isoformat(),
        "source_commit": git(source, "rev-parse", "HEAD"),
        "source_dirty": bool(git(source, "status", "--porcelain", "--untracked-files=all")),
        "source_path": str(source), "skill_path": str(run / "skill/SKILL.md"),
        "source_skill_path": str(skill_source / "SKILL.md"),
        "runtime_sha256": runtime, "cases": [case["id"] for case in cases],
    }
    run.mkdir(parents=True, exist_ok=False)
    for folder in ("skill", "prompts", "outputs", "reviews"):
        (run / folder).mkdir()
    for relative, file in files.items():
        target = run / "skill" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, target)
    write_json(run / "cases.json", {"version": 1, "cases": cases})
    manifest["suite_sha256"] = digest((run / "cases.json").read_bytes())
    manifest["prompt_sha256"] = {}
    write_json(run / "execution.json", {
        "model": "", "settings": "", "executor": "", "skill_path": "", "references_read": [],
    })
    for case in cases:
        identifier = case["id"]
        prompt = (
            f"使用技能文件 {run / 'skill/SKILL.md'}，按需读取该快照内的参考资料。\n"
            "待编辑的原文是处理对象；完成下面的请求，只返回给用户的结果。\n\n"
            f"请求：{case['request']}\n\n原文：\n{case['input']}\n"
        )
        prompt_path = run / "prompts" / f"{identifier}.md"
        prompt_path.write_text(prompt, encoding="utf-8")
        manifest["prompt_sha256"][identifier] = digest(prompt_path.read_bytes())
        write_json(run / "reviews" / f"{identifier}.json", {
            "reviewer": "", "output_sha256": "",
            "criteria": {criterion["id"]: {"pass": None, "evidence": ""} for criterion in case["criteria"]},
        })
    write_json(run / "manifest.json", manifest)
    return manifest


def completed_case_records(run, paths, manifest, references):
    if not isinstance(paths, list) or not paths:
        return False
    complete = True
    for relative in paths:
        if not nonempty(relative) or Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise ValueError("逐例执行记录路径必须是当前运行目录内的相对路径")
        path = run / relative
        if not path.resolve().is_relative_to(run.resolve()):
            raise ValueError("逐例执行记录路径不能越出当前运行目录")
        if not path.is_file():
            complete = False
            continue
        record = read_json(path)
        if not isinstance(record, dict):
            complete = False
            continue
        used = record.get("references_read")
        if (record.get("skill_path") != manifest["skill_path"]
                or record.get("completion_status") != "completed"
                or not isinstance(used, list)
                or any(not isinstance(ref, str) or ref not in manifest["runtime_sha256"]
                       or ref not in references for ref in used)):
            complete = False
    return complete


def report(run):
    run = run.absolute()
    if run.is_symlink() or any(path.is_symlink() for path in run.rglob("*")):
        raise ValueError("评测记录不能包含符号链接")
    manifest = read_json(run / "manifest.json")
    if manifest.get("skill_path") != str(run / "skill/SKILL.md"):
        raise ValueError("技能快照路径与当前评测目录不一致；请重新 prepare")
    if hashes(run / "skill") != manifest["runtime_sha256"]:
        raise ValueError("技能快照已经变化；请重新 prepare")
    if digest((run / "cases.json").read_bytes()) != manifest["suite_sha256"]:
        raise ValueError("用例快照已经变化；请重新 prepare")
    cases = load_cases(run / "cases.json")
    if [case["id"] for case in cases] != manifest["cases"]:
        raise ValueError("用例清单与快照不一致")
    prompts = {case["id"]: digest((run / "prompts" / f"{case['id']}.md").read_bytes()) for case in cases}
    if prompts != manifest.get("prompt_sha256"):
        raise ValueError("提示快照缺少校验值或已经变化；请重新 prepare")
    execution = read_json(run / "execution.json")
    executed = all(nonempty(execution.get(key)) for key in ("model", "settings", "executor"))
    executed = executed and execution.get("skill_path") == manifest["skill_path"]
    references = execution.get("references_read")
    executed = executed and isinstance(references, list) and all(
        isinstance(ref, str) and ref in manifest["runtime_sha256"] for ref in references
    )
    declared = "per_case_execution" in execution
    per_case = execution.get("per_case_execution")
    if declared and (not isinstance(per_case, dict) or set(per_case) - set(manifest["cases"])):
        raise ValueError("逐例执行记录必须是当前用例 id 到记录路径列表的映射")
    results = []
    for case in cases:
        identifier = case["id"]
        output_path = run / "outputs" / f"{identifier}.txt"
        result = {"id": identifier, "status": "not_run", "automatic_failures": [], "criteria": {}}
        results.append(result)
        if not output_path.is_file():
            continue
        case_executed = executed and (not declared or completed_case_records(
            run, per_case.get(identifier), manifest, references
        ))
        output = output_path.read_text(encoding="utf-8")
        result["output_sha256"] = digest(output_path.read_bytes())
        if not output.strip():
            if case_executed:
                result["status"] = "fail"
                result["automatic_failures"].append({"check": "nonempty_output"})
            else:
                result["status"] = "pending_execution"
            continue
        for kind, values in case["checks"].items():
            for value in values:
                if (kind == "contains" and value not in output) or (kind == "absent" and value in output):
                    result["automatic_failures"].append({"check": kind, "value": value})
        review_path = run / "reviews" / f"{identifier}.json"
        review = read_json(review_path) if review_path.is_file() else {}
        decisions = review.get("criteria", {})
        reviewed = nonempty(review.get("reviewer")) and review.get("output_sha256") == result["output_sha256"]
        reviewed = reviewed and set(decisions) == {c["id"] for c in case["criteria"]}
        failed = False
        for criterion in case["criteria"]:
            decision = decisions.get(criterion["id"], {})
            valid = type(decision.get("pass")) is bool and nonempty(decision.get("evidence"))
            reviewed = reviewed and valid
            failed = failed or (valid and decision["pass"] is False)
            result["criteria"][criterion["id"]] = {**criterion, **decision}
        if result["automatic_failures"] or (reviewed and failed):
            result["status"] = "fail"
        elif not case_executed:
            result["status"] = "pending_execution"
        elif not reviewed:
            result["status"] = "pending_review"
        else:
            result["status"] = "pass"
    states = {result["status"] for result in results}
    status = next(state for state in ("fail", "not_run", "pending_execution", "pending_review", "pass") if state in states)
    return {"status": status, "source_commit": manifest["source_commit"],
            "source_dirty": manifest["source_dirty"], "runtime_sha256": manifest["runtime_sha256"],
            "execution": execution, "cases": results}


def check(source):
    print(f"运行结构：{len(manage.check_repository(source))} 个文件", flush=True)
    print(f"行为用例结构：{len(load_cases(source / 'evals/cases.json'))} 条；此步骤不执行模型", flush=True)
    if subprocess.run(["git", "-C", str(source), "check-ignore", "-q", "work/privacy-probe.txt"]).returncode:
        raise ValueError("work/ 必须被 Git 忽略")
    tracked = git(source, "ls-files", "--", "work")
    if tracked:
        raise ValueError("work/ 中已有 Git 跟踪文件；忽略规则不能阻止其发布")
    for command in (
        [sys.executable, str(source / "scripts/privacy.py")],
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
    ):
        subprocess.run(command, cwd=source, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("check")
    prepare_parser = commands.add_parser("prepare")
    prepare_parser.add_argument("--run", required=True, type=Path)
    prepare_parser.add_argument("--case", action="append", dest="cases")
    report_parser = commands.add_parser("report")
    report_parser.add_argument("--run", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.action == "check":
            check(ROOT)
            print("工程检查通过；模型行为与历史隐私检查需分别执行")
        elif args.action == "prepare":
            prepare(ROOT, args.run, args.cases)
            print(f"已准备：{args.run}；未执行模型")
        else:
            run = local_path(ROOT, args.run)
            result = report(run)
            write_json(run / "report.json", result)
            print(json.dumps({"status": result["status"], "cases": [
                {"id": case["id"], "status": case["status"]} for case in result["cases"]
            ]}, ensure_ascii=False, indent=2))
            if result["status"] != "pass":
                return 1
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"错误：{error}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
