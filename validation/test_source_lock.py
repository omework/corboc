# SPDX-License-Identifier: MIT OR Apache-2.0
"""Exercise source identity checks using isolated local Git repositories."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import corbo_sources


class SourceLockTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="corboc-lock-")
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name).resolve()
        self.source = self.home / "source"
        self.source.mkdir()
        self.compiler = self.home / "compiler"
        self.compiler.mkdir()
        original = corbo_sources.ROOT
        self.addCleanup(setattr, corbo_sources, "ROOT", original)
        corbo_sources.ROOT = self.compiler
        self.git(self.source, "init", "-q")
        for name in ("stdlib/src/item.crb", "runtime/corbo_runtime.h", "CORE_GRAMMAR.ebnf",
                     "docs/LANGUAGE_RULES.md", "docs/VALIDATION_GUIDELINES.md"):
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture\n")
        self.git(self.source, "add", ".")
        self.commit(self.source)
        self.revision = self.git(self.source, "rev-parse", "HEAD").strip()
        (self.compiler / "corbo.lock").write_text(
            f'[corbo]\ngit="{self.source.as_posix()}"\nrev="{self.revision}"\n'
            'stdlib="stdlib/src"\nruntime="runtime"\ngrammar="CORE_GRAMMAR.ebnf"\n'
            'rules="docs/LANGUAGE_RULES.md"\nvalidation_guidelines="docs/VALIDATION_GUIDELINES.md"\n'
        )

    def git(self, repo, *args):
        result = subprocess.run(["git", *args], cwd=repo, check=True,
                                capture_output=True, text=True, timeout=30)
        return result.stdout

    def commit(self, repo):
        self.git(repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "--no-gpg-sign", "--allow-empty", "-qm", "fixture")

    def test_clean_locked_source(self):
        self.assertEqual(corbo_sources.source_root(self.source), self.source)

    def test_local_clone_uses_commit_not_dirty_working_tree(self):
        (self.source / "stdlib/src/item.crb").write_text("uncommitted\n")
        cache = corbo_sources.prepare(self.source)
        self.assertEqual((cache / "stdlib/src/item.crb").read_text(), "fixture\n")
        self.assertEqual(self.git(cache, "rev-parse", "HEAD").strip(), self.revision)

    def test_modified_std_rejected(self):
        (self.source / "stdlib/src/item.crb").write_text("modified\n")
        with self.assertRaisesRegex(RuntimeError, "local changes"):
            corbo_sources.source_root(self.source)

    def test_untracked_runtime_code_rejected(self):
        (self.source / "runtime/extra.c.inc").write_text("modified\n")
        with self.assertRaisesRegex(RuntimeError, "local changes"):
            corbo_sources.source_root(self.source)

    def test_wrong_cache_revision_is_not_reset(self):
        cache = corbo_sources.prepare(self.source)
        self.commit(cache)
        changed = self.git(cache, "rev-parse", "HEAD").strip()
        with self.assertRaisesRegex(RuntimeError, "revision mismatch"):
            corbo_sources.prepare()
        self.assertEqual(self.git(cache, "rev-parse", "HEAD").strip(), changed)

    def test_short_revision_rejected(self):
        path = self.compiler / "corbo.lock"
        path.write_text(path.read_text().replace(self.revision, self.revision[:8]))
        with self.assertRaisesRegex(ValueError, "full immutable commit"):
            corbo_sources.lock()


if __name__ == "__main__":
    unittest.main()
