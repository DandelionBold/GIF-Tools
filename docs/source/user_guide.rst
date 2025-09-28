User Guide
==========

This guide provides examples and tutorials for using GIF-Tools.

Basic Usage
-----------

All GIF-Tools functions follow a consistent pattern:

.. code-block:: python

   from gif_tools.core import function_name
   
   result = function_name(input_path, output_path, **parameters)

Basic Tools
-----------

Resize GIF
~~~~~~~~~~

.. code-block:: python

   from gif_tools.core import resize_gif
   
   # Resize to specific dimensions
   resize_gif('input.gif', 'output.gif', 200, 200)
   
   # Resize by percentage
   from gif_tools.core import resize_gif_by_percentage
   resize_gif_by_percentage('input.gif', 'output.gif', 50)  # 50% of original size

Rotate GIF
~~~~~~~~~~

.. code-block:: python

   from gif_tools.core import rotate_gif
   
   # Rotate 90 degrees clockwise
   rotate_gif('input.gif', 'output.gif', 90)
   
   # Flip horizontally
   from gif_tools.core import flip_gif_horizontal
   flip_gif_horizontal('input.gif', 'output.gif')

Crop GIF
~~~~~~~~

.. code-block:: python

   from gif_tools.core import crop_gif
   
   # Crop to specific region (x, y, width, height)
   crop_gif('input.gif', 'output.gif', 10, 10, 100, 100)
   
   # Crop center square
   from gif_tools.core import crop_gif_center
   crop_gif_center('input.gif', 'output.gif', 100, 100)

Advanced Tools
--------------

Add Text
~~~~~~~~

.. code-block:: python

   from gif_tools.core import add_text_to_gif
   
   # Simple text
   add_text_to_gif('input.gif', 'output.gif', 'Hello World!')
   
   # Customized text
   add_text_to_gif(
       'input.gif', 'output.gif', 'Custom Text',
       position=(10, 10),
       font_size=24,
       color=(255, 0, 0),  # Red
       background_color=(0, 0, 0, 128)  # Semi-transparent black
   )

Optimize GIF
~~~~~~~~~~~~

.. code-block:: python

   from gif_tools.core import optimize_gif
   
   # Basic optimization
   optimize_gif('input.gif', 'output.gif')
   
   # Quality-based optimization
   from gif_tools.core import optimize_gif_by_quality
   optimize_gif_by_quality('input.gif', 'output.gif', 'high')

Speed Control
~~~~~~~~~~~~~

.. code-block:: python

   from gif_tools.core import change_gif_speed
   
   # Double speed
   change_gif_speed('input.gif', 'output.gif', 2.0)
   
   # Half speed
   change_gif_speed('input.gif', 'output.gif', 0.5)

Batch Processing
----------------

.. code-block:: python

   from gif_tools.core import resize_gif_batch
   
   # Resize all GIFs in a directory
   resize_gif_batch('input_dir/', 'output_dir/', 200, 200)

Error Handling
--------------

All functions raise :class:`gif_tools.utils.ValidationError` for invalid inputs:

.. code-block:: python

   from gif_tools.core import resize_gif
   from gif_tools.utils import ValidationError
   
   try:
       resize_gif('nonexistent.gif', 'output.gif', 200, 200)
   except ValidationError as e:
       print(f"Error: {e}")
