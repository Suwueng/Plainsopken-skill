import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "manage.py"
spec = importlib.util.spec_from_file_location("manage", SCRIPT)
manage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manage)


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.destination = self.root / "codex" / "skills" / "plainspoken"
        (self.source / "SKILL.md").write_text("---\nname: plainspoken\ndescription: Test skill\n---\n[Guide](references/guide.md)\n")
        (self.source / "LICENSE").write_text("License fixture")
        (self.source / "agents").mkdir()
        (self.source / "agents" / "openai.yaml").write_text("interface: {}\n")
        (self.source / "references").mkdir()
        (self.source / "references" / "guide.md").write_text("Original guide")
        (self.source / "README.md").write_text("Development only")

    def test_export_excludes_development_and_records_version(self):
        self.assertIsNone(manage.install(self.source, self.destination, "abc123"))
        self.assertFalse((self.destination / "README.md").exists())
        record = json.loads((self.destination / manage.RECORD).read_text())
        self.assertEqual(record["source_commit"], "abc123")
        self.assertEqual(len(record["sha256"]), 4)

    def test_update_removes_stale_files_and_rollback_restores_them(self):
        manage.install(self.source, self.destination, "first")
        (self.destination / "references" / "obsolete.md").write_text("Old extra file")
        (self.source / "references" / "guide.md").write_text("Updated guide")
        backup = manage.install(self.source, self.destination, "second")
        self.assertFalse((self.destination / "references" / "obsolete.md").exists())
        self.assertFalse(backup.is_relative_to(self.destination.parent))
        current_backup = manage.install(backup, self.destination)
        self.assertEqual((self.destination / "references" / "guide.md").read_text(), "Original guide")
        self.assertEqual((self.destination / "references" / "obsolete.md").read_text(), "Old extra file")
        self.assertEqual(json.loads((self.destination / manage.RECORD).read_text())["source_commit"], "first")
        self.assertTrue(current_backup.is_dir())

    def test_invalid_source_leaves_installed_version_untouched(self):
        manage.install(self.source, self.destination, "first")
        original = (self.destination / "SKILL.md").read_bytes()
        (self.source / "references" / "guide.md").unlink()
        with self.assertRaisesRegex(ValueError, "无效本地链接"):
            manage.install(self.source, self.destination)
        self.assertEqual((self.destination / "SKILL.md").read_bytes(), original)

    def test_symlinks_and_overlapping_destination_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "不能重叠"):
            manage.install(self.source, self.source / "installed")
        self.destination.parent.mkdir(parents=True)
        self.destination.symlink_to(self.source, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "符号链接"):
            manage.install(self.source, self.destination)
        (self.source / "references" / "alias.md").symlink_to(self.source / "LICENSE")
        with self.assertRaisesRegex(ValueError, "符号链接"):
            manage.check(self.source)

    def test_failed_swap_restores_previous_installation(self):
        manage.install(self.source, self.destination, "first")
        original_rename = Path.rename

        def fail_stage(path, target):
            if path.name == "package":
                raise OSError("simulated swap failure")
            return original_rename(path, target)

        with patch.object(Path, "rename", fail_stage):
            with self.assertRaisesRegex(OSError, "simulated swap failure"):
                manage.install(self.source, self.destination, "second")
        self.assertEqual(json.loads((self.destination / manage.RECORD).read_text())["source_commit"], "first")

    def test_uncommitted_changes_block_installation(self):
        def git(*args):
            return subprocess.run(["git", "-C", str(self.source), *args], check=True, capture_output=True)
        git("init", "-b", "main")
        git("add", ".")
        git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-m", "Fixture")
        self.assertEqual(len(manage.committed_source(self.source)), 40)
        (self.source / ".git" / "info" / "exclude").write_text("references/ignored.txt\n")
        ignored = self.source / "references" / "ignored.txt"
        ignored.write_text("Ignored file must not enter a versioned installation")
        with self.assertRaisesRegex(ValueError, "未纳入 Git"):
            manage.committed_source(self.source)
        ignored.unlink()
        (self.source / "SKILL.md").write_text("Uncommitted change")
        with self.assertRaisesRegex(ValueError, "未提交"):
            manage.committed_source(self.source)


if __name__ == "__main__":
    unittest.main()
