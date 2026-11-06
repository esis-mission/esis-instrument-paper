import aastex

__all__ = [
    "software",
]


def software() -> aastex.Software:
    """
    The software this article was built with, in alphabetical order.

    The packages of the ESIS team, and fiasco, are cited by the archive on
    Zenodo of the version installed, so that the citation follows the
    version the article is built with. Of these, only aastex declares its
    concept DOI in its metadata so far, so the others are given theirs here.
    Astropy, Matplotlib and NumPy are cited by the papers they ask to be
    cited by.
    """
    return aastex.Software(
        [
            aastex.PythonPackage("aastex"),
            r"Astropy \citep{Astropy2013,Astropy2018,Astropy2022}",
            aastex.PythonPackage(
                "euv-snapshot-imaging-spectrograph",
                key="esis",
                doi="10.5281/zenodo.23113153",
            ),
            aastex.PythonPackage("fiasco", doi="10.5281/zenodo.7504257"),
            r"Matplotlib \citep{Hunter2007}",
            aastex.PythonPackage(
                "msfc-ccd",
                key="msfc_ccd",
                doi="10.5281/zenodo.23090943",
            ),
            aastex.PythonPackage(
                "named-arrays",
                key="named_arrays",
                doi="10.5281/zenodo.23072813",
            ),
            r"NumPy \citep{Harris2020}",
            aastex.PythonPackage("optika", doi="10.5281/zenodo.23074621"),
            aastex.PythonPackage("utu", doi="10.5281/zenodo.23107787"),
        ]
    )
