import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "privacy.py"
OLD_LICENSED_PATH = "references/astrodict/astrodict241020_ec.txt"
LICENSED_PATH = "skills/plainspoken/" + OLD_LICENSED_PATH
# Synthetic bytes exercise historical privacy exceptions, not distribution permission.
LICENSED_DATA = b"Synthetic astronomy fixture.\n"
spec = importlib.util.spec_from_file_location("privacy", SCRIPT)
privacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(privacy)


class PrivacyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        (self.root / ".gitignore").write_text("/work/\n.env\n")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.DEVNULL)

    def commit(self, message="Fixture"):
        self.git("add", "-A")
        self.git("commit", "-m", message)

    def rules(self, report):
        return {item["rule"] for item in report["findings"]}

    def test_untracked_content_and_redacted_report(self):
        secret = "ghp_" + "a1B2" * 10
        (self.root / "draft.md").write_text(secret)
        report = privacy.scan(self.root)
        self.assertIn("token", self.rules(report))
        self.assertNotIn(secret, json.dumps(report))
        self.assertEqual(report["coverage"], "generic_only")

    def test_staged_content_is_independent_of_worktree(self):
        path = self.root / "draft.md"
        path.write_text("owner" + "@private.invalid")
        self.git("add", "draft.md")
        path.write_text("Clean content")
        self.assertFalse(privacy.scan(self.root)["findings"])
        self.assertIn("email", self.rules(privacy.scan(self.root, "staged")))

    def test_deleted_content_and_old_identity_remain_in_history(self):
        secret = "sk-" + "Ab12" * 10
        (self.root / "removed.md").write_text(secret)
        self.git("add", "-A")
        self.git("-c", "user.name=Private Person", "-c", "user.email=owner" + "@private.invalid", "commit", "-m", "Fixture")
        (self.root / "removed.md").unlink()
        self.commit()
        self.assertFalse(privacy.scan(self.root)["findings"])
        report = privacy.scan(self.root, "history")
        self.assertTrue({"token", "email", "identity"}.issubset(self.rules(report)))
        output = json.dumps(report)
        for value in (secret, "Private Person", "owner" + "@private.invalid"):
            self.assertNotIn(value, output)

    def test_history_includes_other_branches_and_annotated_tags(self):
        self.commit()
        self.git("checkout", "-b", "other")
        (self.root / "other.md").write_text("/" + "Users/" + "private-person/Documents")
        self.commit()
        self.git("checkout", "main")
        self.git("tag", "-a", "fixture", "-m", "Contact owner" + "@private.invalid")
        rules = self.rules(privacy.scan(self.root, "history"))
        self.assertTrue({"user-path", "email"}.issubset(rules))

    def test_history_scans_and_redacts_lightweight_tag_and_branch_names(self):
        self.commit()
        email = "owner" + "@private.invalid"
        private = "Private" + "Handle123"
        folder = self.root / "work"
        folder.mkdir()
        (folder / "private-patterns.txt").write_text(private + "\n")
        self.git("tag", email)
        self.git("branch", private)
        report = privacy.scan(self.root, "history")
        self.assertTrue({"email", "local-private-pattern"}.issubset(self.rules(report)))
        self.assertNotIn(email, json.dumps(report))
        self.assertNotIn(private, json.dumps(report))

    def test_history_scans_commit_messages_and_tags_to_blobs(self):
        self.commit("Contact owner" + "@private.invalid")
        oid = subprocess.check_output(
            ["git", "-C", str(self.root), "hash-object", "-w", "--stdin"], input=b"\x00\xff"
        ).decode().strip()
        self.git("tag", "binary-fixture", oid)
        report = privacy.scan(self.root, "history")
        self.assertTrue({"email", "binary"}.issubset(self.rules(report)))
        self.assertTrue(any(item["location"].endswith(":message") for item in report["findings"]))

    def test_history_scans_tags_to_trees_with_private_paths(self):
        folder = self.root / "work"
        folder.mkdir()
        (folder / "note.md").write_text("clean")
        self.git("add", "-f", "work/note.md")
        oid = self.git("write-tree").decode().strip()
        self.git("tag", "tree-fixture", oid)
        self.assertIn("private-path", self.rules(privacy.scan(self.root, "history")))

    def test_symlinks_are_not_followed_in_each_scope(self):
        (self.root / "alias.md").symlink_to("absent")
        self.assertIn("symlink", self.rules(privacy.scan(self.root)))
        self.git("add", "alias.md")
        self.assertIn("symlink", self.rules(privacy.scan(self.root, "staged")))
        self.commit()
        self.assertIn("symlink", self.rules(privacy.scan(self.root, "history")))

    def test_symlinked_parent_is_not_followed(self):
        folder = self.root / "nested"
        folder.mkdir()
        (folder / "file.md").write_text("clean")
        self.commit()
        (folder / "file.md").unlink()
        folder.rmdir()
        folder.symlink_to(self.root, target_is_directory=True)
        self.assertIn("symlink", self.rules(privacy.scan(self.root)))

    def test_ignored_local_patterns_are_used_without_reporting_them(self):
        folder = self.root / "work"
        folder.mkdir()
        value = "Private" + "Handle123"
        (folder / "private-patterns.txt").write_text(value + "\n")
        (self.root / "draft.md").write_text(value)
        report = privacy.scan(self.root)
        self.assertEqual(report["coverage"], "generic_and_local")
        self.assertIn("local-private-pattern", self.rules(report))
        self.assertNotIn(value, json.dumps(report))

    def test_local_patterns_must_be_ignored_and_untracked(self):
        folder = self.root / "work"
        folder.mkdir()
        (folder / "private-patterns.txt").write_text("Private" + "Handle123\n")
        self.git("add", "-f", "work/private-patterns.txt")
        self.assertIn("local-patterns-not-private", self.rules(privacy.scan(self.root)))

    def test_unreadable_local_patterns_and_non_repository_fail_closed(self):
        folder = self.root / "work" / "private-patterns.txt"
        folder.mkdir(parents=True)
        self.assertIn("unreadable-local-patterns", self.rules(privacy.scan(self.root)))
        with tempfile.TemporaryDirectory() as empty:
            self.assertIn("scan-error", self.rules(privacy.scan(Path(empty))))

    def test_binary_and_forbidden_paths_fail_closed(self):
        (self.root / "unknown.dat").write_bytes(b"\x00\xff\x01")
        (self.root / ".env").write_text("SAFE=1")
        self.git("add", "-f", ".env")
        self.assertTrue({"binary", "private-path"}.issubset(self.rules(privacy.scan(self.root))))

    def test_common_rules_and_allowed_examples(self):
        examples = "test@example.invalid test@example.com 123+test@users.noreply.github.com"
        self.assertFalse(privacy.content_rules(examples, []))
        for value in ("/" + "Users/alice/a", "/" + "home/alice/a", "C:" + "\\Users\\alice\\a"):
            self.assertIn("user-path", privacy.content_rules(value, []))
        self.assertIn("private-key", privacy.content_rules("-----BEGIN " + "PRIVATE KEY-----", []))

    def test_approved_public_identity_overrides_only_contained_local_patterns(self):
        name, email = "Peng Cheng", "chengpengsmc@qq.com"
        identity = f"{name} <{email}>"
        patterns = [name, email, identity, name.split()[1], email.split("@")[0][:-3]]
        for text in (name, email, identity, f"Author: {identity}\n"):
            with self.subTest(text=text):
                self.assertFalse(privacy.content_rules(text, patterns))
        self.assertIn("local-private-pattern", privacy.content_rules(f"Author: {identity}", [f"Author: {identity}"]))
        self.assertIn("local-private-pattern", privacy.content_rules(f"{email}\n{patterns[-1]}", patterns))

    def test_public_email_exception_has_strict_boundaries(self):
        email = "chengpengsmc@qq.com"
        private = email.split("@")[0][:-3]
        for text in ("x" + email, "+" + email, email + "x", email + ".invalid", email + "-extra", "x@" + email):
            with self.subTest(text=text):
                self.assertTrue({"email", "local-private-pattern"}.issubset(privacy.content_rules(text, [private])))
        self.assertIn("email", privacy.content_rules("someone" + "@qq.com", []))
        self.assertIn("email", privacy.content_rules(email.upper(), []))

    def test_public_identity_does_not_allow_local_user_paths(self):
        name, email = "Peng Cheng", "chengpengsmc@qq.com"
        private = email.split("@")[0][:-3]
        for user in (name, email, private):
            with self.subTest(user=user):
                text = "/" + "Users/" + user + "/Documents"
                self.assertTrue({"user-path", "local-private-pattern"}.issubset(privacy.content_rules(text, [user])))

    def test_history_allows_exact_public_identity_with_local_patterns(self):
        name, email = "Peng Cheng", "chengpengsmc@qq.com"
        self.git("config", "user.name", name)
        self.git("config", "user.email", email)
        folder = self.root / "work"
        folder.mkdir()
        (folder / "private-patterns.txt").write_text(email.split("@")[0][:-3] + "\n" + name + "\n")
        self.commit()
        self.git("tag", "-a", "public", "-m", "Fixture")
        self.assertFalse(privacy.scan(self.root, "history")["findings"])

    def test_history_rejects_public_identity_with_wrong_name_or_email(self):
        name, email = "Peng Cheng", "chengpengsmc@qq.com"
        for actual_name, actual_email in ((name, "test@example.invalid"), ("Test", email), (name.lower(), email)):
            with self.subTest(name=actual_name, email=actual_email):
                self.git("-c", "user.name=" + actual_name, "-c", "user.email=" + actual_email,
                         "commit", "--allow-empty", "-m", "Fixture")
                oid = self.git("rev-parse", "HEAD").decode().strip()
                findings = privacy.scan(self.root, "history")["findings"]
                self.assertIn({"location": f"commit:{oid}:author", "rule": "identity"}, findings)
                self.assertIn({"location": f"commit:{oid}:committer", "rule": "identity"}, findings)

    def test_sensitive_filename_is_redacted(self):
        value = "owner" + "@private.invalid"
        (self.root / value).write_text("clean")
        report = privacy.scan(self.root)
        self.assertIn("email", self.rules(report))
        self.assertNotIn(value, json.dumps(report))

    @patch.object(privacy, "LICENSED_SHA256", hashlib.sha256(LICENSED_DATA).hexdigest())
    def test_licensed_data_exception_is_only_for_historical_review(self):
        folder = self.root / "work"
        folder.mkdir()
        (folder / "private-patterns.txt").write_text("astronomy\n")
        previous = None
        for path in (OLD_LICENSED_PATH, LICENSED_PATH):
            with self.subTest(path=path):
                target = self.root / path
                target.parent.mkdir(parents=True)
                target.write_bytes(LICENSED_DATA)
                if previous is not None:
                    previous.unlink()
                self.commit()
                self.assertFalse(privacy.scan(self.root, "history", allow_legacy_data=True)["findings"])
                for scope in ("worktree", "staged", "history"):
                    self.assertIn("external-data-in-candidate", self.rules(privacy.scan(self.root, scope)))
                previous = target

    def test_legacy_exception_cannot_be_used_on_current_candidates(self):
        for scope in ("worktree", "staged"):
            with self.assertRaises(ValueError):
                privacy.scan(self.root, scope, allow_legacy_data=True)

    def test_external_dictionary_readme_is_not_a_publication_candidate(self):
        for path in ("references/astrodict/readme.txt", "skills/plainspoken/references/astrodict/readme.txt"):
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("Synthetic external resource notice")
        self.git("add", "-A")
        for scope in ("worktree", "staged"):
            self.assertEqual(sum(x["rule"] == "external-data-in-candidate"
                                 for x in privacy.scan(self.root, scope)["findings"]), 2)

    @patch.object(privacy, "LICENSED_SHA256", hashlib.sha256(LICENSED_DATA).hexdigest())
    def test_licensed_data_exception_cannot_hide_modified_content(self):
        for path in (OLD_LICENSED_PATH, LICENSED_PATH):
            with self.subTest(path=path):
                target = self.root / path
                target.parent.mkdir(parents=True)
                target.write_bytes(LICENSED_DATA + ("owner" + "@private.invalid").encode())
                self.commit()
                for scope in ("worktree", "staged", "history"):
                    findings = privacy.scan(self.root, scope)["findings"]
                    rules = {item["rule"] for item in findings if item["location"].endswith(":" + path)}
                    self.assertTrue({"licensed-data-changed", "email"}.issubset(rules), scope)
                report = privacy.scan(self.root, "history", allow_legacy_data=True)
                self.assertTrue({"licensed-data-changed", "email"}.issubset(self.rules(report)))

    @patch.object(privacy, "LICENSED_SHA256", hashlib.sha256(LICENSED_DATA).hexdigest())
    def test_licensed_data_at_other_path_still_uses_content_rules(self):
        folder = self.root / "work"
        folder.mkdir()
        (folder / "private-patterns.txt").write_text("astronomy\n")
        target = self.root / "skills/other/references/astrodict/astrodict241020_ec.txt"
        target.parent.mkdir(parents=True)
        target.write_bytes(LICENSED_DATA)
        self.commit()
        for scope in ("worktree", "staged", "history"):
            self.assertIn("local-private-pattern", self.rules(privacy.scan(self.root, scope)), scope)


if __name__ == "__main__":
    unittest.main()
