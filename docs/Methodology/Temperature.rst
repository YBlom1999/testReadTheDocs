Thermal model
=============

The thermal model calculates the temperature of the module for every hour of
the simulated period. The temperature is needed by the electrical model,
because the performance of a solar cell depends on its operating temperature.

The model uses the temperature models of the Python package ``pvlib``. It
combines the irradiance that is received by the front of the module (from the
:doc:`Illumination` model) with the ambient temperature and the wind speed
from the weather data. The temperature model is selected with ``thermalModel``
in the ``thermal`` section of the configuration file.

.. contents:: On this page
   :local:
   :depth: 2

Overview
--------

The calculation consists of three steps:

1. The weather data provides the ambient temperature :math:`T_a` and the wind
   speed :math:`v` for every hour.
2. The irradiance :math:`G` on the module is obtained from the illumination
   model.
3. A temperature model converts :math:`T_a`, :math:`v` and :math:`G` into the
   module temperature :math:`T`.

Three temperature models are available.

.. list-table::
   :header-rows: 1
   :widths: 15 45 40

   * - Model
     - Description
     - Input
   * - ``Ross``
     - Simple model, where the temperature rise is proportional to the
       irradiance.
     - Irradiance, ambient temperature, NOCT
   * - ``SAPM``
     - Empirical Sandia model with parameters for four mounting
       configurations. Includes the cooling by wind.
     - Irradiance, ambient temperature, wind speed, mounting configuration
   * - ``Fuentes``
     - Heat-balance model that includes the geometry of the module and the
       thermal history.
     - Irradiance, ambient temperature, wind speed, module geometry, NOCT,
       emissivity

Input
-----

Weather data
~~~~~~~~~~~~

The ambient dry-bulb temperature (°C) and the wind speed (m/s) are taken from
the hourly weather data. The ``Ross`` model does not use the wind speed.

Irradiance
~~~~~~~~~~

The source of the irradiance is defined as  ``projected_front`` (default): the 
spectral irradiance on the front side of the module is summed over all angle bins 
and integrated over the wavelength:

  .. math::

     G(t) = \int \sum_{k} I_{front}(\lambda,\theta_k,t)\, d\lambda

The total irradiance that reaches the front is used. The reflected part is
not subtracted, so the irradiance is not corrected for the absorption of the
device.

Temperature models
------------------

Ross model
~~~~~~~~~~

In the Ross model, the temperature difference between the cell and the air is
proportional to the irradiance:

.. math::

   T = T_a + \frac{NOCT - 20}{800}\, G

Here :math:`G` is in W/m² and :math:`T` and :math:`T_a` are in °C. The
nominal operating cell temperature (NOCT) is the cell temperature at an
irradiance of 800 W/m², an ambient temperature of 20 °C and a wind speed of
1 m/s. The only parameter is ``noct``. The model assumes a constant wind speed
of 1 m/s, so it does not respond to changes in the wind.

SAPM model
~~~~~~~~~~

The Sandia Array Performance Model (SAPM) first calculates the temperature of
the back surface of the module, which depends on the irradiance and the wind
speed, and then adds a correction for the temperature difference between the
back surface and the cell:

.. math::

   T_{mod} = G\,\exp(a + b\,v) + T_a, \qquad
   T = T_{mod} + \frac{G}{G_0}\,\Delta T

where :math:`v` is the wind speed, :math:`G_0 = 1000` W/m², and :math:`a`,
:math:`b` and :math:`\Delta T` are parameters that depend on the way the module
is mounted. The mounting configuration is chosen with ``SAPM_type``:

.. list-table::
   :header-rows: 1
   :widths: 10 40 15 15 20

   * - ``SAPM_type``
     - Configuration
     - :math:`a`
     - :math:`b`
     - :math:`\Delta T` (K)
   * - 0
     - Open rack, glass/glass
     - -3.47
     - -0.0594
     - 3
   * - 1
     - Close mount, glass/glass
     - -2.98
     - -0.0471
     - 1
   * - 2
     - Open rack, glass/polymer
     - -3.56
     - -0.0750
     - 3
   * - 3
     - Insulated back, glass/polymer
     - -2.81
     - -0.0455
     - 0

The parameters are the standard values that are provided by ``pvlib``. A
module on an open rack is cooled well and gets the lowest temperature. The
temperature of a module with an insulated back is the highest, because there
is no airflow along the rear surface.

Fuentes model
~~~~~~~~~~~~~

The Fuentes model is a heat-balance model, which is also used in PVWatts. It
describes the heat that is absorbed from the irradiance and the heat that is
lost by radiation and by convection to the air, which depends on the wind
speed, the geometry of the module and its tilt. Because the model includes
the heat capacity of the module, the temperature depends on the conditions in
the previous hours.

The following parameters are needed:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Parameter
     - Description
   * - ``module_height``
     - Height of the module above the ground (m)
   * - ``module_width``, ``module_length``
     - Dimensions of the module (m)
   * - ``module_tilt_deg``
     - Tilt of the module from horizontal (°)
   * - ``noct``
     - Installed nominal operating cell temperature (°C)
   * - ``fuentes_module_emissivity``
     - Emissivity of the module (-)

All other parameters of the model, such as the absorption and the height of the
wind measurement, keep the default values of ``pvlib``.

Because the temperature depends on the history, this model needs a continuous
series of hourly values, with at least two rows. The calculation uses the time
elapsed between the rows, and not the date. If the simulation is run for
separate periods of time, the temperature in the first hours is influenced by
the starting conditions. The tilt that is specified here is separate from the
tilt in the ``illumination`` section, so both values should be set
consistently.

Output
------

The result is the temperature of the module in °C for every hour and every
absorber, as an array of shape (hours, absorbers). The model uses a
single-layer description, so all absorbers of the device have the same
temperature. This array is the input of the electrical model.

The temperature that is returned is the cell temperature. For the ``Ross`` and
``Fuentes`` models, the module temperature and the cell temperature are equal.
The ``SAPM`` model also calculates the temperature of the back surface of the
module, but only the cell temperature is passed on.

Configuration
-------------

An example of the ``thermal`` section in the configuration file:

.. code-block:: yaml

   thermal:
      thermalModel: 'SAPM' # Options are 'SAPM','Fuentes','Ross'
      SAPM_type: 0
      noct: 48
      irradiance_source: 'projected_front'

For the ``Ross`` model only ``noct`` is used, for ``SAPM`` only ``SAPM_type``
is used, and for ``Fuentes`` the geometry parameters from the table above are
required as well.

Assumptions and limitations
---------------------------

- The temperature is calculated from the irradiance that reaches the front of
  the module. The absorptance of the device from the optical model is not
  used, so the heat that is generated in the device is not calculated from the
  absorbed light. The irradiance on the rear side is not included.
- The ``Ross`` and ``SAPM`` models assume steady-state conditions: the
  temperature responds immediately to a change of the irradiance. Only the
  ``Fuentes`` model includes thermal inertia.
- All absorbers have the same temperature, and temperature differences within
  the module are not described.