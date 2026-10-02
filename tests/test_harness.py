import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("harness", SCRIPTS / "harness.py")
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.skill = self.root / "skills/plainspoken"
        for directory in ("skills/plainspoken/agents", "skills/plainspoken/references", "evals", "work"):
            (self.root / directory).mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("---\nname: plainspoken\ndescription: Test skill\n---\n")
        (self.root / "LICENSE").write_text("Test license")
        (self.skill / "LICENSE").write_text("Test license")
        (self.skill / "THIRD_PARTY_NOTICES.md").write_text("External sources keep their terms")
        (self.skill / "agents/openai.yaml").write_text("interface: {}\n")
        (self.skill / "references/guide.md").write_text("Keep facts")
        (self.root / ".gitignore").write_text("/work/\n")
        self.case = {
            "id": "facts", "tags": ["status"], "request": "Rewrite naturally.",
            "input": "Latency is 10 ms for beta users only.",
            "checks": {"contains": ["10 ms"], "absent": ["all users"]},
            "criteria": [{"id": "scope", "level": "critical", "requirement": "Keep beta scope"}],
        }
        (self.root / "evals/cases.json").write_text(json.dumps({"version": 1, "cases": [self.case]}))
        for args in (("init", "-b", "main"), ("add", "."),
                     ("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-m", "Fixture")):
            subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)
        self.run = self.root / "work/runs/test"

    def prepare(self):
        harness.prepare(self.root, self.run)

    def complete(self, output="Latency is 10 ms for beta users only."):
        (self.run / "outputs/facts.txt").write_text(output)
        execution = {
            "model": "test-model", "settings": "test settings", "executor": "fixture",
            "skill_path": str(self.run / "skill/SKILL.md"),
            "references_read": ["references/guide.md"],
        }
        (self.run / "execution.json").write_text(json.dumps(execution))
        review = {
            "reviewer": "test reviewer", "output_sha256": harness.digest(output.encode()),
            "criteria": {"scope": {"pass": True, "evidence": "Output keeps beta users only."}},
        }
        (self.run / "reviews/facts.json").write_text(json.dumps(review))

    def declare_case_execution(self):
        path = self.run / "execution.json"
        execution = json.loads(path.read_text())
        execution["per_case_execution"] = {"facts": ["per-case/facts.json"]}
        path.write_text(json.dumps(execution))
        record_path = self.run / "per-case/facts.json"
        record_path.parent.mkdir()
        record_path.write_text(json.dumps({
            "skill_path": execution["skill_path"], "references_read": execution["references_read"],
            "completion_status": "completed", "model": "exact model unknown",
        }))
        return record_path

    def test_prepare_pins_dirty_runtime_and_hides_rubric_from_prompt(self):
        (self.skill / "references/guide.md").write_text("Changed local rules")
        (self.root / "SKILL.md").write_text("Stale root entry must not be used")
        self.prepare()
        manifest = json.loads((self.run / "manifest.json").read_text())
        self.assertTrue(manifest["source_dirty"])
        self.assertEqual(manifest["source_path"], str(self.root))
        self.assertEqual(manifest["source_skill_path"], str(self.skill / "SKILL.md"))
        self.assertEqual((self.run / "skill/SKILL.md").read_bytes(), (self.skill / "SKILL.md").read_bytes())
        self.assertEqual((self.run / "skill/LICENSE").read_bytes(), (self.root / "LICENSE").read_bytes())
        self.assertTrue((self.run / "skill/THIRD_PARTY_NOTICES.md").is_file())
        self.assertFalse((self.run / "skill/evals").exists())
        self.assertEqual((self.run / "skill/references/guide.md").read_text(), "Changed local rules")
        prompt = (self.run / "prompts/facts.md").read_text()
        self.assertIn(str(self.run / "skill/SKILL.md"), prompt)
        self.assertNotIn("Keep beta scope", prompt)
        self.assertNotIn("criteria", prompt)
        self.assertEqual(harness.report(self.run)["status"], "not_run")

    def test_only_reviewed_actual_output_can_pass(self):
        self.prepare()
        self.complete()
        self.assertEqual(harness.report(self.run)["status"], "pass")
        (self.run / "reviews/facts.json").unlink()
        self.assertEqual(harness.report(self.run)["status"], "pending_review")

    def test_executed_blank_output_fails_even_with_positive_review(self):
        self.case["checks"] = {}
        (self.root / "evals/cases.json").write_text(json.dumps({"version": 1, "cases": [self.case]}))
        self.prepare()
        for output in ("", " \n\t"):
            with self.subTest(output=repr(output)):
                self.complete(output)
                result = harness.report(self.run)
                self.assertEqual(result["status"], "fail")
                case = result["cases"][0]
                self.assertEqual(case["status"], "fail")
                self.assertEqual(case["output_sha256"], harness.digest(output.encode()))
                self.assertEqual(case["automatic_failures"], [{"check": "nonempty_output"}])
                self.assertEqual((self.run / "outputs/facts.txt").read_text(), output)

    def test_blank_file_without_valid_execution_is_pending(self):
        self.prepare()
        (self.run / "outputs/facts.txt").write_text("")
        self.assertEqual(harness.report(self.run)["status"], "pending_execution")
        self.complete("")
        path = self.run / "execution.json"
        execution = json.loads(path.read_text())
        execution["skill_path"] = str(self.skill / "SKILL.md")
        path.write_text(json.dumps(execution))
        self.assertEqual(harness.report(self.run)["status"], "pending_execution")

    def test_missing_output_stays_not_run_despite_run_execution_metadata(self):
        self.prepare()
        self.complete()
        (self.run / "outputs/facts.txt").unlink()
        self.assertEqual(harness.report(self.run)["status"], "not_run")

    def test_review_cannot_hide_lost_literal_or_new_claim(self):
        self.prepare()
        self.complete("Latency is fast for all users.")
        result = harness.report(self.run)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(len(result["cases"][0]["automatic_failures"]), 2)

    def test_modified_output_invalidates_old_review(self):
        self.prepare()
        self.complete()
        (self.run / "outputs/facts.txt").write_text("Latency is 10 ms.")
        self.assertEqual(harness.report(self.run)["status"], "pending_review")

    def test_changed_skill_or_suite_rejects_report(self):
        self.prepare()
        (self.run / "skill/references/guide.md").write_text("Tampered rules")
        with self.assertRaisesRegex(ValueError, "快照"):
            harness.report(self.run)

    def test_execution_must_identify_the_pinned_skill(self):
        self.prepare()
        self.complete()
        execution = json.loads((self.run / "execution.json").read_text())
        execution["skill_path"] = str(self.skill / "SKILL.md")
        (self.run / "execution.json").write_text(json.dumps(execution))
        self.assertEqual(harness.report(self.run)["status"], "pending_execution")

    def test_complete_declared_records_can_pass_including_multiple_rounds(self):
        self.prepare()
        self.complete()
        record_path = self.declare_case_execution()
        self.assertEqual(harness.report(self.run)["status"], "pass")
        second = record_path.with_name("second.json")
        second.write_bytes(record_path.read_bytes())
        path = self.run / "execution.json"
        execution = json.loads(path.read_text())
        execution["per_case_execution"]["facts"].append("per-case/second.json")
        path.write_text(json.dumps(execution))
        self.assertEqual(harness.report(self.run)["status"], "pass")
        record = json.loads(second.read_text())
        record["completion_status"] = "failed"
        second.write_text(json.dumps(record))
        self.assertEqual(harness.report(self.run)["status"], "pending_execution")

    def test_missing_failed_or_wrong_skill_record_cannot_pass(self):
        self.prepare()
        self.complete()
        path = self.declare_case_execution()
        original = json.loads(path.read_text())
        for record in (None, {**original, "completion_status": "failed"},
                       {**original, "skill_path": str(self.skill / "SKILL.md")}):
            with self.subTest(record=record):
                if record is None:
                    path.unlink()
                else:
                    path.write_text(json.dumps(record))
                self.assertEqual(harness.report(self.run)["status"], "pending_execution")

    def test_declared_mapping_requires_known_cases_and_case_coverage(self):
        self.prepare()
        self.complete()
        self.declare_case_execution()
        path = self.run / "execution.json"
        execution = json.loads(path.read_text())
        for mapping in ({}, {"facts": []}):
            with self.subTest(mapping=mapping):
                path.write_text(json.dumps({**execution, "per_case_execution": mapping}))
                self.assertEqual(harness.report(self.run)["status"], "pending_execution")
        for mapping in (None, [], {"unknown": ["per-case/facts.json"]}):
            with self.subTest(mapping=mapping):
                path.write_text(json.dumps({**execution, "per_case_execution": mapping}))
                with self.assertRaisesRegex(ValueError, "逐例"):
                    harness.report(self.run)

    def test_declared_record_paths_cannot_escape_the_run(self):
        self.prepare()
        self.complete()
        record_path = self.declare_case_execution()
        outside = self.run.parent / "outside.json"
        outside.write_bytes(record_path.read_bytes())
        path = self.run / "execution.json"
        execution = json.loads(path.read_text())
        for relative in ("../outside.json", str(outside), 1):
            with self.subTest(path=relative):
                execution["per_case_execution"]["facts"] = [relative]
                path.write_text(json.dumps(execution))
                with self.assertRaisesRegex(ValueError, "逐例.*路径"):
                    harness.report(self.run)

    def test_declared_references_must_belong_to_snapshot_and_run_record(self):
        self.prepare()
        self.complete()
        path = self.declare_case_execution()
        record = json.loads(path.read_text())
        for references in (None, ["references/missing.md"]):
            with self.subTest(references=references):
                path.write_text(json.dumps({**record, "references_read": references}))
                self.assertEqual(harness.report(self.run)["status"], "pending_execution")
        path.write_text(json.dumps(record))
        run_record = self.run / "execution.json"
        execution = json.loads(run_record.read_text())
        execution["references_read"] = []
        run_record.write_text(json.dumps(execution))
        self.assertEqual(harness.report(self.run)["status"], "pending_execution")

    def test_nonobject_declared_record_cannot_pass(self):
        self.prepare()
        self.complete()
        path = self.declare_case_execution()
        for record in (None, [], "completed"):
            with self.subTest(record=record):
                path.write_text(json.dumps(record))
                self.assertEqual(harness.report(self.run)["status"], "pending_execution")

    def test_blank_output_with_failed_case_record_is_pending(self):
        self.prepare()
        self.complete("")
        path = self.declare_case_execution()
        record = json.loads(path.read_text())
        record["completion_status"] = "failed"
        path.write_text(json.dumps(record))
        self.assertEqual(harness.report(self.run)["status"], "pending_execution")

    def test_existing_snapshot_report_does_not_depend_on_source_layout(self):
        self.prepare()
        self.complete()
        path = self.run / "manifest.json"
        manifest = json.loads(path.read_text())
        manifest.pop("source_skill_path", None)
        path.write_text(json.dumps(manifest))
        shutil.rmtree(self.root / "skills")
        (self.root / "LICENSE").unlink()
        self.assertEqual(harness.report(self.run)["status"], "pass")

    def test_license_drift_blocks_prepare_without_rewriting_source(self):
        (self.skill / "LICENSE").write_text("Stale license")
        with self.assertRaisesRegex(ValueError, "许可.*同步"):
            self.prepare()
        self.assertEqual((self.skill / "LICENSE").read_text(), "Stale license")
        self.assertFalse(self.run.exists())

    def test_prepare_rejects_symlinked_skill_parent(self):
        outside = self.root / "external-skills"
        (self.root / "skills").rename(outside)
        (self.root / "skills").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "符号链接"):
            self.prepare()
        self.assertFalse(self.run.exists())

    def test_modified_prompt_or_missing_prompt_hash_rejects_report(self):
        self.prepare()
        self.complete()
        prompt = self.run / "prompts/facts.md"
        original = prompt.read_text()
        prompt.write_text("Answer a different request without using the skill.")
        with self.assertRaisesRegex(ValueError, "提示"):
            harness.report(self.run)
        prompt.write_text(original)
        path = self.run / "manifest.json"
        manifest = json.loads(path.read_text())
        manifest.pop("prompt_sha256", None)
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "提示"):
            harness.report(self.run)

    def test_copied_run_cannot_claim_the_old_skill_path(self):
        self.prepare()
        self.complete()
        copied = self.root / "work/runs/copied"
        shutil.copytree(self.run, copied)
        with self.assertRaisesRegex(ValueError, "路径"):
            harness.report(copied)

    def test_report_rejects_symlinked_records_before_reading_or_writing(self):
        self.prepare()
        self.complete()
        outside = self.root / "public-report.json"
        outside.write_text("Must remain unchanged")
        for relative in ("manifest.json", "execution.json", "cases.json", "skill",
                         "prompts/facts.md", "outputs/facts.txt", "reviews/facts.json", "report.json"):
            with self.subTest(path=relative):
                path = self.run / relative
                backup = path.with_name(path.name + ".original")
                existed = path.exists()
                if existed:
                    path.rename(backup)
                path.symlink_to(outside)
                try:
                    with self.assertRaisesRegex(ValueError, "符号链接"):
                        result = harness.report(self.run)
                        harness.write_json(self.run / "report.json", result)
                    self.assertEqual(outside.read_text(), "Must remain unchanged")
                finally:
                    path.unlink()
                    if existed:
                        backup.rename(path)

    def test_case_containers_require_the_documented_types(self):
        path = self.root / "evals/cases.json"
        invalid = [
            {"version": 1, "cases": "facts"},
            {"version": 1, "cases": {"facts": self.case}},
            {"version": 1, "cases": [None]},
            {"version": 1, "cases": ["facts"]},
            {"version": 1, "cases": [{**self.case, "criteria": [None]}]},
            {"version": 1, "cases": [{**self.case, "criteria": ["scope"]}]},
        ]
        for payload in invalid:
            with self.subTest(payload=payload):
                path.write_text(json.dumps(payload))
                with self.assertRaises(ValueError):
                    harness.load_cases(path)

    def test_rejects_unknown_case_duplicate_and_outside_run(self):
        with self.assertRaisesRegex(ValueError, "用例"):
            harness.prepare(self.root, self.run, ["missing"])
        with self.assertRaisesRegex(ValueError, "work"):
            harness.prepare(self.root, self.root / "public-result")
        self.prepare()
        with self.assertRaises(FileExistsError):
            self.prepare()
        path = self.root / "evals/cases.json"
        path.write_text(json.dumps({"version": 1, "cases": [self.case, self.case]}))
        with self.assertRaisesRegex(ValueError, "重复"):
            harness.load_cases(path)

    def test_false_review_fails_and_missing_evidence_never_passes(self):
        self.prepare()
        self.complete()
        path = self.run / "reviews/facts.json"
        review = json.loads(path.read_text())
        review["criteria"]["scope"]["pass"] = False
        path.write_text(json.dumps(review))
        self.assertEqual(harness.report(self.run)["status"], "fail")
        review["criteria"]["scope"] = {"pass": True, "evidence": ""}
        path.write_text(json.dumps(review))
        self.assertEqual(harness.report(self.run)["status"], "pending_review")


if __name__ == "__main__":
    unittest.main()
