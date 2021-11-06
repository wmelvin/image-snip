import shutil

from pathlib import Path
from PIL import Image
from textwrap import dedent

import image_snip


def options_file_with_proc(opt_path, process_instruction):
    d = opt_path / "testopts"
    d.mkdir()
    p = d / "test-options.txt"
    p.write_text(
        dedent(
            """
            output_folder: ./output/tests
            timestamp_mode: 2
            {0}
            ./images/test-1920x1440.jpg
            """
        ).format(process_instruction)
    )
    assert p.exists()
    return p


def options_file_with_proc_and_image(
    opt_path, process_instruction, image_name
):
    """
    Returns (options_file_path, test_image_path).
    """
    d = opt_path / "testopts"
    d.mkdir()

    #  Make a copy of the test image.
    src = Path("./images/test-1920x1440.jpg")
    dst = d / image_name
    shutil.copyfile(src, dst)

    p = d / "test-options.txt"
    p.write_text(
        dedent(
            """
            output_folder: ./output/tests
            # timestamp_mode:
            {0}
            {1}
            """
        ).format(process_instruction, dst)
    )
    assert p.exists()
    return (p, dst)


def test_crop_to_box(tmp_path):
    """Test crop_to_box(x1, y1, x2, y2)."""
    p = options_file_with_proc(tmp_path, "crop_to_box(200, 100, 900, 500)")
    args = ["image_snip.py", "--options-file", str(p)]
    result = image_snip.main(args)
    assert result == 0


def test_crop_larger_than_source(tmp_path):
    """Test specifying cropped size larger than the source image size."""
    opt_path, img_path = options_file_with_proc_and_image(
        tmp_path, "crop_from_left_top(2000, 1800)", "test-larger.jpg"
    )
    args = ["image_snip.py", "--options-file", str(opt_path)]
    result = image_snip.main(args)
    assert result == 0
    # Should keep source image size, not scale to larger size.
    expected_size = (1920, 1440)  
    assert Image.open(img_path).size == expected_size


def test_crop_zoom(tmp_path):
    p = options_file_with_proc(tmp_path, "crop_zoom(800, 800)")
    args = ["image_snip.py", "--options-file", str(p)]
    result = image_snip.main(args)
    assert result == 0


def test_crop_center(tmp_path):
    p = options_file_with_proc(tmp_path, "crop_from_center(1024, 768)")
    args = ["image_snip.py", "--options-file", str(p)]
    result = image_snip.main(args)
    assert result == 0


def test_crop_left_top(tmp_path):
    p = options_file_with_proc(tmp_path, "crop_from_left_top(640, 480)")
    args = ["image_snip.py", "--options-file", str(p)]
    result = image_snip.main(args)
    assert result == 0


def test_crop_right_top(tmp_path):
    p = options_file_with_proc(tmp_path, "crop_from_right_top(640, 480)")
    args = ["image_snip.py", "--options-file", str(p)]
    result = image_snip.main(args)
    assert result == 0


def test_crop_left_bottom(tmp_path):
    p = options_file_with_proc(tmp_path, "crop_from_left_bottom(640, 480)")
    args = ["image_snip.py", "--options-file", str(p)]
    result = image_snip.main(args)
    assert result == 0


def test_crop_right_bottom(tmp_path):
    p = options_file_with_proc(tmp_path, "crop_from_right_bottom(640, 480)")
    args = ["image_snip.py", "--options-file", str(p)]
    result = image_snip.main(args)
    assert result == 0


def test_options(tmp_path):
    d = tmp_path / "testopts"
    d.mkdir()
    p = d / "test-options.txt"
    p.write_text(
        dedent(
            """
            #  test-options
            output_folder: ./output/tests
            timestamp_mode: 2

            crop_from_center(960, 960)

            crop_from_left_top(1280, 960)
            crop_from_right_top(960, 960)
            crop_from_left_bottom(960, 480)
            crop_from_right_bottom(640, 480)

            ./images/test-1920x1440.jpg
            """
        )
    )
    assert p.exists()

    args = [
        "image_snip.py",
        "--options-file",
        str(p),
    ]

    result = image_snip.main(args)
    assert result == 0
