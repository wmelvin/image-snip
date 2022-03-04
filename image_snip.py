#!/usr/bin/env python3

import argparse
import io
import sys

from collections import namedtuple
from datetime import datetime
from pathlib import Path
from PIL import Image
from textwrap import dedent


app_version = "220304.1"

pub_version = "0.1.dev1"

app_label = f"image_snip.py version {pub_version} (mod {app_version})"


AppOptions = namedtuple(
    "AppOptions",
    "proc_list, image_paths, output_dir, timestamp_mode, gif_ms, do_overwrite",
)


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
    a string that ends with two integers, in parentheses, separated by
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


def extract_gif_param(proc: str):
    """
    Extracts the parameter for an animated GIF, currently just the frame
    display duration in milliseconds, from a string that ends with an
    integer, in parentheses.
    """
    a = proc.strip(")").split("(")
    assert len(a) == 2
    return int(a[1])


def extract_target_box(proc: str):
    """
    Extracts target box as a tuple of 4 integers (x1, y1, x2, y2) from
    a string that ends with four integers, in parentheses, separated
    by a comma.
    """
    a = proc.strip(")").split("(")
    assert len(a) == 2
    b = a[1].split(",")
    assert len(b) == 4
    return (int(b[0]), int(b[1]), int(b[2]), int(b[3]))


def get_target_box(proc, current_size):
    x1, y1, x2, y2 = extract_target_box(proc)

    if (x2 < x1) or (y2 < y1):
        sys.stderr.write("ERROR: Invalid box coordinates.\n")
        sys.stderr.write(f"  {proc}\n")
        sys.exit(1)

    adjusted = False
    if current_size[0] < x1:
        x1 = current_size[0]
        adjusted = True

    if current_size[1] < y1:
        y1 = current_size[1]
        adjusted = True

    if current_size[0] < x2:
        x2 = current_size[0]
        adjusted = True

    if current_size[1] < y2:
        y2 = current_size[1]
        adjusted = True

    if adjusted:
        print("Warning: Box coordinates adjusted to fit image size.")

    return (x1, y1, x2, y2)


def get_args(argv):
    ap = argparse.ArgumentParser(
        description="Modifies images (crop, resize, and more) and saves the "
        + "modified versions as .jpg files. An options (plain text) file is "
        + "required to specify the process instructions and list of image "
        + "files."
    )

    ap.add_argument(
        "opt_file",
        action="store",
        help="Name of 'options file' containing a list of process "
        + "instructions and image file names, one per line.",
    )

    ap.add_argument(
        "--overwrite",
        dest="do_overwrite",
        action="store_true",
        help="Overwrite existing output files. By default, existing files are "
        + "not replaced.",
    )

    ap.add_argument(
        "--template",
        dest="do_template",
        action="store_true",
        help="Write available options, as comment lines, to the specified "
        + "options file to use as a template. If the file already exists "
        + "the template comments are appended to the file.",
    )

    return ap.parse_args(argv[1:])


def write_template_lines(file_path):
    print(f"Writing template lines to '{file_path}'")
    with open(file_path, "a") as f:
        f.write(
            dedent(
                """
                    #--- Available options:

                    # output_folder:

                    # timestamp_mode:
                        # 1 = Add date_time to file name, to the second.
                        # 2 = Add date_time to file name, to the microsecond.

                    #--- Available process instructions:

                    # crop_from_left_top(width, height)

                    # crop_from_right_top(width, height)

                    # crop_from_left_bottom(width, height)

                    # crop_from_right_bottom(width, height)

                    # crop_from_center(width, height)

                    # crop_to_box(x1, y1, x2, y2)

                    # crop_zoom(width, height)

                    # animated_gif(duration_milliseconds)

                    #--- Put list of image files below, one per line:
                """
            )
    )


def get_opt_str(opt_line: str) -> str:
    """
    Extracts the string to the left of the first colon in an option
    assignment.
    """
    a = opt_line.strip().split(":", 1)

    #  TODO: Replace with error check.
    assert len(a) == 2

    return a[1].strip()


def get_opts(args) -> AppOptions:
    opt_file = args.opt_file
    if opt_file is None:
        sys.stderr.write("ERROR: No options file specified.\n")
        sys.exit(1)

    if args.do_template:
        write_template_lines(opt_file)
        return None

    if not Path(opt_file).exists():
        sys.stderr.write(f"ERROR: File not found: '{opt_file}'\n")
        sys.exit(1)

    print(f"Reading options from '{opt_file}'.")

    image_paths = []
    proc_list = []
    output_dir = ""
    timestamp_mode = 0
    gif_ms = 0

    error_list = []
    with open(opt_file, "r") as f:
        for line in f.readlines():
            s = line.strip().strip("'\"")
            if (0 < len(s)) and (not s.startswith("#")):
                if s.startswith("crop_") and s.endswith(")"):
                    #  Process instruction.
                    proc_list.append(s)
                elif s.startswith("animated_gif(") and s.endswith(")"):
                    #  Instruction to make an animated GIF.
                    gif_ms = extract_gif_param(s)
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

    if len(proc_list) == 0 and gif_ms == 0:
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

    opts = AppOptions(
        proc_list,
        image_paths,
        output_dir,
        timestamp_mode,
        gif_ms,
        args.do_overwrite,
    )

    return opts


def make_gif(gif_ms, image_list, out_path):
    # #  Use the last file in the list as the basis for the animated GIF
    # #  file name.
    # last_file = Path(image_list[-1])

    #  Use the first file in the list as the basis for the animated GIF
    #  file name.
    p = Path(image_list[0])
    gif_path = (out_path / f"zgif-{p.name}").with_suffix(".gif")

    new_img = None
    frames = []
    first = True

    for file_name in image_list:
        print(f"Reading '{Path(file_name)}'")

        img = Image.open(file_name)
        # print(img.format, img.size, img.mode)

        mem_buf = io.BytesIO()

        #  Use Image.save to convert to GIF format in-memory.
        img.save(mem_buf, format="GIF")

        img = Image.open(mem_buf)
        # print(img.format, img.size, img.mode)

        if first:
            first_size = img.size
            new_img = img
            first = False
        else:
            if img.size != first_size:
                img.resize(first_size)
            frames.append(img)

    print(f"Writing '{gif_path}'")

    if new_img is not None:
        new_img.save(
            str(gif_path),
            format="GIF",
            append_images=frames,
            save_all=True,
            duration=gif_ms,
            loop=0,
        )


def main(argv):
    print(f"\n{app_label}\n")

    args = get_args(argv)

    opts = get_opts(args)

    if opts is None:
        #  Is None if write_template_lines was called.
        return 0

    if len(opts.output_dir) == 0:
        #  Default to a new directory under the first image files's parent.
        dt = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = opts.image_paths[0].parent / f"crop_{dt}"
        assert not out_path.exists()
        out_path.mkdir()
    else:
        #  If output_dir is specified it must already exist.
        out_path = Path(opts.output_dir)

    assert out_path.exists()

    # gif_ms = 0
    gif_images = []

    for image_path in opts.image_paths:
        print(f"Reading '{image_path}'")

        src = Image.open(image_path)

        img = Image.new("RGB", src.size)

        img.paste(src, (0, 0))

        if len(opts.proc_list) == 0:
            if 0 < opts.gif_ms:
                gif_images.append(str(image_path))
        else:
            for proc in opts.proc_list:
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
                    target_size = get_target_size(proc, img.size)
                    crop_box = crop_box_center(img.size, target_size)
                    img = img.crop(crop_box)

                elif proc.startswith("crop_to_box("):
                    crop_box = get_target_box(proc, img.size)
                    img = img.crop(crop_box)

                else:
                    sys.stderr.write(
                        "ERROR: Unknown process instruction in options file:\n"
                        + f"'{proc}'\n"
                    )
                    sys.exit(1)

            file_name = get_output_name(
                out_path, image_path, opts.timestamp_mode
            )
            print(f"Saving '{file_name}'")

            p = Path(file_name)
            if p.exists():
                if opts.do_overwrite:
                    p.unlink()
                else:
                    sys.stderr.write(
                        "ERROR: Cannot replace exising file:\n" + f"'{p}'\n"
                    )
                    sys.exit(1)

            img.save(file_name)

            if 0 < opts.gif_ms:
                gif_images.append(file_name)

    if 0 < len(gif_images):
        make_gif(opts.gif_ms, gif_images, out_path)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
