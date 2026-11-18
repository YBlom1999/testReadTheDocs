# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 11:42:12 2026

@author: a6748
"""
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np
from utils.ey_config import load_config
from run_config import sweepEYCalcPlus


config = load_config('ExampleVaryTilt.yaml')

results = sweepEYCalcPlus(config)

## Make plots of the result
tilt = np.array(config.data['sweep']['varyingValues']).flatten()
energy_yield = np.array([results[k]['TotalEnergyYield'] for k in range(len(results))])
fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(tilt, energy_yield/1e3, marker='o', color='steelblue', linewidth=2)

ax.set_xlabel('Tilt (nm)')
ax.set_ylabel('Energy Yield (kWh/m²)')
ax.set_title('Energy Yield vs Tilt')

fig.tight_layout()
plt.show()

## make figure of spectral irradiance
fig, ax = plt.subplots(figsize=(8, 5))

cmap = cm.viridis
norm = mcolors.Normalize(vmin=0, vmax=len(tilt) - 1)

for i in range(len(tilt)):
    ax.plot(results[i]['wavelength'],
            results[i]['hourlySpecIllumFront'].sum(axis=2).sum(axis=0),
            color=cmap(norm(i)), linewidth=1, label=f'Tilt = {tilt[i]}°')

ax.set_xlabel('Wavelength (nm)')
ax.set_xlim([300,1500])
ax.set_ylabel('Spectral Irradiance (W/nm/m^2)')
ax.legend()
fig.tight_layout()
plt.show()