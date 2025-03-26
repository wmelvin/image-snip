#!/usr/bin/env python3

from __future__ import annotations

import argparse
import io
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import NamedTuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont

__version__ = "2025.03.1"

app_label = f"image_snip (v{__version__})"


FOOTER_PAD_PX = 10
FOOTER_FOREGROUND_RGB = (255, 255, 255)
FOOTER_BACKGROUND_RGB = (25, 25, 112)

TIMESTAMP_SEC = 1  # Add date_time to file name, to the second.
TIMESTAMP_MIC = 2  # Add date_time to file name, to the microsecond.


@dataclass
class FileInfo:
    path: Path = None
    text: str = None


class AppOptions(NamedTuple):
    opts_text: str
    proc_list: list[str]
    files: list[FileInfo]
    output_dir: str
    new_name: str
    output_format: str
    timestamp_mode: int
    gif_ms: int
    do_overwrite: bool
    text_font: str
    text_size: int
    text_numbering: int


def get_new_size_zoom(current_size, target_size):
    """Returns size (width, height) to scale image so
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


# def get_output_name(
#     output_path: Path, output_format: str, input_name: str, timestamp_mode: int
# ):
def get_output_name(
    output_path: Path, input_name: str, opts: AppOptions, file_num: int
) -> str:
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

    if opts.new_name:
        if len(opts.files) > 1:
            file_stem = f"{opts.new_name}-{file_num:03d}"
        else:
            file_stem = opts.new_name
    else:
        file_stem = p.stem

    #  Add a date_time tag to the file name if specified.
    #  Otherwise, append "-crop" to the file name, unless
    #  new_name is specified.

    if opts.timestamp_mode == TIMESTAMP_SEC:
        file_stem = f"{file_stem}-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    elif opts.timestamp_mode == TIMESTAMP_MIC:
        file_stem = f"{file_stem}-{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    elif len(opts.new_name) == 0:
        file_stem = f"{p.stem}-crop"

    if opts.output_format:
        assert opts.output_format in ["JPG", "PNG"]
        ext = f".{opts.output_format.lower()}"
    else:
        ext = p.suffix

    return str(output_path.joinpath(f"{file_stem}{ext}"))


def extract_target_size(proc: str):
    """
    Extracts target size as a tuple of 2 integers (width, height) from
    a string that ends with two integers, in parentheses, separated by
    a comma.
    """
    #  TODO: Replace assert with validation check and error message.
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

    if msg:
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
    #  TODO: Replace assert with validation check and error message.
    a = proc.strip(")").split("(")
    assert len(a) == 2
    return int(a[1])


def extract_text_param(s: str):
    """
    Extracts the parameters for adding text to the bottom of an image,
    from a string that contains a font name (string) and a font size
    (integer), and a numbering option (integer) in parentheses,
    separated by a comma.
    """
    #  TODO: Replace assert with validation check and error message.
    a = s.strip(")").split("(")
    assert len(a) == 2
    b = a[1].split(",")
    assert len(b) == 3
    return (b[0].strip("'\""), int(b[1]), int(b[2]))


def extract_border_attrs(s: str):
    """
    Extract the attributes for adding a border to an image.
    Return (width, (R, G, B))
    """
    #  TODO: Replace assert with validation check and error message.
    a = s.strip(")").split("(")
    assert len(a) == 2

    if "," in a[1]:
        b = [int(x) for x in a[1].split(",")]
        assert len(b) == 4
        return b[0], (b[1], b[2], b[3])

    #  Default border color same as text footer background color.
    return (int(a[1]), FOOTER_BACKGROUND_RGB)


def extract_rounded_attrs(s: str):
    """
    Extract the attributes for adding a rounded border to an image.
    Return (raduis, padding, (R, G, B)) or (raduis, padding, None)
    for transparent background.
    """
    a = s.strip(")").split("(")
    if len(a) != 2:
        return (None, None, None)

    if "," not in a[1]:
        return (None, None, None)

    b = [int(x) for x in a[1].split(",")]

    if len(b) == 5:
        return b[0], b[1], (b[2], b[3], b[4])

    if len(b) == 2:
        return b[0], b[1], None

    return (None, None, None)


def extract_target_box(proc: str):
    """
    Extracts target box as a tuple of 4 integers (x1, y1, x2, y2) from
    a string that ends with four integers, in parentheses, separated
    by a comma.
    """
    #  TODO: Replace assert with validation check and error message.
    a = proc.strip(")").split("(")
    assert len(a) == 2
    b = a[1].split(",")
    assert len(b) == 4
    return (int(b[0]), int(b[1]), int(b[2]), int(b[3]))


def get_target_box(proc, current_size):
    """
    Return box coordinates (x1, y1, x2, y2) to crop image to target box.
    If the box coordinates are outside the current image size, the
    coordinates are adjusted to fit the image size. If the box coordinates
    are invalid, the program exits.
    """
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


def get_args(arglist=None):
    """
    Return arguments parsed from the command line using argparse.
    """
    ap = argparse.ArgumentParser(
        description="Modifies images (crop, resize, and more) and saves the "
        "modified versions as .jpg files. An options (plain text) file is "
        "required to specify the process instructions and list of image "
        "files."
    )

    ap.add_argument(
        "opt_file",
        action="store",
        help="Name of 'options file' containing a list of process "
        "instructions and image file names, one per line.",
    )

    ap.add_argument(
        "--overwrite",
        dest="do_overwrite",
        action="store_true",
        help="Overwrite existing output files. By default, existing files are "
        "not replaced.",
    )

    ap.add_argument(
        "--template",
        dest="do_template",
        action="store_true",
        help="Write available options, as comment lines, to the specified "
        "options file to use as a template. If the file already exists "
        "the template comments are appended to the file.",
    )

    return ap.parse_args(arglist)


def write_template_lines(file_path):
    """
    Write a list of regognized options and process instructions to the
    specified file. If the file already exists the template comments
    are appended to the file.
    """
    print(f"Writing template lines to '{file_path}'")
    with Path(file_path).open("a") as f:
        f.write(
            dedent(
                """
                    # --- image_snip --- Available options:

                    # output_folder:

                    # --- Give files a new name. If more than one file, a sequence
                    #     number will be added to the file name.
                    # new_name:

                    # output_format: JPG | PNG

                    # timestamp_mode:
                        # 1 = Add date_time to file name, to the second.
                        # 2 = Add date_time to file name, to the microsecond.

                    # --- Available process instructions:

                    # crop_from_left_top(width, height)

                    # crop_from_right_top(width, height)

                    # crop_from_left_bottom(width, height)

                    # crop_from_right_bottom(width, height)

                    # crop_from_center(width, height)

                    # crop_to_box(x1, y1, x2, y2)

                    # crop_zoom(width, height)

                    # --- border with default color
                    # border(width)

                    # --- border - specify RGB color
                    # border(width, red, green, blue)

                    # --- rounded border with transparent background
                    # rounded(radius, padding)

                    # --- rounded border - specify RGB background color
                    # rounded(radius, padding, red, green, blue)

                    # animated_gif(duration_milliseconds)

                    # text_footers("font-file-name", font-size, numbering)
                    #   numbering:
                    #     0 = No numbering
                    #     1 = Image number in footer.
                    #     2 = Image number of total in footer.

                    #--- Put list of image files below, one per line:
                    #      If adding text_footers, put the text (caption) on the
                    #      line above the image file name, and begin that line
                    #      with the '>' character to indicate a caption.

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


def get_opts(arglist=None) -> AppOptions:
    """
    Return AppOptions (named tuple) set per the command line arguments
    and the options file. Checks for missing paths and errors in the
    options file.
    """

    args = get_args(arglist)

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

    files: list[FileInfo] = []
    proc_list = []
    output_dir = ""
    new_name = ""
    output_format = ""
    timestamp_mode = 0
    gif_ms = 0
    text_font = ""
    text_size = 0
    text_numbering = 0

    error_list = []
    caption = ""

    opt_text = Path(opt_file).read_text()

    for line in opt_text.splitlines():
        s = line.strip().strip("'\"")
        if s and (not s.startswith("#")):
            if s.startswith(("crop_", "border(", "rounded(")) and s.endswith(")"):
                #  Process instruction.
                proc_list.append(s)
                continue

            if s.startswith("text_footers(") and s.endswith(")"):
                #  Instruction to add text to the bottom of the image.
                text_font, text_size, text_numbering = extract_text_param(s)
                proc_list.append(s)
                continue

            if s.startswith("animated_gif(") and s.endswith(")"):
                #  Instruction to make an animated GIF.
                gif_ms = extract_gif_param(s)
                continue

            if s.startswith("output_folder:"):
                #  Output folder/directory option.
                output_dir = get_opt_str(s)
                continue

            if s.startswith("new_name:"):
                #  New file name option.
                new_name = get_opt_str(s)
                continue

            if s.startswith("output_format:"):
                #  Output format: JPG, JPEG, or PNG.
                output_format = get_opt_str(s)
                continue

            if s.startswith("timestamp_mode:"):
                #  Mode for adding a timestamp to the output file name.
                timestamp_mode = int(get_opt_str(s))
                continue

            if s.startswith(">"):
                #  Footer caption to add to subsequent images.
                #  A line with only '>' clears the text.
                caption = s[1:].strip(" '\"")
                continue

            #  Image file path.
            p = Path(s).expanduser().resolve()
            if p.exists():
                files.append(FileInfo(p, caption))
            else:
                error_list.append(f"File not found: '{p}'")

    if error_list:
        sys.stderr.write("ERRORS:\n")
        for msg in error_list:
            sys.stderr.write(f"{msg}\n")
        sys.exit(1)

    if not files:
        sys.stderr.write("ERROR: Options file did not contain any image file names.\n")
        sys.exit(1)

    if not (proc_list or gif_ms or text_font):
        sys.stderr.write(
            "\nERROR: Options file did not contain any process instructions.\n"
        )
        sys.exit(1)

    if output_dir:
        p = Path(output_dir).expanduser().resolve()
        if not p.exists():
            sys.stderr.write(f"ERROR: output_folder not found: {p}\n")
            sys.exit(1)
        output_dir = str(p)

    if output_format:
        #  If output_format was specified, narrow it down to JPG or PNG.
        if output_format.upper() in ["JPG", "JPEG"]:
            output_format = "JPG"
        elif output_format.upper() == "PNG":
            output_format = "PNG"
        else:
            print(
                f"WARNING: output_format '{output_format}' not valid. "
                "Defaulting to 'PNG'."
            )
            output_format = "PNG"

    return AppOptions(
        opt_text,
        proc_list,
        files,
        output_dir,
        new_name,
        output_format,
        timestamp_mode,
        gif_ms,
        args.do_overwrite,
        text_font,
        text_size,
        text_numbering,
    )


def make_gif(gif_ms, image_list, out_path):
    """
    Make an animated GIF from a list of image files.

    gif_ms: The display duration in milliseconds for each frame.
    image_list: List of image file names.
    out_path: Path to the output directory.
    """
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


def get_est_text_ht(font, font_size, pad_px=20):
    """
    Return the estimeted height in pixels needed to display text using the
    given font and font size.
    ImageDraw.Draw has a textlength() method, but no textheight() method,
    so get the length of the letter "M" and use that to estimate the height.
    Some padding is added to the height.
    """
    temp_img = Image.new("RGB", (400, 400))
    draw = ImageDraw.Draw(temp_img)
    font_len = int(draw.textlength("M", font=font, font_size=font_size))

    return font_len + pad_px


def add_text_footer(image, text, font, font_size, numbering, file_num, file_count):
    """
    Add a footer with text to an image.

    image: Image object to modify.
    text: The text to add to the image.
    font: The font (ImageFont object) to use.
    font_size: The font size to use.
    numbering: The numbering option.
    file_num: The number of the current image file.
    file_count: The total number of image files.

    Returns a new Image object with the footer added.
    """

    est_ht = get_est_text_ht(font, font_size)
    new_h = int(image.height + est_ht + (FOOTER_PAD_PX * 2))

    im = Image.new("RGB", (image.width, new_h), FOOTER_BACKGROUND_RGB)
    im.paste(image, (0, 0))

    #  If the numbering option is 1 or 2 add the image number to the text,
    #  even if text is empty.
    if numbering == 1:
        text = f"{text}  ({file_num})"
    elif numbering == 2:
        text = f"{text}  ({file_num}/{file_count})"

    if text:
        draw = ImageDraw.Draw(im)
        text_at = (est_ht, image.height + FOOTER_PAD_PX)
        draw.text(text_at, text, font=font, fill=FOOTER_FOREGROUND_RGB)

    return im


def add_border(src: Image.Image, proc):
    w, rgb = extract_border_attrs(proc)
    ww = w + w
    new_size = (src.width - ww, src.height - ww)

    img = Image.new("RGB", src.size, rgb)

    src = src.resize(new_size, Image.Resampling.NEAREST)

    img.paste(src, (w, w))

    return img


def add_rounded_border(src: Image.Image, proc) -> Image.Image:
    corner_radius, padding, rgb = extract_rounded_attrs(proc)

    if rgb is None:
        bg_img = Image.new("RGBA", src.size, (0, 0, 0, 0))
    else:
        bg_img = Image.new("RGB", src.size, rgb)

    mask = Image.new("L", src.size, 0)

    draw = ImageDraw.Draw(mask)

    draw.rounded_rectangle(
        (padding, padding, src.size[0] - padding, src.size[1] - padding),
        radius=corner_radius,
        fill=255,
    )

    blur_radius = 1  # Smooth the corners a bit.
    mask = mask.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    return Image.composite(src, bg_img, mask)


def main(arglist=None):
    print(f"\n{app_label}\n")

    opts = get_opts(arglist)

    if opts is None:
        #  Is None if write_template_lines was called.
        return 0

    if opts.text_font:
        try:
            if opts.text_font.lower().endswith(".ttf"):
                font = ImageFont.truetype(opts.text_font, opts.text_size)
            else:
                font = ImageFont.load(opts.text_font)
        except OSError:
            print(f"WARNING: Cannot load font '{opts.text_font}'.")
            return 1
        if not opts.text_size:
            print("WARNING: No font size specified.")
            return 1

    dt = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not opts.output_dir:
        #  Default to a new directory under the first image files's parent.
        out_path = opts.files[0].path.parent / f"crop_{dt}"
        assert not out_path.exists()
        out_path.mkdir()
    else:
        #  If output_dir is specified it must already exist.
        out_path = Path(opts.output_dir)

    #  TODO: Replace assert with validation check and error message.
    assert out_path.exists()

    (out_path / f"image_snip_options-{dt}.txt").write_text(opts.opts_text)

    gif_images = []

    for file_num, file_info in enumerate(opts.files, start=1):
        print(f"Reading '{file_info.path}'")

        src = Image.open(file_info.path)

        img = Image.new("RGB", src.size)

        img.paste(src, (0, 0))

        if not opts.proc_list:
            if opts.gif_ms > 0:
                gif_images.append(str(file_info.path))
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

                elif proc.startswith("border("):
                    img = add_border(img, proc)

                elif proc.startswith("rounded("):
                    img = add_rounded_border(img, proc)

                elif proc.startswith("text_footers("):
                    if opts.text_font:
                        img = add_text_footer(
                            img,
                            file_info.text,
                            font,
                            opts.text_size,
                            opts.text_numbering,
                            file_num,
                            len(opts.files),
                        )

                else:
                    sys.stderr.write(
                        "ERROR: Unknown process instruction in options file:\n"
                        f"'{proc}'\n"
                    )
                    sys.exit(1)

            # file_name = get_output_name(
            #     out_path, opts.output_format, file_info.path, opts.timestamp_mode
            # )
            file_name = get_output_name(out_path, file_info.path, opts, file_num)
            print(f"Saving '{file_name}'")

            p = Path(file_name)
            if p.exists():
                if opts.do_overwrite:
                    p.unlink()
                else:
                    sys.stderr.write(f"ERROR: Cannot replace exising file:\n'{p}'\n")
                    sys.exit(1)

            img.save(file_name)

            if opts.gif_ms > 0:
                gif_images.append(file_name)

    if gif_images:
        make_gif(opts.gif_ms, gif_images, out_path)

    return 0


if __name__ == "__main__":
    main()
