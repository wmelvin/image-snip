#!/usr/bin/env python3

import sys

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


def get_output_name(input_name: str):
    p = Path(input_name).expanduser().resolve()
    return str(p.parent.joinpath(f"crop-{p.stem}.jpg"))


def main():
    img_list = [
        "~/LocalCopy/Screenshots_Tweets/Screenshot_2021-10-27_07-56-24.png",
        "~/LocalCopy/Screenshots_Tweets/Screenshot_2021-10-27_07-56-45.png",
    ]  # <-- Image file names here.

    # for file_name in img_list:
    #     out_name = get_output_name(file_name)
    #     if Path(out_name).exists():
    #         sys.stderr.write(f"Output file already exists\n  '{out_name}'\n")
    #         sys.exit(1)

    target_size = (650, 950)

    for im in img_list:
        image_path = Path(im).expanduser().resolve()
        print(image_path)

        img = Image.open(image_path)

        new_size = get_new_size_zoom(img.size, target_size)
        img = img.resize(new_size)

        crop_box = crop_box_center(img.size, target_size)
        img = img.crop(crop_box)

        file_name = get_output_name(image_path)
        print(file_name)

        assert not Path(file_name).exists()

        img.save(file_name)


if __name__ == '__main__':
    main()
