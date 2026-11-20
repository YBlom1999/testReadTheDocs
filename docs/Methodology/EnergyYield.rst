Energy yield
============

The energy yield calculation is the last step of the modelling framework. It
combines the results of the other models into the electrical output of the
solar cells for every hour of the simulated period:

- the received irradiance from the :doc:`Illumination` model,
- the absorptance of each absorber from the :doc:`Optics` model,
- the module temperature from the :doc:`ThermalModel`, and
- the electrical parameters of the solar cells.

First the photocurrent of each absorber is calculated from the absorbed light.
The electrical model then converts this photocurrent, together with the module
temperature, into the current-voltage characteristics and the maximum power for
every hour. The energy yield follows from the power over time.

.. contents:: On this page
   :local:
   :depth: 2

Overview
--------

The calculation consists of the following steps:

1. The input data is checked, and the absorptance is interpolated to the
   angles and wavelengths of the irradiance data.
2. The short-circuit current density :math:`J_{sc}` is calculated for every
   absorber and every hour.
3. If degradation is switched on, a degradation factor is calculated and
   applied.
4. The electrical model calculates the open-circuit voltage, the fill factor
   and the maximum power point for every hour.
5. The results are returned, and optionally stored so they can be reused.

Input
-----

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Input
     - Description
   * - Irradiance
     - The spectral irradiance on the front (and the rear) of the module,
       resolved in hour, wavelength and angle, and the total irradiance on the
       front. The output of the illumination model.
   * - Optics
     - The absorptance of each layer as a function of angle and wavelength,
       and the indices of the absorber layers. The output of the optical
       model. If the optical model also provides the absorptance for light from
       the rear, the rear side is included.
   * - Electrical parameters
     - The settings of the solar cells: the solver, the configuration, the
       collection efficiency, the resistances, the diode parameters, and the
       temperature coefficients (see :ref:`ey-electrical`).
   * - Module temperature
     - The hourly temperature of the module from the thermal model.
   * - Weather data
     - Used to determine the number of hours of the simulation.

The weather data, the irradiance and the module temperature must all have the
same number of hours.

Photocurrent
------------

Absorptance on the irradiance grid
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The optical model and the illumination model use different grids. Before the
photocurrent is calculated, the absorptance of each absorber is therefore
interpolated linearly to the angle bins and to the wavelengths of the
irradiance data. Outside the range of the optical data, the first or last value
is used.

Short-circuit current density
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The photocurrent follows from the number of absorbed photons. Each absorbed
photon with wavelength :math:`\lambda` has an energy :math:`hc/\lambda`, so the
photon flux is the spectral irradiance multiplied by :math:`\lambda/(hc)`. Every
absorbed photon is assumed to generate one electron, multiplied by the
collection efficiency :math:`CE_k` of absorber :math:`k`. For hour :math:`t`
this gives:

.. math::

   J_{sc,k}(t) = C \cdot CE_k \int \sum_{\theta}
   A_k(\lambda,\theta)\, I_{front}(\lambda,\theta,t)\, \lambda \, d\lambda

with the constant

.. math::

   C = \frac{q}{hc}\cdot 10^{-10}

where :math:`q` is the elementary charge, :math:`h` is the Planck constant and
:math:`c` is the speed of light. The factor :math:`10^{-10}` converts the
wavelength from nm and the current from A/m² to mA/cm², so :math:`J_{sc}` is
given in mA/cm². The sum runs over the angle bins, so the angular dependence of
the absorptance is included.

If the optical model provides the absorptance for light from the rear, the
contribution of the rear is added in the same way with the irradiance on the
rear :math:`I_{back}` and the rear absorptance, which makes the calculation
suitable for bifacial devices.

Integration over the wavelength
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The integral over the wavelength can be evaluated in two ways. The method is
chosen with ``photocurrent_integration`` in the ``electrical`` section:

- ``uniform_bin_sum`` (default): the values are summed and multiplied by the
  wavelength step. This requires a uniform wavelength grid.
- ``trapezoid``: trapezoidal integration, for spectra that are sampled at
  points.

.. _ey-electrical:

Electrical calculation
----------------------

The electrical model calculates the open-circuit voltage :math:`V_{oc}`, the
fill factor, and the current, voltage and power at the maximum power point,
from :math:`J_{sc}` and the temperature of the module. The ``solver`` option
selects between two ways to do this:

- ``analytical``: a diode model that is solved analytically (using the Lambert
  W function). The solar cell is described by its series resistance, shunt
  resistance, saturation current density and ideality factor, and the
  temperature coefficients of :math:`J_{sc}` and :math:`V_{oc}` account for the
  module temperature.
- ``numerical``: the current-voltage curves are calculated with LTspice
  circuits. The circuit that is used is selected with ``mode`` in the
  ``ltspice`` subsection (for example ``2T_n``, ``3T_n`` or a module
  configuration).

The ``configuration`` determines how the absorbers are connected:

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Configuration
     - Calculation
   * - ``2T``
     - Two-terminal tandem. The absorbers are connected in series, so the
       current is limited by the absorber that produces the lowest current:
       :math:`J_{sc} = \min_k J_{sc,k}`. The tandem is calculated with this
       current-matched :math:`J_{sc}`, and the sub-cells are evaluated at
       the same current. The result has an additional entry for the complete
       tandem device.
   * - ``4T``
     - Four-terminal tandem. Each absorber operates independently with its own
       :math:`J_{sc,k}`.
   * - ``3T``
     - Three-terminal tandem. The analytical solver uses the four-terminal
       calculation as an approximation. The numerical solver describes the
       three-terminal circuit.
   * - ``Single``
     - A single solar cell.
   * - ``2T exp``, ``4T exp``
     - A measured current-voltage curve is used instead of a diode model. The
       curve is shifted so that its current at zero voltage equals the
       calculated :math:`J_{sc}`, and the maximum power point is taken from the
       shifted curve. For the two-terminal case the lowest :math:`J_{sc}` is
       used.

Degradation
-----------

The model can include the degradation of the solar cells. It is switched on by
setting ``degradation_type`` to ``combined``, which describes degradation
caused by temperature and by light. The hourly module temperature and the total
irradiance on the front are used to calculate a degradation factor for each
absorber and hour. The activation energies and the other degradation
parameters are given in ``params``.

``degradation_parameter`` selects which property degrades. With ``CE``, the
collection efficiency is degraded, so the degradation factor is multiplied with
:math:`J_{sc}`:

.. math::

   J_{sc,k}(t) \rightarrow J_{sc,k}(t)\, DF_k(t)

The other options (series resistance, shunt resistance and dark current)
require the numerical solver.

Two cases are distinguished. If both the temperature and the irradiance are
constant for all hours, the input is treated as an accelerated test with
constant stress. The hour index then represents the accumulated stress time,
and not a calendar hour. Otherwise, the degradation is calculated for real
weather conditions. A degradation state at the start of the simulation can be
supplied.

Output
------

The result is a dictionary with the following hourly quantities for every
absorber:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Quantity
     - Description
   * - ``Jsc``
     - Short-circuit current density (mA/cm²)
   * - ``Voc``
     - Open-circuit voltage (V)
   * - ``FF``
     - Fill factor
   * - ``JMPP``
     - Current density at the maximum power point
   * - ``VMPP``
     - Voltage at the maximum power point
   * - ``Pmpp``
     - Power at the maximum power point

For the ``2T`` configuration, the arrays contain an extra column for the
complete tandem device, after the columns of the sub-cells.

Because every value belongs to one hour, the energy yield over a period is the
sum of the hourly maximum power:

.. math::

   E = \sum_t P_{mpp}(t)\,\Delta t, \qquad \Delta t = 1\ \mathrm{h}

Storing results
---------------

The calculation can take a long time, especially with the numerical solver. If
``store_results`` in the ``paths`` section is switched on, the results are saved
in the folder ``energy_results``, together with a text database that lists the
settings of each calculation. Before a new calculation is started, the settings
are compared with this database. The comparison includes the irradiance, the
optics, the electrical parameters, the module temperature, the module inputs,
the location and the degradation parameters. If the same calculation was done
before, the saved results are loaded instead. With ``store_results`` switched
off, everything is calculated again.

Input checks
------------

The calculation stops with an error if the number of hours of the weather data,
the irradiance and the module temperature do not match. It returns an empty
result with a warning if:

- the electrical parameters are not defined for the same number of absorbers,
- the number of absorbers in the optics does not match the electrical
  parameters, or
- an experimental configuration (``2T exp`` or ``4T exp``) is selected without
  the measured current-voltage curves.

Assumptions and limitations
---------------------------

- Every absorbed photon generates one electron-hole pair that contributes to
  the current, multiplied by the collection efficiency. The efficiency is
  independent of the wavelength.
- Each hour is calculated as a steady-state situation, using the irradiance and
  the temperature of that hour.
- Every absorber has its own temperature from the thermal model, but the thermal
  model currently gives the same value for all absorbers.
- With the analytical solver, the three-terminal configuration is only an
  approximation, based on the four-terminal calculation.
- With the ``2T`` configuration, the absorbers are assumed to be perfectly
  current-matched, with the lowest current determining the output.