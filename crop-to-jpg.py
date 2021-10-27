#!/usr/bin/env python3

import argparse
import sys

from datetime import datetime
from pathlib import Path
from PIL import Image


def get_new_size_zoom(current_size, target_size):
    scale_w = target_size[0] / current_size[0]
    scale_h = target_size[1] / current_size[1]
    scale_by = max(scale_w, scale_h)
    return (int(current_size[0] * scale_by), int(current_size[1] * scale_by))


def crop_box_center(current_size, target_size):
    cur_w, cur_h = current_size
    trg_w, trg_h = target_size

    if trg_w < cur_w:
        x1 = int((cur_w - trg_w) / 2)
        x2 = cur_w - x1
    else:
        x1 = 0
        x2 = trg_w

    if trg_h < cur_h:
        y1 = int((cur_h - trg_h) / 2)
        y2 = cur_h - y1
    else:
        y1 = 0
        y2 = trg_h

    return (x1, y1, x2, y2)


def crop_box_left_top(current_size, target_size):
    """Crop to target size from left-top."""
    cur_w, cur_h = current_size
    trg_w, trg_h = target_size

    assert trg_w <= cur_w
    assert trg_h <= cur_h

    x1 = 0
    x2 = trg_w

    y1 = 0
    y2 = trg_h

    return (x1, y1, x2, y2)


def crop_box_right_top(current_size, target_size):
    """Crop to target size from right-top."""
    cur_w, cur_h = current_size
    trg_w, trg_h = target_size

    assert trg_w <= cur_w
    assert trg_h <= cur_h

    x1 = cur_w - trg_w
    x2 = cur_w

    y1 = 0
    y2 = y1 + trg_h

    return (x1, y1, x2, y2)


def crop_box_left_bottom(current_size, target_size):
    """Crop to target size from left-bottom."""
    cur_w, cur_h = current_size
    trg_w, trg_h = target_size

    assert trg_w <= cur_w
    assert trg_h <= cur_h

    x1 = 0
    x2 = trg_w

    y1 = cur_h - trg_h
    y2 = y1 + trg_h

    return (x1, y1, x2, y2)


def get_output_name(output_path: Path, input_name: str):
    p = Path(input_name)
    return str(output_path.joinpath(f"{p.stem}-crop.jpg"))


def get_args():
    ap = argparse.ArgumentParser(
        description="Crop images and save the cropped versions as .jpg files."
    )

    ap.add_argument(
        "-l",
        "--list-file",
        dest="list_file",
        action="store",
        help="Name of file containing a list of image file names, "
        + "one per line.",
    )

    args = ap.parse_args()

    return args.list_file


def main():
    list_file = get_args()

    #  For now, require a list file. Support for image names as args can be
    #  added later.
    if list_file is None:
        sys.stderr.write("ERROR: No image list file specified.\n")
        sys.exit(1)

    if not Path(list_file).exists():
        sys.stderr.write(f"ERROR: List file not found: '{list_file}'\n")
        sys.exit(1)

    print(f"Reading image list from '{list_file}'.")

    image_paths = []
    error_list = []
    with open(list_file, "r") as f:
        for line in f.readlines():
            s = line.strip().strip("'\"")
            if (0 < len(s)) and (not s.startswith("#")):
                p = Path(s).expanduser().resolve()
                if p.exists():
                    image_paths.append(p)
                else:
                    error_list.append(f"File not found: '{p}'")

    if 0 < len(error_list):
        sys.stderr.write("ERRORS:\n")
        for msg in error_list:
            sys.stderr.write(f"{msg}\n")
        sys.exit(1)

    if len(image_paths) == 0:
        sys.stderr.write(
            "ERROR: List file did not contain any valid file names.\n"
        )
        sys.exit(1)

    # dt = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    dt = datetime.now().strftime("%Y%m%d_%H%M%S")

    #  Save to a directory under the first image files's parent.
    out_path = image_paths[0].parent / f"crop_{dt}"

    assert not out_path.exists()

    out_path.mkdir()

    assert out_path.exists()

    #  sys.exit(0)  # <-- stop here for now.

    # target_size = (650, 950)
    #  TODO: Add to args.

    for image_path in image_paths:
        print(f"Reading '{image_path}'")

        img = Image.open(image_path)

        # new_size = get_new_size_zoom(img.size, target_size)
        # img = img.resize(new_size)

        # crop_box = crop_box_center(img.size, target_size)
        # img = img.crop(crop_box)

        target_size = (1190, 980)
        crop_box = crop_box_left_top(img.size, target_size)
        img = img.crop(crop_box)

        target_size = (640, 960)
        crop_box = crop_box_right_top(img.size, target_size)
        img = img.crop(crop_box)

        target_size = (640, 855)
        crop_box = crop_box_left_bottom(img.size, target_size)
        img = img.crop(crop_box)

        file_name = get_output_name(out_path, image_path)
        print(f"Saving '{file_name}'")

        assert not Path(file_name).exists()

        img.save(file_name)


if __name__ == '__main__':
    main()
