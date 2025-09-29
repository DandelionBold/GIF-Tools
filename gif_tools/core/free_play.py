"""
Free Play - Layer GIFs with click-to-place functionality.
"""

from pathlib import Path
from typing import List, Dict, Any, Tuple, Union
from PIL import Image
import os


def layer_gifs_free_play(
    gif_layers: List[Dict[str, Any]],
    output_path: Union[str, Path],
    canvas_width: int = 600,
    canvas_height: int = 400,
    quality: int = 85
) -> Path:
    """
    Layer multiple GIFs into one combined GIF.
    
    Args:
        gif_layers: List of layer dictionaries with 'file_path', 'position', 'frames', 'durations', 'is_animated', 'frame_start'
        output_path: Path to save the combined GIF
        canvas_width: Width of the output canvas
        canvas_height: Height of the output canvas
        quality: Output quality (1-100)
        
    Returns:
        Path to the output GIF file
    """
    if not gif_layers:
        raise ValueError("No GIF layers provided")
    
    # Convert to Path
    output_path = Path(output_path)
    
    # Validate gif_layers data structure
    if not isinstance(gif_layers, list):
        raise ValueError(f"gif_layers must be a list, got {type(gif_layers)}")
    
    for i, layer in enumerate(gif_layers):
        if not isinstance(layer, dict):
            raise ValueError(f"Layer {i} must be a dictionary, got {type(layer)}: {layer}")
        if 'frames' not in layer:
            raise ValueError(f"Layer {i} missing 'frames' key")
        if 'durations' not in layer:
            raise ValueError(f"Layer {i} missing 'durations' key")
        if 'position' not in layer:
            raise ValueError(f"Layer {i} missing 'position' key")
        if 'is_animated' not in layer:
            raise ValueError(f"Layer {i} missing 'is_animated' key")
    
    # Create output frames
    output_frames = []
    output_durations = []
    
    # Get the maximum number of frames
    max_frames = max(len(layer['frames']) for layer in gif_layers)
    
    for frame_idx in range(max_frames):
        # Create base frame with custom canvas size
        base_frame = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
        
        # Add each layer
        for layer in gif_layers:
            if layer['is_animated']:
                # Calculate frame index with frame start offset
                layer_frame_start = layer.get('frame_start', 0)
                layer_frame_idx = (frame_idx + layer_frame_start) % len(layer['frames'])
                layer_frame = layer['frames'][layer_frame_idx]
                layer_duration = layer['durations'][layer_frame_idx % len(layer['durations'])]
            else:
                # Use first frame for static GIFs
                layer_frame = layer['frames'][0]
                layer_duration = layer['durations'][0]
            
            # Paste layer at its position
            x, y = layer['position']
            if layer_frame.mode == 'RGBA':
                base_frame.paste(layer_frame, (x, y), layer_frame)
            else:
                base_frame.paste(layer_frame, (x, y))
        
        output_frames.append(base_frame)
        output_durations.append(layer_duration)
    
    # Save combined GIF
    if len(output_frames) == 1:
        # Single frame - save as static image
        output_frames[0].save(output_path, 'GIF', quality=quality, optimize=True)
    else:
        # Multiple frames - save as animated GIF
        output_frames[0].save(
            output_path,
            'GIF',
            save_all=True,
            append_images=output_frames[1:],
            duration=output_durations,
            loop=0,
            quality=quality,
            optimize=True
        )
    
    return output_path


def create_gif_layer(
    file_path: Union[str, Path],
    position: Tuple[int, int] = (0, 0)
) -> Dict[str, Any]:
    """
    Create a GIF layer from a file.
    
    Args:
        file_path: Path to the GIF file
        position: Position to place the GIF (x, y)
        
    Returns:
        Layer dictionary
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"GIF file not found: {file_path}")
    
    # Load GIF
    gif = Image.open(file_path)
    
    # Extract frames
    frames = []
    durations = []
    
    if gif.is_animated:
        for frame_idx in range(gif.n_frames):
            gif.seek(frame_idx)
            frames.append(gif.copy().convert('RGBA'))
            durations.append(gif.info.get('duration', 100))
    else:
        frames.append(gif.copy().convert('RGBA'))
        durations.append(100)
    
    return {
        'file_path': str(file_path),
        'position': position,
        'frames': frames,
        'durations': durations,
        'is_animated': gif.is_animated
    }
