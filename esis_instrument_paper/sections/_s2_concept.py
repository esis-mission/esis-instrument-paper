import aastex

__all__ = [
    "concept",
]


def concept() -> aastex.Section:
    result = aastex.Section(aastex.NoEscape(r"The \ESIS\ Concept"))
    result.append(
        r"""
A primary goal of the \ESIS\ instrument is to improve upon the imaging spectroscopy demonstrated by \MOSES.  
Therefore, the design of the new instrument draws heavily from experiences and lessons learned through two flights of the \MOSES\ instrument.
\ESIS\ and \MOSES\ are both \CTIS\ instruments.
As such, both produce \sout{dispersed images} \roy{overlappograms} of a narrow portion of the solar spectrum, with the goal of enabling the reconstruction of a spectral line profile at every point in the field of view.
The similarities end there, however, as the optical layout of \ESIS\ differs significantly from that of \MOSES.
In this section, we detail some difficulties and limitations encountered with \MOSES, then describe how the new design of \ESIS\ addresses these issues."""
    )

    subsection_limitations = aastex.Subsection(
        aastex.NoEscape(r"Limitations of the \MOSES\ Design")
    )
    subsection_limitations.append(
        r"""
The \MOSES\ design features a single concave diffraction grating forming images on three \CCD\ 
detectors~\citep{Fox10} (Figure~\ref{fig:mosesSchematic}). 
The optical path is folded in half by a single flat secondary mirror (omitted in Figure~\ref{fig:mosesSchematic}).
Provided that the three cameras are positioned correctly, this arrangement allows the entire telescope to be brought 
into focus using only the central (undispersed) order and a visible light source.
Unfortunately this design uses volume inefficiently for two reasons.
First, the lack of magnification by the secondary mirror limits the folded length of the entire telescope to be no less 
than half of the \SI{5}{\meter} focal length of the grating~\citep{Fox10,Fox11}.
Second, the resolving power of the instrument is limited by the ratio of camera separation to pixel size.
To achieve the maximum dispersion of \mosesDispersionDoppler~\citep{Fox10}, the outboard orders are imaged as 
far apart as possible in the $\sim\text{\skinDiameter}$ diameter envelope of the rocket payload.
This planar arrangement leaves much unused space in the cylindrical volume of the payload."""
    )

    # TODO: the MOSES schematic figure goes here, once it has been
    # rebuilt on the current `esis` and `optika` model.

    subsection_limitations.append(r"""
Furthermore, the monolithic secondary, though it confers the focus advantage noted above, does not 
allow efficient placement of the $m=\pm1$ \CCDs.  
For all practical purposes, the payload can only accommodate three diffraction orders ($m=-1, 0, +1$).
Therefore, \textit{\MOSES\ can only collect, at most, three pieces of information at each point in the field of view.}
From this, it is not reasonable to expect the reconstruction of more than three degrees of freedom for each spectral line, 
except in the case very compact, isolated features such as those described by \citet{Fox10} and \citet{Rust17}.
Consequently, it is a reasonable approximation to say that \MOSES\ is sensitive primarily to spectral line intensities, 
shifts, and widths \citep{KankThom01}.
With any tomographic apparatus, the degree of detail that can be resolved in the object depends critically on the 
number of viewing angles~\citep{Kak88,Descour97,Hagen08}.
So it is with the spectrum we observe with \MOSES: more dispersed images are required to confer sensitivity to finer 
spectral details such as higher moments of the spectral line shape.

A related issue stems from the use of a single dispersion plane.
Since the solar corona and transition region are structured by magnetic fields, the scene tends to be dominated by 
\sout{field aligned} \roy{field-aligned} structures such as loops~\citep{Rosner78,Bonnet80}.
When the \MOSES\ dispersion direction happens to be aligned nearly perpendicular to the magnetic field, filamentary 
structures on the transition region serve almost as spectrograph slits unto themselves.
The estimation of Doppler shifts then becomes a simple act of triangulation, and broadenings are also readily 
diagnosed~\citep{Fox10,Courrier18}.
A double-peaked profile can also be observed with sufficiently isolated features~\citep{Rust17}.
Unfortunately, solar magnetic fields in the transition region are quite complex and do not have a global preferred 
direction.
In cases where the field is nearly parallel to the instrument dispersion, spectral shifts and broadenings are not 
readily apparent.

The single diffraction grating also leads to a compromise in the optical performance of the instrument.
Since the \MOSES\ grating forms images in three orders simultaneously, there aren't enough degrees of freedom in the 
optical system to control aberrations in all three spectral orders.  
During the first mission, \MOSES\ was flown with a small amount of defocus~\citep{Rust17}, which exacerbated the 
inter-order \PSF\ variation and caused the individual \PSFs\ to span several 
pixels~\citep{Rust17,Atwood18}. 
The outboard \PSFs\ were elongated, with their major exes at different angles.
This resulted in spurious spectral features that require additional consideration~\citep{Atwood18} and further increase 
the complexity of the inversion process~\citep{Rust17,Courrier18}. 

As \MOSES\ lacks a field stop, it is possible for the grating to image off-band radiation on the detector from solar 
features that lie outside the intended \FOV. 
Although the intensity of this off-band radiation is relatively low, it is not negligible.
\citet{Parker2022} compared synthetic \MOSES\ images to the real data and found that approximately 
ten percent of the intensity in the zeroth order image originated from more than ten dim lines in the \MOSES\ passband, 
most of them are too faint to be visible in the dispersed images.  
This study revealed that an undispersed ($m=0$) channel, although attractive due to its lack of spatial-spectral 
ambiguity, is of limited utility due to spectral contamination.
Moreover the \FOV\ should be clearly defined, and the same, for each image so that the spectral and spatial content of 
the image is clearly defined.

Finally, the exposure cadence of \MOSES\ is hindered by a $\sim$\SI{6}{\second} readout time for the \CCDs~\citep{
Fox11}. 
The observing interval for a solar sounding rocket flight is typically about five minutes. 
Consequently, every second of observing time is precious, both to achieve adequate exposure time and to catch the 
full development of dynamical phenomena. 
The \MOSES\ observing duty cycle is $\sim$\SI{50}{\percent} since it is limited by the readout time of its \CCDs. 
Thus, valuable observing time is lost. The readout data gap compelled us to develop a sequence with exposures ranging 
from $0.25$-\SI{24}{\second}, a careful trade-off between deep and fast exposures. 

In summary, our experience leads us to conclude that the \MOSES\ design has the following primary limitations:
\begin{enumerate}
    \item inefficient use of volume \label{item-length} %(x and y direction)
    \item dispersion constrained by payload dimensions \label{item-disp_con}
    \item too few dispersed images (orders) \label{item-orders}
    \item single dispersion plane \label{item-dispersion}
    \item lack of aberration control \label{item-PSF}
    \item poorly-defined and wavelength dependent \FOV\ \label{item-FOV}
    \item spectral contamination
    \item low duty cycle \label{item-CAD}
\end{enumerate}
In designing \ESIS, we have sought to improve upon each of these points.""")
    result.append(subsection_limitations)

    return result
