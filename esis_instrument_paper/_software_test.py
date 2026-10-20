import pathlib
import re

import aastex

import esis_instrument_paper


def test_software() -> None:
    """
    Every package has a concept DOI on Zenodo to be cited by, no two share a
    key, and no key is also the key of an entry in ``sources.bib``, which
    the document refuses to build with.
    """
    result = esis_instrument_paper.software()
    assert isinstance(result, aastex.Software)
    packages = [n for n in result.names if isinstance(n, aastex.PythonPackage)]
    assert packages
    for package in packages:
        assert package.doi_.startswith("10.5281/zenodo.")
    keys = [package.key_ for package in packages]
    assert len(set(keys)) == len(keys)
    path = pathlib.Path(esis_instrument_paper.__file__).parent / "sources.bib"
    sources = re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", path.read_text(encoding="utf-8"))
    assert not set(keys) & set(sources)
