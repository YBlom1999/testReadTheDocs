Illumination model
==================

The illumination model calculates the irradiance that is received by the
front and the rear side of the module. It takes the spectral irradiance on a
horizontal surface (see :doc:`SpectralIrradiance`), the sun position from the
weather data, and the module parameters (tilt, azimuth, tracking, albedo, row
spacing) as input. For every hour it returns the received irradiance, resolved
in wavelength and in angle of incidence, separately for the front and the
rear side. These results are used by the optical model (angular and spectral
information), and by the thermal and electrical models (total received
irradiance).

.. contents:: On this page
   :local:
   :depth: 2

Overview
--------

Two illumination models are available. The model is selected with
``IlluminationModel`` in the ``illumination`` section of the configuration
file.

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * -
     - ``Simplified``
     - ``Viewfactor``
   * - Approach
     - Angular decomposition into direct, diffuse and ground-reflected light
     - View-factor simulation of a periodic array of module rows
   * - Inter-row shading
     - Not included
     - Included
   * - Mounting height and row spacing
     - Not used
     - Used
   * - Tracking
     - Fixed tilt and several tracking modes
     - Fixed orientation only
   * - Angular resolution
     - 90 angle bins of 1°
     - 20 bins of equal solid angle (and 36 azimuth bins)
   * - Speed
     - Fast
     - Slower

Both models split the incoming light into the same three contributions:

- **Direct light** from the sun.
- **Diffuse light** from the sky.
- **Ground-reflected light**, which depends on the albedo of the ground.

Each contribution is calculated for the front and for the rear side of the
module. Light that reaches the rear side comes from the sky behind the module
and from the ground, which makes the model suitable for bifacial modules.

Input
-----

Spectral irradiance
~~~~~~~~~~~~~~~~~~~

The spectral direct horizontal and diffuse horizontal irradiance for every
hour, on a wavelength grid. This is the output of the spectral irradiance
model, which includes the effect of clouds.

The wavelength grid can be reduced with ``spectral_sampling``:

- ``every_tenth`` (default): every tenth wavelength of the input is used.
- ``full_300_1200_1nm``: all wavelengths from 300 to 1200 nm at 1 nm
  resolution are used. This requires 1 nm input spectra and the
  ``Simplified`` model.

Weather data
~~~~~~~~~~~~

From the hourly weather data (TMY3 or CAMS) the following quantities are used:

- the solar zenith and azimuth angle,
- for the ``Viewfactor`` model also the direct normal irradiance (DNI), the
  diffuse horizontal irradiance (DHI), the ambient temperature and the wind
  speed.

Module and ground
~~~~~~~~~~~~~~~~~

- ``module_tilt`` and ``module_azimuth``: orientation of the module.
- ``albedoMaterial``: material of the ground, which determines the spectral
  albedo :math:`\rho(\lambda)`.
- ``tracking``: tracking mode (``Simplified`` model only).
- ``module_spacing``: distance between the module rows (``Viewfactor`` model).
- ``solar_angle_sampling``: set to ``hour_end`` to use the average of the sun
  position at the beginning and the end of each hour, instead of the value at
  the time stamp.

Simplified model
----------------

The simplified model treats the sky as a hemisphere of diffuse light plus one
direct beam, and calculates how much of each reaches the two sides of the
module. It does not include the mounting height or shading by neighbouring
module rows.

Light components
~~~~~~~~~~~~~~~~

The spectral irradiance on the horizontal plane is converted into radiances.
The direct normal irradiance follows from the direct horizontal irradiance and
the solar zenith angle :math:`\theta_S`, and is set to zero when the sun is
below the horizon:

.. math::

   I_{dir,N}(\lambda) = \frac{I_{dir,H}(\lambda)}{\cos\theta_S}

The sky is assumed to be an isotropic diffuse source, and the ground is
assumed to reflect light equally in all directions (Lambertian). This gives
the diffuse and ground-reflected radiance:

.. math::

   L_{dif}(\lambda) = \frac{I_{dif,H}(\lambda)}{\pi}, \qquad
   L_{alb}(\lambda) = \rho(\lambda)\,
   \frac{I_{dir,H}(\lambda) + I_{dif,H}(\lambda)}{\pi}

Which directions see the sky
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The orientation of the module (tilt, azimuth, and for tracking modules the
position of the hour) determines which directions in front of the module see
the sky and which see the ground. This is stored in an illumination map
:math:`G(\theta,\varphi)` on a grid of 1°, where :math:`\theta` is the angle
from the module normal and :math:`\varphi` the azimuth in the frame of the
module. :math:`G = 1` for directions that point to the sky and :math:`G = 0`
for directions that point to the ground.

The rear side looks in the opposite direction, so a direction that sees the
sky from the front sees the ground from the rear, and the other way around.
The map for the rear side is therefore :math:`1 - G`.

The sun position is rotated into the frame of the module as well. The result
is the angle of incidence of the direct beam on the module,
:math:`\theta'_S`.

Direct light
~~~~~~~~~~~~

The direct beam reaches the front when the sun is above the horizon and in
front of the module (:math:`G = 1` for the sun direction). The light is placed
in the angle bin of :math:`\theta'_S` and weighted with the cosine of the
angle of incidence:

.. math::

   I_{dir,front}(\lambda, \theta'_S) = I_{dir,N}(\lambda)\cos\theta'_S

When the sun is above the horizon but behind the module, the beam hits the
rear side, in the bin of the angle of incidence measured from the rear normal.
Otherwise, the direct contribution is zero.

Diffuse and ground-reflected light
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For every angle bin :math:`\theta_k` (1° steps from 0° to 89°) the part of the
hemisphere that sees the sky is integrated, weighted with
:math:`\sin\theta\cos\theta` (the projection onto the module):

.. math::

   w_{sky}(\theta_k) = \sin\theta_k\cos\theta_k\,\Delta\theta\,\Delta\varphi
   \sum_{\varphi} G(\theta_k,\varphi), \qquad
   w_{gr}(\theta_k) = \sin\theta_k\cos\theta_k\,\Delta\theta\,\Delta\varphi
   \sum_{\varphi} \bigl(1 - G(\theta_k,\varphi)\bigr)

The front receives diffuse light from the sky and reflected light from the
ground. The rear side receives the same with the roles of sky and ground
exchanged:

.. math::

   I_{front}(\lambda,\theta_k) = I_{dir,front}
   + L_{dif}(\lambda)\,w_{sky}(\theta_k)
   + L_{alb}(\lambda)\,w_{gr}(\theta_k)

.. math::

   I_{back}(\lambda,\theta_k) = I_{dir,back}
   + L_{dif}(\lambda)\,w_{gr}(\theta_k)
   + L_{alb}(\lambda)\,w_{sky}(\theta_k)

The total (broadband) irradiance on each side is obtained by integrating over
the wavelength and summing over all angle bins.

Tracking
~~~~~~~~

For a tracking system, the orientation of the module is recalculated for
every hour, and the illumination map and the rotation of the sun position are
updated accordingly. The following modes are implemented. When the sun is
below the horizon, the module returns to a horizontal position.

.. list-table::
   :header-rows: 1
   :widths: 10 90

   * - Mode
     - Behaviour
   * - 0
     - Fixed tilt and azimuth.
   * - 1
     - Single-axis tracking around a horizontal axis. The tilt follows the
       east-west movement of the sun.
   * - 2
     - Two-axis tracking. The module always faces the sun.
   * - 3
     - The module follows the azimuth of the sun at a fixed tilt.
   * - 4
     - Seesaw tilt tracking.
   * - 5
     - Partial tracking. The tilt follows the zenith angle of the sun,
       multiplied by a factor that depends on the ratio between direct and
       diffuse light. The module faces the sun more when the share of direct
       light is higher.

Output
~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - Quantity
     - Shape
     - Description
   * - ``frontSpec``
     - (hours, wavelengths, 90)
     - Spectral irradiance on the front per angle bin
   * - ``backSpec``
     - (hours, wavelengths, 90)
     - Spectral irradiance on the rear per angle bin
   * - ``frontAbs``
     - (hours,)
     - Total irradiance on the front (W/m²)
   * - ``backAbs``
     - (hours,)
     - Total irradiance on the rear (W/m²)
   * - ``wavelengths``
     - (wavelengths,)
     - Wavelength grid (nm)
   * - ``AOI``
     - (90,)
     - Angle-of-incidence grid (rad)

If the thermal model is set to use ``legacy_direct_diffuse`` as irradiance
source, the output also contains ``legacy_noct_irradiance``, a broadband
irradiance for the temperature calculation.

View-factor model
-----------------

The view-factor model describes the module as part of an infinite array of
parallel rows. Because it calculates which parts of the sky and the ground
each point on the module can see, it includes the shading by neighbouring
rows, and the mounting height is taken into account. It is therefore the
more detailed option for bifacial modules. It only supports a fixed
orientation.

Geometry
~~~~~~~~

The model is a two-dimensional cross-section perpendicular to the rows. The
geometry is defined by:

- the module length :math:`L` (default 1.96 m),
- the tilt and the azimuth of the module,
- the mounting height :math:`H`: the distance from the lowest point of the
  module to the ground (default 0.5 m),
- the row spacing :math:`d`: the distance between the lowest points of two
  adjacent rows (``module_spacing``).

The module is divided into 12 positions along its length, and the ground is
divided into 101 points within one period of the array. The results are
reported for one position near the middle of the module (the sixth of the
twelve). A module tilt of 0° is not possible in this model, and is replaced by
0.5°.

Light components
~~~~~~~~~~~~~~~~

The irradiance is calculated for four contributions on each side of the
module, and the total is their sum:

1. **Direct sky light.** The cosine of the angle between the sun and the
   module normal gives the irradiance on the front (positive) or rear
   (negative) side. The part of the module that is in the shadow of the row in
   front is set to zero. The length of the shadow follows from the geometry of
   the rows and the position of the sun.

2. **Diffuse sky light.** For each position on the module, a view factor
   gives the fraction of the sky hemisphere that is visible, which is limited
   by the neighbouring rows. This view factor depends only on the geometry,
   and not on the position of the sun. It is multiplied by the DHI.

3. **Direct light on the ground.** The shadow of the module on the ground is
   calculated from the sun position and repeated periodically for the whole
   array. Ground points outside the shadow receive the direct light, and
   reflect it in all directions (Lambertian) with a radiance of
   :math:`\cos\theta_S/\pi` per unit of DNI.

4. **Diffuse light on the ground.** At each ground point the sky view factor
   is calculated by adding the angular windows between all module rows that are
   visible from that point. As for the direct light, the result is divided by
   :math:`\pi` to obtain the radiance.

Ground-reflected light on the module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For each position on the module, a matrix describes which ground points are
visible and from which angle. This visible region is limited by the lowest
point of the next row. The matrix is calculated separately for the front and
the rear side. Multiplying the ground radiance (direct and diffuse) with this
matrix and summing over the ground points gives the ground-reflected light on
each side. This is multiplied by the albedo.

Angular and spectral resolution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The optical model needs to know from which angle the light arrives. The
contributions are therefore distributed over angle bins relative to the
normal of the module:

- 20 zenith bins of equal solid angle (the bin edges are equally spaced in
  :math:`\cos\theta`), and
- 36 azimuth bins of 10°.

Direct light is placed in the bin of the sun position, and for light on the
rear side the zenith angle is mirrored. The diffuse and ground-reflected light
is spread over the bins following the angular distribution of the visible sky
and ground.

The spectral information is added afterwards. The spectra of the direct and
diffuse irradiance are normalised so that they integrate to one. The
irradiance of each component (summed over the azimuth bins) is then multiplied
by the matching normalised spectrum: the DNI spectrum for direct light, and the
DHI spectrum for diffuse light. For ground-reflected light, both spectra are
used (direct and diffuse), and the result is multiplied by the spectral albedo
:math:`\rho(\lambda)`:

.. math::

   I_{side}(\lambda,\theta_k) = I_{sky,dir} \, s_{DNI}(\lambda)
   + I_{sky,dif} \, s_{DHI}(\lambda)
   + \rho(\lambda)\bigl[I_{gr,dir}\, s_{DNI}(\lambda)
   + I_{gr,dif}\, s_{DHI}(\lambda)\bigr]

Here :math:`s_{DNI}` and :math:`s_{DHI}` are the normalised spectra, and
"side" is either front or rear.

Output
~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 30 45

   * - Quantity
     - Shape
     - Description
   * - ``frontSpec``
     - (hours, wavelengths, 20)
     - Spectral irradiance on the front per zenith bin
   * - ``backSpec``
     - (hours, wavelengths, 20)
     - Spectral irradiance on the rear per zenith bin
   * - ``frontAbs``
     - (hours, 20, 36)
     - Broadband irradiance on the front per angle bin
   * - ``backAbs``
     - (hours, 20, 36)
     - Broadband irradiance on the rear per angle bin
   * - ``wavelengths``
     - (wavelengths,)
     - Wavelength grid (nm)
   * - ``AOI``
     - (20,)
     - Lower edges of the zenith bins (rad)

Note that ``frontAbs`` and ``backAbs`` have a different shape than in the
simplified model. Here they are resolved in angle, and the total irradiance is
obtained by summing over the angle bins.

Assumptions and limitations
---------------------------

- The sky is treated as an isotropic diffuse source, and the ground as a
  Lambertian reflector. Anisotropic effects such as circumsolar or horizon
  brightening are not included.
- In the simplified model, the mounting height, the row spacing and the
  shading between rows are not taken into account, so the rear-side
  irradiance may be overestimated for dense arrays.
- The view-factor model is a two-dimensional model of infinitely long rows, so
  edge effects at the ends of the rows are not included.
- The view-factor model uses fixed module length and mounting height (1.96 m
  and 0.5 m) unless these are changed in the code, and does not support
  tracking.