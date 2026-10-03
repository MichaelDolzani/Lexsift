"Checking GitHub for newer Lexsift releases"
from typing import Any, Optional

import requests
from loguru import logger
from packaging import version

RELEASES_URL = "https://api.github.com/repos/MichaelDolzani/Lexsift/releases"


def newer_release(data: Any, current_version: str) -> Optional[dict]:
    """Return the newest published release in a GitHub releases API response
    if it is newer than current_version, otherwise None.

    data is whatever the API returned: an error object, an empty list when
    there are no releases yet, or a list of releases.
    """
    if not isinstance(data, list):
        return None
    releases = [r for r in data
                if isinstance(r, dict) and not r.get("draft") and not r.get("prerelease") and r.get("tag_name")]
    best: Optional[dict] = None
    best_version = None
    for release in releases:
        try:
            v = version.parse(release["tag_name"].lstrip("v"))
        except version.InvalidVersion:
            continue
        if best_version is None or v > best_version:
            best, best_version = release, v
    try:
        current = version.parse(current_version)
    except version.InvalidVersion:
        return None
    if best is None or best_version is None or best_version <= current:
        return None
    return best


def fetch_newer_release(current_version: str) -> Optional[dict]:
    "Query GitHub; never raises, since being offline or rate limited is not an error worth showing"
    try:
        res = requests.get(RELEASES_URL, timeout=5)
        res.raise_for_status()
        return newer_release(res.json(), current_version)
    except (requests.RequestException, ValueError) as e:
        logger.info(f"Could not check for updates: {e!r}")
        return None
