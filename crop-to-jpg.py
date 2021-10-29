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

    #  TODO: Replace assertion with error message + sys.exit (or reduce target
    #  to current dimension and show warning).
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

    #  TODO: Replace assertion with error message + sys.exit (or reduce target
    #  to current dimension and show warning).
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

    #  TODO: Replace assertion with error message + sys.exit (or reduce target
    #  to current dimension and show warning).
    assert trg_w <= cur_w
    assert trg_h <= cur_h

    x1 = 0
    x2 = trg_w

    y1 = cur_h - trg_h
    y2 = y1 + trg_h

    return (x1, y1, x2, y2)


def crop_box_right_bottom(current_size, target_size):
    """Crop to target size from right-bottom."""
    cur_w, cur_h = current_size
    trg_w, trg_h = target_size

    #  TODO: Replace assertion with error message + sys.exit (or reduce target
    #  to current dimension and show warning).
    assert trg_w <= cur_w
    assert trg_h <= cur_h

    x1 = cur_w - trg_w
    x2 = cur_w

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
        "--options-file",
        dest="opt_file",
        action="store",
        help="Name of file containing a list of process instructions and "
        + "image file names, one per line.",
    )

    args = ap.parse_args()

    return args.opt_file


def get_target_size(proc: str):
    """
    Extracts target size as a tuple of 2 integers from a string that ends with
    two integers, in parantheses, separated by a comma.
    """
    a = proc.strip(")").split("(")
    assert len(a) == 2
    b = a[1].split(",")
    assert len(b) == 2
    return (int(b[0]), int(b[1]))


def main():
    opt_file = get_args()

    if opt_file is None:
        sys.stderr.write("ERROR: No options file specified.\n")
        sys.exit(1)

    if not Path(opt_file).exists():
        sys.stderr.write(f"ERROR: File not found: '{opt_file}'\n")
        sys.exit(1)

    print(f"Reading options from '{opt_file}'.")

    image_paths = []
    proc_list = []
    error_list = []
    with open(opt_file, "r") as f:
        for line in f.readlines():
            s = line.strip().strip("'\"")
            if (0 < len(s)) and (not s.startswith("#")):
                if s.startswith("crop_from_"):
                    #  Process instruction.
                    proc_list.append(s)
                else:
                    #  Image file path.
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
            "ERROR: Options file did not contain any image file names.\n"
        )
        sys.exit(1)

    if len(proc_list) == 0:
        sys.stderr.write(
            "ERROR: Options file did not contain any process "
            + "instructions.\n"
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

    for image_path in image_paths:
        print(f"Reading '{image_path}'")

        img = Image.open(image_path)

        #  TODO:
        # new_size = get_new_size_zoom(img.size, target_size)
        # img = img.resize(new_size)

        #  TODO:
        # crop_box = crop_box_center(img.size, target_size)
        # img = img.crop(crop_box)

        # target_size = (1190, 980)
        # crop_box = crop_box_left_top(img.size, target_size)
        # img = img.crop(crop_box)

        # target_size = (640, 960)
        # crop_box = crop_box_right_top(img.size, target_size)
        # img = img.crop(crop_box)

        # target_size = (640, 855)
        # crop_box = crop_box_left_bottom(img.size, target_size)
        # img = img.crop(crop_box)

        for proc in proc_list:
            if proc.startswith("crop_from_left_top"):
                target_size = get_target_size(proc)
                crop_box = crop_box_left_top(img.size, target_size)
                img = img.crop(crop_box)
            elif proc.startswith("crop_from_right_top("):
                target_size = get_target_size(proc)
                crop_box = crop_box_right_top(img.size, target_size)
                img = img.crop(crop_box)
            elif proc.startswith("crop_from_left_bottom("):
                target_size = get_target_size(proc)
                crop_box = crop_box_left_bottom(img.size, target_size)
                img = img.crop(crop_box)
            elif proc.startswith("crop_from_right_bottom("):
                target_size = get_target_size(proc)
                crop_box = crop_box_right_bottom(img.size, target_size)
                img = img.crop(crop_box)
            else:
                sys.stderr.write(
                    "ERROR: Unknown process instruction in options file:\n"
                    + f"'{proc}'\n"
                )
                sys.exit(1)

        file_name = get_output_name(out_path, image_path)
        print(f"Saving '{file_name}'")

        assert not Path(file_name).exists()

        img.save(file_name)


if __name__ == "__main__":
    main()
