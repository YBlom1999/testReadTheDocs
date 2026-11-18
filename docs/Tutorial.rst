Tutorial
========

This tutorial walks you through a first simulation with the modelling
framework, from setting up the inputs to inspecting the results. It assumes
the package is already installed. If not, see :doc:`installation`.

.. contents:: On this page
   :local:
   :depth: 2

Overview
--------

In this tutorial you will:

1. Import the package and define the input parameters.
2. Run the simulation.
3. Inspect and plot the results.

Each step builds on the previous one, so it is best to follow them in order.

Step 1: Import the package and set up the inputs
------------------------------------------------

Start by importing the package and defining the inputs. Replace the names
below with the ones used in your package.

.. code-block:: python

   import your_package

   # Location and meteorological data
   location = "Delft, Netherlands"

   # Device and module parameters
   device = {
       "architecture": "perovskite/silicon",
   }

Explain here what each input means, which values are allowed, and where
readers can find more details (for example the :doc:`Methodology` page).

Step 2: Run the simulation
--------------------------

Run the simulation with the inputs defined in the previous step.

.. code-block:: python

   results = your_package.run(location=location, device=device)

Describe what happens in this step, how long it typically takes, and which
settings influence the run time.

Step 3: Inspect the results
---------------------------

The simulation returns the results, which you can print or plot.

.. code-block:: python

   print(results)

   import matplotlib.pyplot as plt

   plt.plot(results["time"], results["power"])
   plt.xlabel("Time")
   plt.ylabel("Power (W)")
   plt.show()

Explain how to interpret the output and what the main result is.

.. note::

   Use notes like this one to point out common pitfalls or useful tips.

Next steps
----------

- Look at the complete studies on the :doc:`Examples` page.
- Read about the underlying models on the :doc:`Methodology` page.
- Browse all functions and classes in the :doc:`API` reference.
