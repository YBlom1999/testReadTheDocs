# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 11:42:12 2026

@author: a6748
"""
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np

from Optics.OpticsModule import OpticsModule
from Illumination.Illumination import Illumination
from EnergyYield.EnergyYield import EnergyYield
from Electrics.solver_paths import validate_solver_paths
from Thermal.thermal import thermalCalculation
from utils.readInputs import prepareOpticsInput, prepareIrradianceInput, prepareElectricInput, prepareIlluminationInput
from utils.ey_config import load_config, validate_thermal_settings
from utils.period_inputs import prepare_period_inputs
from utils.Parameters import Parameters

"""
This script provides an example of how sub bandgap reflectors can be studied with EYCalcPlus.
It requires to do the simulation step by step and adjust the received irradiance at a certain moment

The study of sub bandgap reflectors is performed in: 
Klaus Jäger, Jyotirmoy Mandal, Barry P. Rand, Forrest Meggers, Christiane Becker; 
How do sub-bandgap reflectors affect the performance of photovoltaic modules?. 
Sustainable Energy Fuels 2026; https://doi.org/10.1039/d6se00463f
"""
##################
# Prepare inputs #
##################
config = load_config('ExampleSBR.yaml')

## Optics input
IndRefr, Stack, LayerThickness, AngleResolution, Morphology, bifacial, Polarization, lambdaTMM, PathOpticsResults, StoreInDatabase, IncoherentLayers, indx_abs = prepareOpticsInput(config)

## Irradiance input
(_, AliasLocation, _, _, _, cams_csv_minute, cams_csv_hourly,
 nc_sfc, nc_plev, lat_target, lon_target, timezone) = prepareIrradianceInput(config)

## Illumination input
ModuleInputs= prepareIlluminationInput(config)

## Thermal input
thermal_inputs = config.data['thermal']

## Electric inputs
electrics, PathEYResults = prepareElectricInput(config)
validate_solver_paths(electrics)

################################
# Perform reference simulation #
################################
#Spectral simulation
period = prepare_period_inputs(
    config, selection=None, input_file=None,
    input_start=None, input_timezone=None,
    warmup_history=None)
SpecIrr, DataTMY3 = period.spectra, period.weather
validate_thermal_settings(thermal_inputs, n_hours=len(DataTMY3))
ModuleInputs.update(period.context)

#Optics simulation
optics = OpticsModule(IndRefr, Stack, LayerThickness, AngleResolution, Morphology, bifacial, Polarization, lambdaTMM, PathOpticsResults, StoreInDatabase, IncoherentLayers, indx_abs)

#Illumination calculation
RecIrr = Illumination(SpecIrr, DataTMY3, ModuleInputs,
           data_source='CSV',
           cams_csv_minute=cams_csv_minute,
           cams_csv_hourly=cams_csv_hourly,
           nc_sfc=nc_sfc,
           nc_plev=nc_plev,
           lat_target=lat_target,
           lon_target=lon_target,
           timezone=timezone,
           )

#Temperature simulation
ModuleTemperature_ref = thermalCalculation(thermal_inputs, RecIrr,optics,DataTMY3)

#Electric calculation
degradation = config.data['energy_yield']
EY_ref = EnergyYield(RecIrr, optics, electrics, ModuleTemperature_ref, DataTMY3,
                    PathEYResults, StoreInDatabase, AliasLocation,
                    params=Parameters() if degradation['degradation_type'] == 'combined' else None,
                    Deg_Type=degradation['degradation_type'],
                    Deg_param=degradation['degradation_parameter'],
                    module_inputs=ModuleInputs)

###############################
# Perform simulation with SBR #
###############################
SBR_wavelength = 1400 #Reject all wavelengths (nm) above this value
wavelength_sel = SpecIrr['Irr_spectra_clouds_wavelength'] > SBR_wavelength

#Update received illuminatoin
RecIrr["frontSpec"][:,wavelength_sel,:] = 0
RecIrr["backSpec"][:,wavelength_sel,:] = 0
RecIrr["frontAbs"] = np.trapezoid(RecIrr["frontSpec"].sum(axis =2),SpecIrr['Irr_spectra_clouds_wavelength'])
RecIrr["backAbs"] = np.trapezoid(RecIrr["backSpec"].sum(axis =2),SpecIrr['Irr_spectra_clouds_wavelength'])

#Rerun thermal and electrical simulation
ModuleTemperature_SBR = thermalCalculation(thermal_inputs, RecIrr,optics,DataTMY3)
EY_SBR = EnergyYield(RecIrr, optics, electrics, ModuleTemperature_SBR, DataTMY3,
                    PathEYResults, StoreInDatabase, AliasLocation,
                    params=Parameters() if degradation['degradation_type'] == 'combined' else None,
                    Deg_Type=degradation['degradation_type'],
                    Deg_param=degradation['degradation_parameter'],
                    module_inputs=ModuleInputs)

# ── Plot daily power and temperature──────────────────────────────────────────
day_sel = 150
hours_sel = day_sel*24+np.arange(0,48)

fig, (ax1, ax2) = plt.subplots(2,1, figsize=(10, 8))

ax1.plot(np.arange(0,48),EY_ref['Pmpp'][hours_sel],color = 'blue',label = 'Ref.')
ax1.plot(np.arange(0,48),EY_SBR['Pmpp'][hours_sel],color = 'red',label = 'SBR')
ax1.set_ylabel('Pmpp (W/m^2)')
ax1.legend()
ax1.set_title('Daily trend for 1 and 2 June')

ax2.plot(np.arange(0,48),ModuleTemperature_ref[hours_sel],color = 'blue',label = 'Ref.')
ax2.plot(np.arange(0,48),ModuleTemperature_SBR[hours_sel],color = 'red',label = 'SBR')
ax2.set_ylabel('Tmod (C)')
ax2.legend()
ax2.set_xlabel('Time (h)')

# ── Plot energy yields and temperature────────────────────────────────────────
EnergyYields = [EY_ref['Pmpp'].sum()/1e3,EY_SBR['Pmpp'].sum()/1e3]
temperatures = [ModuleTemperature_ref.flatten(), ModuleTemperature_SBR.flatten()]

fig, (ax1, ax2) = plt.subplots(1,2, figsize=(10, 8))

bars = ax1.bar([1,2], EnergyYields, color='steelblue', width=0.5)

for bar in bars:
    ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
             f'{bar.get_height():.0f}', ha='center', va='bottom', fontsize=12)

ax1.set_xticks([1,2])
ax1.set_xticklabels(['Ref.','SBR'])
ax1.set_ylabel('Energy Yield (kWh/m²)')

ax2.boxplot(temperatures, patch_artist=True,
            boxprops=dict(facecolor='tomato', alpha=0.6))
ax2.set_xticks([1,2])
ax2.set_xticklabels(['Ref.','SBR'])
ax2.set_ylabel('Module Temperature (°C)')
ax2.set_title('Module Temperature Distribution per Location')
