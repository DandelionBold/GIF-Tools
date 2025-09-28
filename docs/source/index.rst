GIF-Tools Documentation
======================

Welcome to GIF-Tools, a comprehensive Python library for GIF processing and manipulation.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   user_guide
   api_reference
   development

Features
--------

GIF-Tools provides 17 powerful tools for GIF processing:

* **Video to GIF** - Convert video files to animated GIFs
* **Resize** - Change GIF dimensions while maintaining aspect ratio
* **Rotate** - Rotate GIFs by 90°, 180°, or 270° degrees
* **Crop** - Cut out specific rectangular areas from GIFs
* **Split** - Extract individual frames from GIFs
* **Merge** - Combine multiple GIFs or images into one
* **Add Text** - Text overlay with customizable fonts and colors
* **Rearrange** - Drag-and-drop frame reordering
* **Reverse** - Play GIF animations backwards
* **Optimize** - Advanced optimization with quality levels
* **Speed Control** - Playback speed adjustment
* **Filter Effects** - Visual effects and enhancements
* **Extract Frames** - Save specific frames as static images
* **Loop Settings** - Control loop count and behavior
* **Format Conversion** - Convert between GIF, WebP, APNG formats
* **Batch Processing** - Process multiple files at once
* **Watermark** - Add image or text watermarks

Quick Start
-----------

.. code-block:: python

   from gif_tools.core import resize_gif, add_text_to_gif
   
   # Resize a GIF
   resize_gif('input.gif', 'output.gif', 200, 200)
   
   # Add text to a GIF
   add_text_to_gif('input.gif', 'output.gif', 'Hello World!')

Installation
------------

.. code-block:: bash

   pip install gif-tools

For development installation:

.. code-block:: bash

   git clone https://github.com/KamalNady/GIF-Tools.git
   cd GIF-Tools
   pip install -e .

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
