import sys

import pytest

from lexsift.dictformats import MissingDependencyError, parseMDX


def test_parse_mdx_without_readmdict(monkeypatch):
    # A None entry in sys.modules makes the import fail, as when python-lzo/readmdict are missing
    monkeypatch.setitem(sys.modules, "readmdict", None)
    with pytest.raises(MissingDependencyError, match=r"lexsift\[mdx\]"):
        parseMDX("unused.mdx")
