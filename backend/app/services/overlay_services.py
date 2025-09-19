from typing import List, Dict, Any, Tuple
import ffmpeg
from app.utils import create_file_name, get_upload_path
from sqlalchemy.orm import Session
from app.db import SessionLocal, Overlay


VALID_OVERLAY_TYPES = {"text", "image", "video"}
VALID_LANGUAGES = {"en", "hi", "ta", "bn", "te", "mr"}  # Example Indian languages


def validate_overlays(
    overlays: List[Dict[str, Any]], file_map: Dict[str, Any], max_overlays: int = 3
) -> Tuple[bool, List[str]]:
    """
    Validates a list of overlay objects in a JSON array.

    Args:
        overlays (list): List of overlay dicts from JSON.
        file_map (dict): Mapping of file_key to uploaded file (for image/video overlays).
        max_overlays (int): Maximum allowed overlays.

    Returns:
        is_valid (bool): True if all overlays are valid.
        errors (list): List of error messages if any.
    """
    errors = []

    # Validate that overlays is a list
    if not isinstance(overlays, list):
        errors.append("Overlays must be a list")
        return False, errors

    # Check maximum overlays
    if len(overlays) > max_overlays:
        errors.append(f"Maximum {max_overlays} overlays allowed")

    # Loop through each overlay object
    for idx, overlay in enumerate(overlays, start=1):
        # Validate type
        otype = overlay.get("type")
        if otype not in VALID_OVERLAY_TYPES:
            errors.append(f"Overlay {idx}: Invalid type '{otype}'")

        # Validate start and end times
        start = overlay.get("start")
        end = overlay.get("end")
        if (
            start is None
            or end is None
            or not isinstance(start, (int, float))
            or not isinstance(end, (int, float))
        ):
            errors.append(f"Overlay {idx}: start and end must be numeric")
        elif start >= end:
            errors.append(f"Overlay {idx}: start must be less than end")

        # Validate text overlay
        if otype == "text":
            if not overlay.get("content"):
                errors.append(f"Overlay {idx}: Text overlay must have 'content'")
            language = overlay.get("language")
            if language and language not in VALID_LANGUAGES:
                errors.append(f"Overlay {idx}: Invalid language '{language}'")

        # Validate image/video overlay
        if otype in {"image", "video"}:
            file_key = overlay.get("file_key")
            if not file_key or file_key not in file_map or not file_map[file_key]:
                errors.append(f"Overlay {idx}: Missing or invalid file for overlay")

            # Optional opacity
            opacity = overlay.get("opacity")
            if opacity is not None and (
                not isinstance(opacity, (int, float)) or not (0 <= opacity <= 1)
            ):
                errors.append(
                    f"Overlay {idx}: Opacity must be a number between 0 and 1"
                )

            # Optional scale
            scale = overlay.get("scale")
            if scale and ("width" not in scale or "height" not in scale):
                errors.append(f"Overlay {idx}: Scale must have 'width' and 'height'")

        # Validate position
        pos = overlay.get("position")
        if not pos or not isinstance(pos, dict) or "x" not in pos or "y" not in pos:
            errors.append(f"Overlay {idx}: Position must have 'x' and 'y'")

    is_valid = len(errors) == 0
    return is_valid, errors


def apply_overlays_to_video(input_file: str, overlays: List[Dict[str, Any]]) -> str:
    """"
    start the overlay process
    """
    input_folder = get_upload_path()
    input_file_path = input_folder / input_file
    
    base = ffmpeg.input(str(input_file_path))
    
    inputs = []  # extra inputs for images/videos

    # Prepare inputs for image/video overlays
    for overlay in overlays:
        if overlay['type'] in ['image', 'video']:
            inputs.append(ffmpeg.input(overlay['file_key']))
        else:
            inputs.append(None)

    overlay_stream = base
    input_index = 0
    
    for idx, overlay in enumerate(overlays):
        otype = overlay['type']
        start = overlay.get('start', 0)
        end = overlay.get('end', 999999)
        enable_expr = f'between(t,{start},{end})'

        pos = overlay.get('position', {'x': 0, 'y': 0})
        x = pos.get('x', 0)
        y = pos.get('y', 0)

        if otype == 'text':            
            overlay_stream = overlay_stream.drawtext(
                text=overlay['content'],
                x=x,
                y=y,
                fontsize=overlay.get('fontsize', 24),
                fontcolor=overlay.get('fontcolor', 'white'),
                enable=enable_expr,
                fontfile='C:/Windows/Fonts/arial.ttf',
                escape_text=True
            )

        elif otype in ['image', 'video']:
            media = inputs[input_index]
            input_index += 1

            scale = overlay.get('scale')
            if scale:
                media = media.filter('scale', scale['width'], scale['height'])

            overlay_stream = ffmpeg.overlay(
                overlay_stream,
                media,
                x=x,
                y=y,
                enable=enable_expr
            )

    output_folder = get_upload_path('overlays')
    output_file= create_file_name()
    output_path = output_folder / output_file
    
    print(output_path)
    
    ffmpeg.output(overlay_stream, str(output_path)).run(overwrite_output=True)
    return output_file

def save_overlay(job_id: str, overlay_filename: str, overlays: list):
    """
    Save overlay record into database.

    Args:
        job_id (str): ID of the job.
        overlay_filename (str): Filename of the overlay.
        overlays (list): JSON-compatible list (e.g. [{}, {}]).

    Returns:
        Overlay: The saved Overlay object.
    """
    db: Session = SessionLocal()
    try:
        new_overlay = Overlay(
            job_id=job_id,
            overlay_filename=overlay_filename,
            overlay=overlays
        )
        db.add(new_overlay)
        db.commit()
        db.refresh(new_overlay)
        return new_overlay
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()