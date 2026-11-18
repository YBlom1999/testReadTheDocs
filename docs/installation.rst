How to install
==============

Requirements
------------

- Python 3.9 or newer
- ``pip`` (included with most Python installations)

Install from PyPI
-----------------

The easiest way to install the latest release is with ``pip``:

.. code-block:: bash

   pip install your-package

Install from source
-------------------

To get the latest development version, clone the repository and install it:

.. code-block:: bash

   git clone https://github.com/YBlom1999/testReadTheDocs.git
   cd testReadTheDocs
   pip install .

For development, use an editable install so changes to the code take effect immediately:

.. code-block:: bash

   pip install -e .

Using a virtual environment (recommended)
-----------------------------------------

Installing into a virtual environment keeps the package's dependencies separate from the rest of your system:

.. code-block:: bash

   python -m venv .venv
   source .venv/bin/activate    # on Windows: .venv\Scripts\activate
   pip install your-package

Using conda
-----------

.. code-block:: bash

   conda create -n your-env python=3.12
   conda activate your-env
   pip install your-package

Verify the installation
-----------------------

Check that the package can be imported:

.. code-block:: bash

   python -c "import your_package; print(your_package.__version__)"

Troubleshooting
---------------

.. note::

   If ``pip`` installs the package but the import fails, make sure you are
   running ``python`` from the same environment where you ran ``pip install``.

If you run into other problems, please open an issue on
`GitHub <https://github.com/YBlom1999/testReadTheDocs/issues>`_.