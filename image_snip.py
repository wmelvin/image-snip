#!/usr/bin/env python3

import argparse
import sys

from datetime import datetime
from pathlib import Path
from PIL import Image


def get_new_size_zoom(current_size, target_size):
    """
    Returns size (width, height) to scale image so
    smallest dimension fits target size.
    """
    scale_w = target_size[0] / current_size[0]
    scale_h = target_size[1] / current_size[1]
    scale_by = max(scale_w, scale_h)
    return (int(current_size[0] * scale_by), int(current_size[1] * scale_by))


def crop_box_center(current_size, target_size):
    """
    Returns box coordinates (x1, y1, x2, y2) to
    crop image to target size from center.
    """
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
    """
    Returns box coordinates (x1, y1, x2, y2) to
    crop image to target size from left-top.
    """
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
    """
    Returns box coordinates (x1, y1, x2, y2) to
    crop image to target size from right-top.
    """
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
    """
    Returns box coordinates (x1, y1, x2, y2) to
    crop image to target size from left-bottom.
    """
    cur_w, cur_h = current_size
    trg_w, trg_h = target_size
    assert trg_w <= cur_w
    assert trg_h <= cur_h
    x1 = 0
    x2 = trg_w
    y1 = cur_h - trg_h
    y2 = y1 + trg_h
    return (x1, y1, x2, y2)


def crop_box_right_bottom(current_size, target_size):
    """
    Returns box coordinates (x1, y1, x2, y2) to
    crop image to target size from right-bottom.
    """
    cur_w, cur_h = current_size
    trg_w, trg_h = target_size
    assert trg_w <= cur_w
    assert trg_h <= cur_h
    x1 = cur_w - trg_w
    x2 = cur_w
    y1 = cur_h - trg_h
    y2 = y1 + trg_h
    return (x1, y1, x2, y2)


def get_output_name(output_path: Path, input_name: str, timestamp_mode: int):
    """
    Returns the full path for the output file based on the name of the source
    image file.

    A date_time tag is added to the file name depending on timestamp_mode:
      1 = Add date_time to the second.
      2 = Add date_time to the microsecond.

    Otherwise, "-crop" is appended to the source file name.

    Output files are .jpg format.
    """
    p = Path(input_name)
    if timestamp_mode == 1:
        file_stem = f"{p.stem}-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    elif timestamp_mode == 2:
        file_stem = f"{p.stem}-{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    else:
        file_stem = f"{p.stem}-crop"
    return str(output_path.joinpath(f"{file_stem}.jpg"))


def extract_target_size(proc: str):
    """
    Extracts target size as a tuple of 2 integers (width, height) from
    a string that ends with two integers, in parantheses, separated by
    a comma.
    """
    a = proc.strip(")").split("(")
    assert len(a) == 2
    b = a[1].split(",")
    assert len(b) == 2
    return (int(b[0]), int(b[1]))


def get_target_size(proc, current_size):
    width, height = extract_target_size(proc)
    msg = ""
    if current_size[0] < width:
        msg += "\n  Current width is less than the specified target width."
        width = current_size[0]
    if current_size[1] < height:
        msg += "\n  Current height is less than the specified target height."
        height = current_size[1]
    result = (width, height)
    if 0 < len(msg):
        print(f"WARNING: Target image size reduced from specified value.{msg}")
        print(f"  Process instruction: {proc}")
        print(f"  Current size: {current_size}")
        print(f"  Adjusted target size: {result}")
    return result


def extract_target_box(proc: str):
    """
    Extracts target box as a tuple of 4 integers (x1, y1, x2, y2) from
    a string that ends with four integers, in parantheses, separated
    by a comma.
    """
    a = proc.strip(")").split("(")
    assert len(a) == 2
    b = a[1].split(",")
    assert len(b) == 4
    return (int(b[0]), int(b[1]), int(b[2]), int(b[3]))


def get_target_box(proc, current_size):
    x1, y1, x2, y2 = extract_target_box(proc)

    #  TODO: Replace with error checks, or automatic limits with warning
    #  when applied?
    assert x1 < current_size[0]
    assert y1 < current_size[1]
    assert x2 < current_size[0]
    assert y2 < current_size[1]
    assert x1 < x2
    assert y1 < y2

    return (x1, y1, x2, y2)


def get_args(argv):
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

    return ap.parse_args(argv[1:])


def get_opt_str(opt_line: str) -> str:
    """
    Extracts the string to the left of the first colon in an option
    assignment.
    """
    a = opt_line.strip().split(":", 1)

    #  TODO: Replace with error check.
    assert len(a) == 2

    return a[1].strip()


def get_opts(args):
    opt_file = args.opt_file
    if opt_file is None:
        sys.stderr.write("ERROR: No options file specified.\n")
        sys.exit(1)

    if not Path(opt_file).exists():
        sys.stderr.write(f"ERROR: File not found: '{opt_file}'\n")
        sys.exit(1)

    print(f"Reading options from '{opt_file}'.")

    image_paths = []
    proc_list = []
    output_dir = ""
    timestamp_mode = 0

    error_list = []
    with open(opt_file, "r") as f:
        for line in f.readlines():
            s = line.strip().strip("'\"")
            if (0 < len(s)) and (not s.startswith("#")):
                if s.startswith("crop_") and s.endswith(")"):
                    #  Process instruction.
                    proc_list.append(s)
                elif s.startswith("output_folder:"):
                    #  Output folder/directory option.
                    output_dir = get_opt_str(s)
                elif s.startswith("timestamp_mode:"):
                    #  Mode for adding a timestamp to the output file name.
                    timestamp_mode = int(get_opt_str(s))
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

    if 0 < len(output_dir):
        p = Path(output_dir).expanduser().resolve()
        if not p.exists():
            sys.stderr.write(
                "ERROR: Specified output_folder does not exist.\n"
            )
            sys.exit(1)
        output_dir = str(p)

    return (proc_list, image_paths, output_dir, timestamp_mode)


def main(argv):
    args = get_args(argv)
    # opt_file = get_opts(args)

    proc_list, image_paths, output_dir, timestamp_mode = get_opts(args)

    if len(output_dir) == 0:
        #  Default to a new directory under the first image files's parent.
        dt = datetime.now().strftime('%Y%m%d_%H%M%S')
        out_path = image_paths[0].parent / f"crop_{dt}"
        assert not out_path.exists()
        out_path.mkdir()
    else:
        #  If output_dir is specified it must already exist.
        out_path = Path(output_dir)

    assert out_path.exists()

    for image_path in image_paths:
        print(f"Reading '{image_path}'")

        img = Image.open(image_path)

        for proc in proc_list:
            if proc.startswith("crop_from_center"):
                target_size = get_target_size(proc, img.size)
                crop_box = crop_box_center(img.size, target_size)
                img = img.crop(crop_box)

            elif proc.startswith("crop_from_left_top"):
                target_size = get_target_size(proc, img.size)
                crop_box = crop_box_left_top(img.size, target_size)
                img = img.crop(crop_box)

            elif proc.startswith("crop_from_right_top("):
                target_size = get_target_size(proc, img.size)
                crop_box = crop_box_right_top(img.size, target_size)
                img = img.crop(crop_box)

            elif proc.startswith("crop_from_left_bottom("):
                target_size = get_target_size(proc, img.size)
                crop_box = crop_box_left_bottom(img.size, target_size)
                img = img.crop(crop_box)

            elif proc.startswith("crop_from_right_bottom("):
                target_size = get_target_size(proc, img.size)
                crop_box = crop_box_right_bottom(img.size, target_size)
                img = img.crop(crop_box)

            elif proc.startswith("crop_zoom("):
                target_size = get_target_size(proc, img.size)
                new_size = get_new_size_zoom(img.size, target_size)
                img = img.resize(new_size)

            elif proc.startswith("crop_to_box("):
                crop_box = get_target_box(proc, img.size)
                img = img.crop(crop_box)

            else:
                sys.stderr.write(
                    "ERROR: Unknown process instruction in options file:\n"
                    + f"'{proc}'\n"
                )
                sys.exit(1)

        file_name = get_output_name(out_path, image_path, timestamp_mode)
        print(f"Saving '{file_name}'")

        #  TODO: Overwrite option?
        assert not Path(file_name).exists()

        img.save(file_name)

        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
