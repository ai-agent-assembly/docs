"""Tests for the stale-repo-name audit's scanned-surface coverage.

The audit is a CI gate, and its blind spots are silent: a surface it never sweeps
lets a retired repo name sit undetected. AAASM-4943 widened the sweep to the
mdBook ``.hbs`` theme templates, the suffix-less ``CODEOWNERS`` file, and the
``.po``/``.pot`` translation catalogs (previously counted but not name-audited).
These tests pin that coverage so a future narrowing of the surface set fails
loudly instead of re-opening the gap.

Stdlib ``unittest`` only — this repo has no third-party test toolchain. Run with:
``python3.12 -m unittest docs.scripts.test_check_repo_names`` from the repo root,
or ``python3.12 docs/scripts/test_check_repo_names.py``.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_repo_names as audit  # noqa: E402

# One representative retired name from the alias map, with its replacement.
_OLD_NAME = "agent-assembly-cloud"
_NEW_NAME = "cloud"


class TrackedSurfaceCoverageTest(unittest.TestCase):
    """The real repo's ``.hbs`` and ``CODEOWNERS`` files must be in the sweep."""

    def setUp(self) -> None:
        rels = {p.relative_to(audit.REPO_ROOT).as_posix() for p in audit.tracked_files()}
        self._tracked = rels

    def test_hbs_theme_template_is_swept(self) -> None:
        self.assertIn("docs/theme/head.hbs", self._tracked)

    def test_codeowners_is_swept(self) -> None:
        # Suffix-less, so it is matched by exact filename, not extension.
        self.assertIn(".github/CODEOWNERS", self._tracked)

    def test_po_catalogs_are_discoverable(self) -> None:
        # Fed into audit_stale_names by main() alongside tracked_files().
        po_rels = {
            p.relative_to(audit.REPO_ROOT).as_posix() for p in audit.tracked_po_files()
        }
        self.assertIn("docs/po/messages.pot", po_rels)


class StaleNameDetectionTest(unittest.TestCase):
    """A retired name planted in a newly-swept surface is caught by the audit."""

    def _fixture(self, tmp: str, name: str, body: str) -> Path:
        path = Path(tmp) / name
        path.write_text(body, encoding="utf-8")
        return path

    # Fixtures live under REPO_ROOT because audit_stale_names reports repo-relative
    # paths (path.relative_to(REPO_ROOT)); they are untracked temp files, so they
    # do not affect the git-ls-files-driven clean-tree run.
    _TMP_UNDER_ROOT = {"dir": audit.REPO_ROOT}

    def test_flags_stale_name_in_hbs_fixture(self) -> None:
        with tempfile.TemporaryDirectory(**self._TMP_UNDER_ROOT) as tmp:
            path = self._fixture(
                tmp, "head.hbs", f'<link href="https://github.com/org/{_OLD_NAME}">\n'
            )
            violations = audit.audit_stale_names([path])
        self.assertEqual(len(violations), 1)
        self.assertIn(_OLD_NAME, violations[0])
        self.assertIn(_NEW_NAME, violations[0])

    def test_flags_stale_name_in_codeowners_fixture(self) -> None:
        with tempfile.TemporaryDirectory(**self._TMP_UNDER_ROOT) as tmp:
            path = self._fixture(
                tmp, "CODEOWNERS", f"docs/ @ai-agent-assembly/{_OLD_NAME}\n"
            )
            violations = audit.audit_stale_names([path])
        self.assertEqual(len(violations), 1)
        self.assertIn(_OLD_NAME, violations[0])

    def test_flags_stale_name_in_po_fixture(self) -> None:
        with tempfile.TemporaryDirectory(**self._TMP_UNDER_ROOT) as tmp:
            path = self._fixture(
                tmp, "zh-Hant.po", f'msgid "see {_OLD_NAME} for details"\n'
            )
            violations = audit.audit_stale_names([path])
        self.assertEqual(len(violations), 1)
        self.assertIn(_OLD_NAME, violations[0])


class CleanTreeRegressionTest(unittest.TestCase):
    """The widened sweep must still pass on the current (clean) tree."""

    def test_main_exits_zero(self) -> None:
        self.assertEqual(audit.main([]), 0)


if __name__ == "__main__":
    unittest.main()
