Spectral irradiance model
=========================

This module calculates realistic irradiation data, which is used as input for
the energy yield calculations. For this the TMY3 data sets, available from the
National Renewable Energy Laboratory (NREL), are used. They contain
statistically representative and hourly resolved meteorological / irradiation
data of many locations spread over the USA, representing all relevant climatic
zones. For each location, they contain measured atmospheric properties like
dry-bulb temperature, pressure, precipitable water, aerosol optical depth and
albedo. Based on all these properties, the irradiance and the sun's position,
the spectrally resolved (280 nm - 4000 nm) clear sky irradiance is calculated
with SMARTS. In SMARTS, we use the Shettle and Fenn's urban aerosol model and
the US standard reference atmosphere.

The obtained clear sky irradiance is further enhanced by a simple cloud model.
For this, the cloud cover, which is available in the TMY3 dataset is used.
This simple cloud model assumes no spectral change for the direct irradiation.
The diffuse irradiation however, is assumed to be composed by the direct and
diffuse clear sky irradiance weighted by the cloud cover. The normalized
spectral data is finally scaled to the measured diffuse irradiance of the TMY3
data.

.. math::

   I_{\text{clouds,dir}}(\lambda) =
   \frac{I_{\text{clear,dir}}(\lambda)}
        {\int I_{\text{clear,dir}}(\lambda)\,d\lambda}
   \cdot I_{\text{meas,dir}}\,.

.. math::

   I_{\text{clouds,diff}}(\lambda) =
   \frac{I_{\text{clear,diff}}(\lambda)\cdot(1-\text{CC})
         + I_{\text{clear,dir}}(\lambda)\cdot \text{CC}}
        {\int \left[ I_{\text{clear,diff}}(\lambda)\cdot(1-\text{CC})
         + I_{\text{clear,dir}}(\lambda)\cdot \text{CC} \right] d\lambda}
   \cdot I_{\text{meas,diff}}\,.