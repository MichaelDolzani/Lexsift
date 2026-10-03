import requests

from lexsift import updates
from lexsift.updates import newer_release


def release(tag, **kwargs):
    return {"tag_name": tag, "html_url": f"https://example.org/{tag}", "body": None, **kwargs}


def test_no_releases_yet():
    assert newer_release([], "0.12.5") is None


def test_api_error_object():
    # GitHub returns a dict for 404s and rate limiting
    assert newer_release({"message": "API rate limit exceeded"}, "0.12.5") is None


def test_newer_release_found():
    assert newer_release([release("v0.13.0"), release("v0.12.5")], "0.12.5")["tag_name"] == "v0.13.0"


def test_picks_highest_version_not_first():
    data = [release("v0.12.6"), release("v0.14.0"), release("v0.13.0")]
    assert newer_release(data, "0.12.5")["tag_name"] == "v0.14.0"


def test_same_or_older_is_not_newer():
    assert newer_release([release("v0.12.5"), release("v0.11.0")], "0.12.5") is None


def test_skips_drafts_prereleases_and_bad_tags():
    data = [release("v1.0.0", draft=True), release("v0.99.0", prerelease=True), release("nightly")]
    assert newer_release(data, "0.12.5") is None


def test_fetch_offline_does_not_raise(monkeypatch):
    def offline(*args, **kwargs):
        raise requests.ConnectionError("offline")
    monkeypatch.setattr(updates.requests, "get", offline)
    assert updates.fetch_newer_release("0.12.5") is None
