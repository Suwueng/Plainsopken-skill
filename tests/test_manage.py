import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
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
        self.skill = self.source / "skills/plainspoken"
        self.skill.mkdir(parents=True)
        self.destination = self.root / "codex" / "skills" / "plainspoken"
        (self.skill / "SKILL.md").write_text("---\nname: plainspoken\ndescription: Test skill\n---\n[Guide](references/guide.md)\n[License](LICENSE)\n")
        (self.source / "LICENSE").write_text("License fixture")
        (self.skill / "LICENSE").write_text("License fixture")
        (self.skill / "THIRD_PARTY_NOTICES.md").write_text("External resources keep their own terms")
        (self.skill / "agents").mkdir()
        (self.skill / "agents" / "openai.yaml").write_text("interface: {}\n")
        (self.skill / "references").mkdir()
        (self.skill / "references" / "guide.md").write_text("Original guide")
        (self.source / "README.md").write_text("Development only")

    def install(self, commit=None):
        return manage.install(self.skill, self.destination, commit)

    def test_export_excludes_development_and_records_version(self):
        self.assertIsNone(self.install("abc123"))
        self.assertFalse((self.destination / "README.md").exists())
        self.assertEqual((self.destination / "LICENSE").read_bytes(), (self.source / "LICENSE").read_bytes())
        self.assertEqual((self.destination / "SKILL.md").read_bytes(), (self.skill / "SKILL.md").read_bytes())
        self.assertFalse((self.destination / "skills").exists())
        self.assertEqual((self.destination / "THIRD_PARTY_NOTICES.md").read_bytes(), (self.skill / "THIRD_PARTY_NOTICES.md").read_bytes())
        record = json.loads((self.destination / manage.RECORD).read_text())
        self.assertEqual(record["source_commit"], "abc123")
        self.assertEqual(record["source_path"], str(self.skill.resolve()))
        self.assertEqual(len(record["sha256"]), 5)

    def test_skill_directory_is_a_complete_standalone_package(self):
        standalone = self.root / "standalone"
        shutil.copytree(self.skill, standalone)
        shutil.rmtree(self.source)
        manage.install(standalone, self.destination)
        self.assertEqual((self.destination / "LICENSE").read_text(), "License fixture")
        self.assertTrue((self.destination / "THIRD_PARTY_NOTICES.md").is_file())

    def test_license_drift_and_missing_notice_block_repository_checks(self):
        (self.source / "LICENSE").write_text("Updated root license")
        with self.assertRaisesRegex(ValueError, "许可.*同步"):
            manage.check_repository(self.source)
        self.assertEqual((self.skill / "LICENSE").read_text(), "License fixture")
        manage.sync_license(self.source)
        self.assertEqual((self.skill / "LICENSE").read_text(), "Updated root license")
        manage.check_repository(self.source)
        (self.skill / "THIRD_PARTY_NOTICES.md").unlink()
        with self.assertRaisesRegex(ValueError, "THIRD_PARTY_NOTICES"):
            manage.check_repository(self.source)

    def test_sync_license_rejects_symlink_without_overwriting_target(self):
        outside = self.root / "outside-license"
        outside.write_text("Unrelated file")
        (self.skill / "LICENSE").unlink()
        (self.skill / "LICENSE").symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "符号链接"):
            manage.sync_license(self.source)
        self.assertEqual(outside.read_text(), "Unrelated file")

    def test_new_source_rejects_bundled_external_dictionary(self):
        data = self.skill / "references/astrodict/fixture.txt"
        data.parent.mkdir()
        data.write_text("Synthetic external dictionary")
        with self.assertRaisesRegex(ValueError, "外部词库"):
            manage.check_repository(self.source)

    def test_legacy_package_without_notice_can_still_be_restored(self):
        (self.skill / "THIRD_PARTY_NOTICES.md").unlink()
        data = self.skill / "references/astrodict/fixture.txt"
        data.parent.mkdir()
        data.write_text("Legacy fixture")
        self.install("legacy")
        self.assertEqual((self.destination / "references/astrodict/fixture.txt").read_text(), "Legacy fixture")

    def test_update_removes_stale_files_and_rollback_restores_them(self):
        self.install("first")
        (self.destination / "references" / "obsolete.md").write_text("Old extra file")
        (self.skill / "references" / "guide.md").write_text("Updated guide")
        backup = self.install("second")
        self.assertFalse((self.destination / "references" / "obsolete.md").exists())
        self.assertFalse(backup.is_relative_to(self.destination.parent))
        current_backup = manage.install(backup, self.destination)
        self.assertEqual((self.destination / "references" / "guide.md").read_text(), "Original guide")
        self.assertEqual((self.destination / "references" / "obsolete.md").read_text(), "Old extra file")
        self.assertEqual(json.loads((self.destination / manage.RECORD).read_text())["source_commit"], "first")
        self.assertTrue(current_backup.is_dir())

    def test_invalid_source_leaves_installed_version_untouched(self):
        self.install("first")
        original = (self.destination / "SKILL.md").read_bytes()
        (self.skill / "references" / "guide.md").unlink()
        with self.assertRaisesRegex(ValueError, "无效本地链接"):
            self.install()
        self.assertEqual((self.destination / "SKILL.md").read_bytes(), original)

    def test_symlinks_and_overlapping_destination_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "不能重叠"):
            manage.install(self.skill, self.skill / "installed")
        self.destination.parent.mkdir(parents=True)
        self.destination.symlink_to(self.skill, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "符号链接"):
            self.install()
        (self.skill / "references" / "alias.md").symlink_to(self.source / "LICENSE")
        with self.assertRaisesRegex(ValueError, "符号链接"):
            manage.check(self.skill)

    def test_runtime_cannot_link_to_repository_development_files(self):
        for link in ("../../README.md", "README.md"):
            with self.subTest(link=link):
                (self.skill / "README.md").write_text("Development file inside source")
                (self.skill / "references/guide.md").write_text("Original guide")
                (self.skill / "SKILL.md").write_text(
                    "---\nname: plainspoken\ndescription: Test skill\n---\n" + f"[Development]({link})\n"
                )
                with self.assertRaisesRegex(ValueError, "无效本地链接"):
                    self.install()
                self.assertFalse(self.destination.exists())

    def test_failed_swap_restores_previous_installation(self):
        self.install("first")
        original_rename = Path.rename

        def fail_stage(path, target):
            if path.name == "package":
                raise OSError("simulated swap failure")
            return original_rename(path, target)

        with patch.object(Path, "rename", fail_stage):
            with self.assertRaisesRegex(OSError, "simulated swap failure"):
                self.install("second")
        self.assertEqual(json.loads((self.destination / manage.RECORD).read_text())["source_commit"], "first")

    def test_uncommitted_changes_block_installation(self):
        def git(*args):
            return subprocess.run(["git", "-C", str(self.source), *args], check=True, capture_output=True)
        git("init", "-b", "main")
        git("add", ".")
        git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-m", "Fixture")
        self.assertEqual(len(manage.committed_source(self.source)), 40)
        (self.source / ".git" / "info" / "exclude").write_text("skills/plainspoken/references/ignored.txt\n")
        ignored = self.skill / "references" / "ignored.txt"
        ignored.write_text("Ignored file must not enter a versioned installation")
        with self.assertRaisesRegex(ValueError, "未纳入 Git"):
            manage.committed_source(self.source)
        ignored.unlink()
        for relative in ("skills/plainspoken/SKILL.md", "LICENSE", "README.md"):
            with self.subTest(path=relative):
                path = self.source / relative
                original = path.read_bytes()
                path.write_text("Uncommitted change")
                with self.assertRaisesRegex(ValueError, "未提交"):
                    manage.committed_source(self.source)
                path.write_bytes(original)

    def test_cli_uses_nested_source_and_root_license_from_another_directory(self):
        script = self.source / "scripts/manage.py"
        script.parent.mkdir()
        shutil.copy2(SCRIPT, script)
        development = self.source / "docs/design.md"
        development.parent.mkdir()
        development.write_text("Development document must survive")
        for args in (("init", "-b", "main"), ("add", "."),
                     ("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-m", "Fixture")):
            subprocess.run(["git", "-C", str(self.source), *args], check=True, capture_output=True)

        def run(*args):
            return subprocess.run([sys.executable, str(script), *args], cwd=self.root, capture_output=True, text=True)

        checked = run("check")
        self.assertEqual(checked.returncode, 0, checked.stderr)
        (self.skill / "LICENSE").write_text("Out of sync")
        mismatch = run("check")
        self.assertNotEqual(mismatch.returncode, 0)
        synced = run("sync-license")
        self.assertEqual(synced.returncode, 0, synced.stderr)
        self.assertEqual((self.skill / "LICENSE").read_bytes(), (self.source / "LICENSE").read_bytes())
        installed = run("install", "--dest", str(self.destination))
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertEqual((self.destination / "LICENSE").read_bytes(), (self.source / "LICENSE").read_bytes())
        self.assertFalse((self.destination / "scripts").exists())
        self.assertFalse((self.destination / "README.md").exists())
        overlap = run("install", "--dest", str(development.parent))
        self.assertNotEqual(overlap.returncode, 0)
        self.assertIn("开发仓库", overlap.stderr)
        self.assertEqual(development.read_text(), "Development document must survive")
        (self.skill / "references/guide.md").write_text("Uncommitted rules")
        blocked = run("install", "--dest", str(self.destination))
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("未提交", blocked.stderr)
        self.assertEqual((self.destination / "references/guide.md").read_text(), "Original guide")
        rolled_back = run("rollback", str(self.destination), "--dest", str(self.root / "restored"))
        self.assertEqual(rolled_back.returncode, 0, rolled_back.stderr)
        self.assertEqual((self.root / "restored" / manage.RECORD).read_bytes(), (self.destination / manage.RECORD).read_bytes())


if __name__ == "__main__":
    unittest.main()
