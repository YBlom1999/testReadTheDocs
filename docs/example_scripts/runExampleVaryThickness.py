# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 11:42:12 2026

@author: a6748
"""
import matplotlib.pyplot as plt
import numpy as np
from utils.ey_config import load_config
from run_config import sweepEYCalcPlus


config = load_config('ExampleVaryThickness.yaml')

results = sweepEYCalcPlus(config)

## Make plots of the result
thickness = np.array(config.data['sweep']['varyingValues']).flatten()
energy_yield = np.array([results[k]['TotalEnergyYield'] for k in range(len(results))])
fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(thickness, energy_yield/1e3, marker='o', color='steelblue', linewidth=2)

ax.set_xlabel('Thickness (nm)')
ax.set_ylabel('Energy Yield (kWh/m²)')
ax.set_title('Energy Yield vs Thickness')

fig.tight_layout()
plt.show()

## Make plot of currentMatching
thickness = np.array(config.data['sweep']['varyingValues']).flatten()
currentTop = np.array([results[k]['IVchar']['Jsc'][:,0].mean() for k in range(len(results))])
currentBot = np.array([results[k]['IVchar']['Jsc'][:,1].mean() for k in range(len(results))])

fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(thickness, currentTop, marker='o', color='blue', linewidth=2)
ax.plot(thickness, currentBot, marker='o', color='red', linewidth=2)

ax.set_xlabel('Thickness (nm)')
ax.set_ylabel('Average absorbed current (mA/cm²)')
ax.set_title('Absorbed current vs Thickness')

fig.tight_layout()
plt.show()