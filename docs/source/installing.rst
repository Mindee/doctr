
************
Installation
************

This library requires Python 3.6 or higher.


Prerequisites
=============

Whichever OS you are running, you will need to install at least TensorFlow or PyTorch. You can refer to their corresponding installation pages to do so:

* TensorFlow: `installation page <https://www.tensorflow.org/install/>`_.
* PyTorch: `installation page <https://pytorch.org/get-started/locally/#start-locally>`_.

If you are running another OS than Linux, you will need a few extra dependencies.

For MacOS users, you can install them as follows:

.. code:: shell

    brew install cairo pango gdk-pixbuf libffi

For Windows users, those dependencies are included in GTK. You can find the latest installer over `here <https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases>`_.


Via Python Package
==================

Install the last stable release of the package using pip:

.. code:: bash

    pip install python-doctr


Via Git
=======

Install the library in developper mode:

.. code:: bash

    git clone https://github.com/mindee/doctr.git
    pip install -e doctr/.
