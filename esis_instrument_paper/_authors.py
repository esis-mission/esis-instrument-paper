import aastex

__all__ = [
    "authors",
]


def authors() -> list[aastex.Author]:
    """
    A list of the authors of this article and their affiliations.
    """

    msu = aastex.Affiliation(
        "Montana State University, "
        "Department of Physics, "
        "P.O. Box 173840, "
        "Bozeman, MT 59717, USA"
    )
    msfc = aastex.Affiliation(
        "NASA Marshall Space Flight Center, " "Huntsville, AL 35812, USA"
    )
    gsfc = aastex.Affiliation(
        "NASA Goddard Space Flight Center, " "Greenbelt, MD 20771, USA"
    )
    lbnl = aastex.Affiliation(
        "Lawrence Berkeley National Laboratory, "
        "1 Cyclotron Road, Berkeley, CA 94720, USA"
    )
    rxo = aastex.Affiliation(
        "Reflective X-ray Optics LLC, "
        "425 Riverside Dr., #16G, New York, NY 10025, USA"
    )

    return [
        aastex.Author(
            name="Roy T. Smart",
            affiliation=msu,
            orcid="0000-0002-9997-5515",
            email="roytsmart@gmail.com",
            corresponding=True,
        ),
        aastex.Author(
            name="Hans T. Courrier",
            affiliation=msu,
        ),
        aastex.Author(
            name="Jacob D. Parker",
            affiliation=gsfc,
            orcid="0000-0001-8732-8284",
        ),
        aastex.Author(
            name="Charles C. Kankelborg",
            affiliation=msu,
            orcid="0000-0002-1992-7469",
        ),
        aastex.Author(
            name="Amy R. Winebarger",
            affiliation=msfc,
            orcid="0000-0002-5608-531X",
        ),
        aastex.Author(
            name="Ken Kobayashi",
            affiliation=msfc,
            orcid="0000-0003-1057-7113",
        ),
        aastex.Author(
            name="Brent Beabout",
            affiliation=msfc,
        ),
        aastex.Author(
            name="Dyana Beabout",
            affiliation=msfc,
        ),
        aastex.Author(
            name="Ben Carrol",
            affiliation=msu,
        ),
        aastex.Author(
            name="Jonathan Cirtain",
            affiliation=msfc,
        ),
        aastex.Author(
            name="James A. Duffy",
            affiliation=msfc,
        ),
        aastex.Author(
            name="Eric Gullikson",
            affiliation=lbnl,
            orcid="0000-0003-0337-7674",
        ),
        aastex.Author(
            name="Micah Johnson",
            affiliation=msu,
        ),
        aastex.Author(
            name="Laurel Rachmeler",
            affiliation=msfc,
            orcid="0000-0002-3770-009X",
        ),
        aastex.Author(
            name="Larry Springer",
            affiliation=msu,
        ),
        aastex.Author(
            name="David L. Windt",
            affiliation=rxo,
            orcid="0000-0001-9084-2516",
        ),
    ]
