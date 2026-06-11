#!/usr/bin/env python3
"""Channel computation for the versioned docs hub.

The deployed site root carries a ``versions.json`` manifest. Every version
subpath (``latest``, a stable tag like ``v0.1.0``, or a pre-release tag like
``v0.1.0-rc.1``) appears in that manifest; a subset of them are promoted to a
live *channel* the theme surfaces in the selector and root redirect:

  * ``latest``      — always the main branch build.
  * ``stable``      — the newest stable release tag (``vX.Y.Z``).
  * ``pre-release`` — the newest pre-release tag (``vX.Y.Z-<pre>``), but ONLY
    when it is strictly greater (semver precedence) than the newest stable.

The gate matters because a pre-release line is only interesting while it is
*ahead* of the shipped stable. Once a stable release supersedes it (e.g. the
``v0.1.0-rc.1`` pre-release becomes redundant after ``v0.1.0`` ships, or a
pre-release that was always behind a newer stable), the pre-release channel is
withdrawn: the version stays archived and reachable, but it is no longer
promoted as a channel.

Channels are recomputed from the FULL version set on every run, so a
superseding stable release removes the pre-release channel automatically.
"""

from __future__ import annotations

import re
from functools import cmp_to_key

STABLE_RE = re.compile(r"^v\d+\.\d+\.\d+$")
PRE_RE = re.compile(r"^v\d+\.\d+\.\d+-")
_SEMVER_RE = re.compile(
    r"^v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
    r"(?:-(?P<pre>[0-9A-Za-z.-]+))?$"
)


def parse_semver(vid: str) -> tuple[int, int, int, tuple[object, ...]] | None:
    """Parse ``vX.Y.Z`` / ``vX.Y.Z-<pre>`` into comparable components.

    Returns ``(major, minor, patch, pre_ids)`` where ``pre_ids`` is the empty
    tuple for a stable release (which, per semver, has HIGHER precedence than
    any pre-release of the same X.Y.Z). Returns ``None`` for non-semver ids
    such as ``latest``.
    """
    m = _SEMVER_RE.match(vid)
    if not m:
        return None
    major = int(m.group("major"))
    minor = int(m.group("minor"))
    patch = int(m.group("patch"))
    pre = m.group("pre")
    if pre is None:
        return (major, minor, patch, ())
    ids: list[object] = []
    for ident in pre.split("."):
        ids.append(int(ident) if ident.isdigit() else ident)
    return (major, minor, patch, tuple(ids))


def _cmp_pre(a_pre: tuple[object, ...], b_pre: tuple[object, ...]) -> int:
    """Compare two pre-release identifier tuples (semver §11.4).

    An empty tuple means "no pre-release" and ranks HIGHER than any non-empty
    pre-release. Numeric identifiers compare numerically and rank lower than
    alphanumeric identifiers; alphanumeric identifiers compare lexically.
    """
    if not a_pre and not b_pre:
        return 0
    if not a_pre:
        return 1  # stable > pre-release
    if not b_pre:
        return -1
    for x, y in zip(a_pre, b_pre):
        x_num = isinstance(x, int)
        y_num = isinstance(y, int)
        if x_num and y_num:
            if x != y:
                return -1 if x < y else 1
        elif x_num != y_num:
            # Numeric identifiers always have lower precedence than alphanumeric.
            return -1 if x_num else 1
        else:
            if x != y:
                return -1 if x < y else 1
    # All shared identifiers equal: the longer set has higher precedence.
    if len(a_pre) != len(b_pre):
        return -1 if len(a_pre) < len(b_pre) else 1
    return 0


def semver_cmp(a: str, b: str) -> int:
    """Three-way semver-precedence comparison of two version ids.

    Returns -1 / 0 / 1 for a < b / a == b / a > b. Non-semver ids (e.g.
    ``latest``) sort below any semver id and lexically among themselves.
    """
    pa = parse_semver(a)
    pb = parse_semver(b)
    if pa is None and pb is None:
        return (a > b) - (a < b)
    if pa is None:
        return -1
    if pb is None:
        return 1
    for x, y in zip(pa[:3], pb[:3]):
        if x != y:
            return -1 if x < y else 1
    return _cmp_pre(pa[3], pb[3])


_semver_key = cmp_to_key(semver_cmp)


def compute_channels(version_ids):
    """Compute channel assignments from the full set of version ids.

    ``version_ids`` is any iterable of subpath ids (``latest`` plus stable /
    pre-release tags). Returns a dict mapping each id to its channel
    (``"latest"`` / ``"stable"`` / ``"pre-release"``) or ``None`` for an
    archived snapshot.

    The pre-release channel is emitted ONLY when the newest pre-release tag is
    strictly greater (semver precedence) than the newest stable tag. With no
    stable tag, any newest pre-release is shown.
    """
    ids = set(version_ids)
    stable_tags = [v for v in ids if STABLE_RE.match(v)]
    pre_tags = [v for v in ids if PRE_RE.match(v)]

    newest_stable = max(stable_tags, key=_semver_key) if stable_tags else None
    newest_pre = max(pre_tags, key=_semver_key) if pre_tags else None

    # The pre-release channel survives only while it is strictly ahead of the
    # newest stable. A superseding (or always-newer) stable withdraws it.
    if newest_pre is not None and newest_stable is not None:
        if semver_cmp(newest_pre, newest_stable) <= 0:
            newest_pre = None

    result = {}
    for vid in ids:
        if vid == "latest":
            result[vid] = "latest"
        elif vid == newest_stable:
            result[vid] = "stable"
        elif vid == newest_pre:
            result[vid] = "pre-release"
        else:
            result[vid] = None
    return result
