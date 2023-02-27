from typing import Tuple, Optional

from PIL import Image


def resize_image(
    image: Image.Image,
    min_sizes: Tuple[int, int] = (450, 450),
    max_sizes: Tuple[int, int] = (900, 1200)
) -> Optional[Image.Image]:

    width, height = image.size
    if width > height:
        w_percent = max_sizes[0] / width
        new_width = max_sizes[0]
        new_height = int(height * w_percent)

        if new_height < min_sizes[1]:
            return None

    else:
        w_percent = max_sizes[1] / height
        new_height = max_sizes[1]
        new_width = int(width * w_percent)

        if new_width < min_sizes[1]:
            return None
    
    new_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return new_image
