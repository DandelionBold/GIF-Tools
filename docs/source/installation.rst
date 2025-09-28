Installation
============

Requirements
------------

* Python 3.8 or higher
* FFmpeg (for video processing)

Installing FFmpeg
-----------------

**Windows:**
.. code-block:: bash

   choco install ffmpeg

**macOS:**
.. code-block:: bash

   brew install ffmpeg

**Ubuntu/Debian:**
.. code-block:: bash

   sudo apt-get update
   sudo apt-get install ffmpeg

Installing GIF-Tools
--------------------

**From PyPI (when available):**
.. code-block:: bash

   pip install gif-tools

**From source:**
.. code-block:: bash

   git clone https://github.com/DandelionBold/GIF-Tools.git
   cd GIF-Tools
   pip install -e .

**Development installation:**
.. code-block:: bash

   git clone https://github.com/DandelionBold/GIF-Tools.git
   cd GIF-Tools
   pip install -r requirements/dev.txt
   pip install -e .

Verifying Installation
----------------------

.. code-block:: python

   import gif_tools
   print(gif_tools.__version__)
