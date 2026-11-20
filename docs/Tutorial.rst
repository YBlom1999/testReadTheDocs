Tutorial
========

This page explains how you can run a simulation. It assumes
the package is already installed. If not, see :doc:`installation`.

.. contents:: On this page
   :local:
   :depth: 2

Run a simulation
----------------

EYCalcPlus can be run from a python console or from the command line.
For both approaches, the script ``run_config.py`` should be used. It reads
the settings from the YAML configuration file described in the next section.

.. code-block:: console

   .venv\Scripts\python.exe run_config.py

Which settings are used for a run is determined by a *profile*. Profiles are
predefined sets of settings that can be defined in the YAML file (see
:ref:`profiles`). The profile that is used is selected with
``default_profile`` in the ``run`` section.

Additional arguments
~~~

Write something about the arguments

Config file
-----------

The YAML configuration file determines all choices of a simulation. It is
divided into sections, where each section controls one part of the modelling
framework: which data is used, how the optics, illumination, thermal and
electrical models behave, and which results are exported. The sections are
described one by one below.

run
~~~

The ``run`` section selects which profile is used by default. The profiles
themselves are defined at the end of the file.

.. code-block:: yaml

   run:
      default_profile: "fixture_hour" # Tracked Phoenix hour; use phoenix for a local full-year run.

results_basket
~~~~~~~~~~~~~~

The ``results_basket`` section determines which results are exported. A set
of default results is always calculated (listed in the comments). Additional
outputs, such as hourly values or spectral data, can be added by setting the
corresponding flag to ``true``. The name of the results file can also be set
here.

.. code-block:: yaml

   results_basket:
      #The default values in the result are:
         #Total energy yield
         #Maximum output power
         #Total illumination front
         #Total illumination rear
         #Mean temperature
         #Maximum temperature
      #Select additional outputs by setting flags to 'true'
      exportHourlyIVchar: false #Hourly values of IV characteristics (Jsc, Voc, FF, Pmpp)
      exportHourlyIlluminationFront: false #Hourly values of absolute illumination on the front
      exportHourlyIlluminationBack: false #Hourly values of absolute illumination on the back
      exportHourlySpecIlluminationFront: false #Hourly values of spectral illumination on the front
      exportHourlySpecIlluminationRBack: false #Hourly values of spectral illumination on the back
      exportHourlySpecIrradiance: false #Hourly values of the spectral irradiance (DNI, DHI)
      exportHourlyTemperature: false #Hourly values of the module temperature
      exportAbsorptance: false #Export spectral absorptance (including reflectance and transmission)
      
      filenameResults: 'Timestamp' #Provide name for results file, 'Timestamp' leads to name of date+time  

paths
~~~~~

The ``paths`` section specifies where input files are located (refractive
index data, layer structures, SMARTS and spectral files) and where results
are stored. With ``store_results`` the results of the optical and energy
yield calculations can be saved and reused instead of calculated again.

.. code-block:: yaml

   paths:
      refractive_index: "_RefractiveIndexLib.xlsx" # Optical n/k workbook, tracked in Git.
      optics_results: "Results_Optics" # Optical cache directory if result storage is enabled.
      layerStructure: "Optics/LayerStructures"
      smartsLocation: "SpectralIrradiance\\Code_SMARTS_295_PC"
      spectralFiles: "SpectralIrradiance\\Spectra_"
      energy_results: "Results_EY" # Energy-yield cache directory if result storage is enabled.
      store_results: false # true: use module result databases; false: calculate afresh.

irradiance
~~~~~~~~~~

The ``irradiance`` section defines where the weather and spectral irradiance
data come from. With ``source`` the data can be read from an existing file,
or generated from a TMY3 or CAMS data set using SMARTS. The remaining
settings identify the location and, optionally, check the input files. The
``cams`` subsection is only needed when the data is generated from CAMS files.

.. code-block:: yaml

   irradiance:
      # hourly_file: one HDF5 file with weather, spectra, and hourly timestamps.
      # cached_tmy3: load a matching pair of precomputed Phoenix-style HDF5 files.
      # tmy3_generate: generate HDF5 files from a local TMY3 CSV using SMARTS.
      # cams_generate: generate HDF5 files from configured CAMS files using SMARTS.
      source: "cached_tmy3" # Profiles select the input for each run.
      location_code: "722780TYA" # Location/file identifier for generated or cached data.
      alias: "Phoenix" # Human-readable location label passed to EnergyYield.
      spectra_dir: "SpectralIrradiance/Spectra_722780TYA_Phoenix" # Input folder for cached_tmy3.
      # For cached_tmy3, set expected SHA-256 values to reject changed input files.
      spectra_sha256: "" # Empty string disables this check for a custom data set.
      weather_sha256: "" # Empty string disables this check for a custom data set.
      data_source: 'csv'
      # input_file: "inputs/hourly.h5" # Required when source is hourly_file.
      # input_start: "2021-01-01T00:00:00+00:00" # For an H5 file without timestamps.
      # timezone: "Europe/Berlin" # Local day/month selection on an hourly file.
      # tmy_utc_offset_hours: -7 # Fixed standard-time offset for TMY calendar selection.

      cams:
         # Required only for cams_generate. Paths can be absolute or repository-relative.
         csv_minute: "" # CAMS minute file with atmospheric and cloud fields.
         csv_hourly: "" # CAMS hourly broadband irradiance file.
         nc_surface: "" # EAC4 surface NetCDF file.
         nc_pressure: "" # EAC4 pressure-level NetCDF file.
         latitude_deg: 0.0 # Target site latitude; set for cams_generate.
         longitude_deg: 0.0 # Target site longitude; set for cams_generate.
         timezone: "" # IANA zone such as Europe/Berlin; required for cams_generate.

optics
~~~~~~

The ``optics`` section controls the optical simulation. It sets the
polarization, the angular resolution, the simulated wavelength range and
the layer stack file that describes the device architecture.

.. code-block:: yaml

   optics:
      polarization: "mixed" # mixed: average TE/TM; TE: electric transverse; TM: magnetic transverse.
      angle_resolution_deg: 10 # Optical angle step; 0 computes normal incidence only; maximum 10.
      wavelength_start_nm: 300 # First simulated optical wavelength, nanometres.
      wavelength_stop_nm: 1200 # Last simulated optical wavelength, nanometres, inclusive.
      wavelength_step_nm: 25 # Optical wavelength spacing, nanometres.
      
      stackFile: 'TandemReference.yaml'

illumination
~~~~~~~~~~~~

The ``illumination`` section describes the module and its surroundings: the
albedo of the ground, the tracking type, and the tilt, spacing and azimuth
of the module. It also selects the illumination model and the sampling
that is used for the spectra and the solar angles.

.. code-block:: yaml

   illumination:
      albedoMaterial: 'Concrete'
      tracking: 0 # 0 fixed; 1 east-west axis; 2 dual-axis; 3 latitude-tilted axis; 4 seesaw.
      module_tilt: 50
      module_spacing: 600
      module_azimuth: 180
      IlluminationModel: 'Simplified' # Simplified or Viewfactor; Viewfactor supports fixed orientation only.
      spectral_sampling: 'every_tenth' # full_300_1200_1nm requires Simplified and 1 nm input spectra.
      solar_angle_sampling: 'hour_end'

thermal
~~~~~~~

The ``thermal`` section selects the model that calculates the module
temperature and sets its parameters. It also determines which irradiance is
used as input for the thermal model.

.. code-block:: yaml

   thermal:
      thermalModel: 'SAPM' #Options are 'SAPM','Fuentes','Ross'
      SAPM_type: 0
      noct: 48
      irradiance_source: 'projected_front' # Reference overlay selects legacy_direct_diffuse.

electrical
~~~~~~~~~~

The ``electrical`` section sets up the electrical model. It selects the
solver (analytical or numerical with LTspice) and the device configuration,
and defines the electrical parameters of each sub-cell, such as resistances,
diode parameters and temperature coefficients. The cell arrays are ordered
as [perovskite top, silicon bottom]. The ``ltspice`` subsection is only used
when the numerical solver is selected.

.. code-block:: yaml

   electrical:
      solver: "analytical" # analytical: diode/Lambert-W model; numerical: LTspice.
      configuration: "2T" # Analytical 3T uses a 4T approximation; numerical topology must match ltspice.mode.
      shunt: "with" # Analytical: with/without; numerical LTspice netlists require with.
      photocurrent_integration: "uniform_bin_sum" # Default; use "trapezoid" for point-sampled spectra.
      rsh_tandem_ohm_cm2: 10000 # Whole-device shunt resistance, ohm cm².
      # Cell arrays below are ordered [perovskite top, silicon bottom].
      rsh_ohm_cm2: [1900, 2800] # Per-cell shunt resistance, ohm cm².
      rs_ohm_cm2: [0.9, 0.8] # Per-cell series resistance, ohm cm².
      collection_efficiency: [1.0, 1.0] # Fraction of generated current collected.
      j0_a_cm2: [8.0e-16, 4.0e-11] # Per-cell diode saturation current density, A/cm².
      ideality_factor: [1.3, 1.0] # Per-cell diode ideality factors.
      tc_jsc_per_k: [0.0002, 0.00001] # Relative Jsc temperature coefficient, K⁻¹.
      tc_voc_v_per_k: [-0.002, -0.0044] # Voc temperature coefficient, V/K.
      # RsTandem is derived from rs_ohm_cm2; do not enter it separately.

      ltspice:
         # 2T_n: two-terminal tandem; SJ/SJ_Pero: single-junction Si/perovskite.
         # 3T_n: three-terminal; 4T_n: four-terminal.
         # module_72HCG12_2T_n / module_72HCG12_SJ_n: 72-cell uniform modules.
         # *_shading_n: matching module with bypass-group shading.
         # Degradation_comp: single-junction or tandem with an active degradation parameter.
         ltspice_path: 'C:\Users\a6748\AppData\Local\Programs\ADI\LTSPICE\LTspice.exe'
         netlists: "Electrics/LTspiceNetlists"
         mode: "2T_n" # Numerical topology, used only when solver is "numerical".
         # voltage_step_v: 0.02 # Optional 3T_n voltage step (0.01, 0.02 or 0.05 V); default 0.01 V.
         rbase_ohm_cm2: 1.0e+9 # Tunnel/base resistance where the selected mode uses it.

energy_yield
~~~~~~~~~~~~

The ``energy_yield`` section controls whether degradation is included in the
energy yield calculation, and which parameter is affected by it.

.. code-block:: yaml

   energy_yield:
      degradation_type: "No_Deg" # No_Deg: off; combined: temperature/light degradation.
      # CE changes collection efficiency; Rsh shunt; Rs series; j0 dark current.
      degradation_parameter: "No_Deg" # No_Deg pairs with No_Deg type; others require combined and numerical Degradation_comp.

sweep
~~~~~

The ``sweep`` section runs the simulation repeatedly for a range of values of
one or more parameters. ``varyingParameters`` gives the path to the
parameter in this file and ``varyingValues`` lists the values to simulate.
The example below varies the module tilt between 10 and 40 degrees.

.. code-block:: yaml

   sweep:
      varyingParameters: ['["illumination"]["module_tilt"]']
      varyingValues: [[10,20,30,40]]

.. _profiles:

Profiles
~~~~~~~~

The ``profiles`` section contains named sets of settings that can be
selected for a run (see ``default_profile`` in the ``run`` section). A
profile lists the settings that differ from the defaults above, so you can
switch between, for example, a quick test and a full-year simulation without
editing the rest of the file. The example defines a short test profile
(``fixture_hour``) that simulates one recorded hour, and a profile
(``phoenix``) for a full-year simulation with local data files. You can add
your own profiles in the same way.

.. code-block:: yaml

   profiles:
      fixture_hour:
         description: "One recorded Phoenix TMY3 daylight hour" # Tracked file-based smoke run.
         irradiance:
            source: "hourly_file"
            input_file: "tests/fixtures/phoenix_one_hour.h5"
         illumination:
            albedoMaterial: 'artificialblack'
            module_tilt: 0

      phoenix:
         description: "Phoenix TMY3 weather and generated spectra" # Requires local HDF5 files.

         irradiance:
            source: "cached_tmy3" # Read the two HDF5 files below; do not regenerate them.
            location_code: "722780TYA" # Station code used in the weather HDF5 filename.
            alias: "Phoenix" # Existing weather location label.
            spectra_dir: "SpectralIrradiance/Spectra_722780TYA_Phoenix" # Local, Git-ignored input folder.
            spectra_sha256: "732486fe8825fe34889ba83cf87dedba14e9e4313b3c998fbe99de0166f1c623" # Pin exact spectra input.
            weather_sha256: "84ad6a3fbe6d596bf08a4d9c311c2e255dc45811ed9b1936a94dae18ad414726" # Pin exact weather input.

         illumination:
            module_tilt: 27 # Fixed south-facing Phoenix example, degrees.
         sweep: null

Next steps
----------

- Look at the complete studies on the :doc:`Examples` page.
- Read about the underlying models on the :doc:`Methodology` page.
- Browse all functions and classes in the :doc:`API` reference.