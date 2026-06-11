#!/usr/bin/env python3
"""Unit tests for the docs-hub channel computation semver gate (AAASM-2753).

Run: ``python3 docs/scripts/channels_test.py`` (no third-party deps).
"""

from __future__ import annotations

import sys

from channels import compute_channels, semver_cmp


def _channels(ids):
    """Return {channel: id} for the promoted channels (ignores archived)."""
    out = {}
    for vid, ch in compute_channels(ids).items():
        if ch:
            out[ch] = vid
    return out


def test_semver_comparator():
    # X.Y.Z-pre < X.Y.Z
    assert semver_cmp("v0.1.0-rc.1", "v0.1.0") < 0
    assert semver_cmp("v0.1.0", "v0.1.0-rc.1") > 0
    # alpha < beta < rc
    assert semver_cmp("v0.1.0-alpha.1", "v0.1.0-beta.1") < 0
    assert semver_cmp("v0.1.0-beta.1", "v0.1.0-rc.1") < 0
    # numeric identifiers compare numerically (not lexically: 6 > 5, 10 > 9)
    assert semver_cmp("v0.1.0-alpha.5", "v0.1.0-alpha.6") < 0
    assert semver_cmp("v0.1.0-alpha.9", "v0.1.0-alpha.10") < 0
    # core precedence
    assert semver_cmp("v0.0.2", "v0.1.0") < 0
    assert semver_cmp("v0.2.0-alpha.1", "v0.1.0") > 0
    # latest sorts below any semver id
    assert semver_cmp("latest", "v0.0.1") < 0


def test_scenario_1_prerelease_ahead_of_stable():
    """Pre-release line ahead of the only stable -> pre-release promoted."""
    ids = {
        "latest",
        "v0.0.2",
        "v0.1.0-alpha.5",
        "v0.1.0-alpha.6",
        "v0.1.0-beta.1",
        "v0.1.0-beta.2",
        "v0.1.0-rc.1",
    }
    ch = _channels(ids)
    assert ch == {
        "latest": "latest",
        "stable": "v0.0.2",
        "pre-release": "v0.1.0-rc.1",
    }, ch


def test_scenario_2_stable_supersedes_prerelease():
    """Adding v0.1.0 supersedes the v0.1.0-* line -> no pre-release channel."""
    ids = {
        "latest",
        "v0.0.2",
        "v0.1.0-alpha.5",
        "v0.1.0-alpha.6",
        "v0.1.0-beta.1",
        "v0.1.0-beta.2",
        "v0.1.0-rc.1",
        "v0.1.0",
    }
    full = compute_channels(ids)
    ch = _channels(ids)
    assert ch == {"latest": "latest", "stable": "v0.1.0"}, ch
    assert "pre-release" not in ch
    # The superseded pre-release stays reachable (archived, channel None).
    assert full["v0.1.0-rc.1"] is None


def test_scenario_3_new_prerelease_pulls_ahead():
    """A v0.2.0-alpha.1 pre-release pulls ahead of stable v0.1.0 -> promoted."""
    ids = {
        "latest",
        "v0.0.2",
        "v0.1.0-alpha.5",
        "v0.1.0-alpha.6",
        "v0.1.0-beta.1",
        "v0.1.0-beta.2",
        "v0.1.0-rc.1",
        "v0.1.0",
        "v0.2.0-alpha.1",
    }
    ch = _channels(ids)
    assert ch == {
        "latest": "latest",
        "stable": "v0.1.0",
        "pre-release": "v0.2.0-alpha.1",
    }, ch


def test_no_stable_shows_any_prerelease():
    """With no stable tag, the newest pre-release is always shown."""
    ids = {"latest", "v0.1.0-alpha.5", "v0.1.0-rc.1"}
    ch = _channels(ids)
    assert ch == {"latest": "latest", "pre-release": "v0.1.0-rc.1"}, ch


def test_prerelease_behind_stable_hidden():
    """The old (now-wrong) demo case: pre-release behind stable -> hidden."""
    ids = {"latest", "v0.1.0", "v0.0.1-alpha.5"}
    full = compute_channels(ids)
    ch = _channels(ids)
    assert ch == {"latest": "latest", "stable": "v0.1.0"}, ch
    assert full["v0.0.1-alpha.5"] is None


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"ERROR {t.__name__}: {e!r}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
