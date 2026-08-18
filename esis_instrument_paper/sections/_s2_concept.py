import aastex

__all__ = [
    "concept",
]


def concept() -> aastex.Section:
    result = aastex.Section("The ESIS Concept")
    result.append(r"""
\ESIS\ and \MOSES\ answer the same question in the same way.
Both disperse the whole field of view without a slit, both record several images of it simultaneously, and both
depend on an inversion to recover a line profile at every point of that field.
Where they differ is in how the projections are arranged, and that difference is the accumulated result of two
\MOSES\ flights.
This section sets out what those flights revealed about the limits of the \MOSES\ design, and how each limit shaped
\ESIS.""")
    result.append(limitations())
    return result


def limitations() -> aastex.Subsection:
    result = aastex.Subsection("Limitations of the MOSES Design")
    result.append(r"""
A single concave grating serves as the imaging element of \MOSES, forming three images on three
\CCDs~\citep{Fox10}, and a flat secondary folds the optical path in half.
One consequence of that arrangement is convenient: with the cameras correctly placed, the undispersed order
can be focused in visible light, so the whole telescope is aligned without a source at the operating wavelength.
The rest of the consequences are constraints.

Because the fold mirror provides no magnification, the instrument cannot be made shorter than half the
\SI{5}{\meter} focal length of the grating~\citep{Fox10,Fox11}.
Dispersion is likewise geometric: it is set by how far apart the cameras sit, so reaching the maximum
\SI{29}{\kilo\meter\per\second} per pixel~\citep{Fox10} means pushing the outboard cameras to the edge of a payload
only \SI{0.56}{\meter} across.
Both constraints act in a single plane, which leaves the cylindrical volume of the payload largely unused
along the orthogonal directions.

That same plane limits how many images can be recorded at all.
Three diffraction orders, $m = -1$, $0$, and $+1$, are as many as the payload will hold, so \MOSES\ measures three
numbers at each point of the field.
Three numbers will not constrain a line profile beyond three degrees of freedom, which in practice means
intensity, Doppler shift, and width~\citep{KankThom01}, and only compact, well isolated features have yielded
more~\citep{Fox10,Rust2019}.
This is the familiar behavior of any tomographic measurement, where the detail recoverable in the object follows
from the number of viewing angles available~\citep{Kak88,Descour97,Hagen08}: finer spectral structure, whether an
additional line in the passband or a higher moment of the profile, requires more projections than \MOSES\ can
provide.

Having only one plane of dispersion also makes the instrument sensitive to the orientation of the scene.
The transition region and corona are threaded by magnetic field, and the emission is drawn out into loops and
filaments along it~\citep{Rosner78,Bonnet80}.
A filament lying nearly perpendicular to the dispersion acts as its own spectrograph slit, and recovering a Doppler
shift reduces to triangulation between the orders~\citep{Fox10,Courrier18}, with sufficiently isolated features
yielding even the splitting of a double-peaked profile~\citep{Rust2019}.
A filament lying nearly parallel to the dispersion yields none of this, and since the field has no globally
preferred direction, which case applies is a matter of where the instrument happens to be pointed.

A single grating must also form all three images at once, which leaves too few degrees of freedom in the optical
prescription to control aberrations in every order.
\MOSES\ flew its first mission slightly defocused~\citep{Rust2019}, which widened the point spread functions to
several pixels and made them differ between orders, the outboard ones elongated along different
axes~\citep{Rust2019,Atwood18}.
Structure introduced by the instrument in this way is difficult to separate from structure in the spectrum, and it
complicates the inversion~\citep{Atwood18,Courrier18}.

Without a field stop, the field of view is defined only by the geometry of the optics, and differs from order to
order and with wavelength.
Light from outside the intended field reaches the detectors, and it is not negligible: comparing synthetic images
against the flight data, \citet{Parker2022moses} attributed roughly a tenth of the undispersed image to more than
ten faint lines in the passband, most of them invisible in the dispersed orders.
An undispersed channel is attractive precisely because it is free of spatial-spectral ambiguity, but that result
shows the ambiguity is replaced by a spectral one.

Finally, the detectors must be read out before they can be exposed again, and the roughly \SI{6}{\second} this
takes~\citep{Fox11} is expensive when a sounding rocket observes for about five minutes in total.
Half of the observing time is spent reading rather than collecting, and the exposures that remain must be traded
against one another, which is why \MOSES\ flew a sequence ranging from a quarter of a second to
\SI{24}{\second}.

Taken together, our experience with \MOSES\ identifies eight limitations of the design:
\begin{enumerate}
    \item inefficient use of the payload volume \label{item-length}
    \item dispersion constrained by the payload diameter \label{item-disp}
    \item too few dispersed images \label{item-orders}
    \item a single plane of dispersion \label{item-plane}
    \item insufficient control of aberrations \label{item-psf}
    \item a field of view which is neither sharply defined nor the same in every order \label{item-fov}
    \item spectral contamination from outside the intended field \label{item-contamination}
    \item an observing duty cycle of only half the flight \label{item-cadence}
\end{enumerate}
Each of these shaped the design of \ESIS.""")
    return result
