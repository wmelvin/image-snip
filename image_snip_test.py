import shutil

from datetime import datetime
from pathlib import Path
from PIL import Image
from textwrap import dedent

import image_snip


test_source_image = Path("./images/example-1-1920x1440.jpg")


def get_test_opts_and_img(
    opt_path: Path, process_instruction: str, image_tag: str
):
    """
    Returns (options_file_path, expected_test_image_path).
    """
    d = opt_path / "testopts"

    d.mkdir()

    #  Make a copy of the test image.
    test_image_name = (
        f"test-{image_tag}-{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
    )

    dst = d / test_image_name

    shutil.copyfile(test_source_image, dst)

    opt_file = d / "test-options.txt"

    opt_file.write_text(
        dedent(
            """
            output_folder: ./output/tests
            # timestamp_mode:
            {0}
            {1}
            """
        ).format(process_instruction, dst)
    )
    assert opt_file.exists()

    expect_image = Path("./output/tests") / f"{dst.stem}-crop.jpg"

    return (opt_file, expect_image)


def test_crop_to_box(tmp_path):
    """Test crop_to_box(x1, y1, x2, y2)."""
    opt, img = get_test_opts_and_img(
        tmp_path, "crop_to_box(200, 100, 900, 500)", "crop_to_box"
    )
    args = ["image_snip.py", "--options-file", str(opt)]
    result = image_snip.main(args)
    assert result == 0
    expected_size = (700, 400)
    assert Image.open(img).size == expected_size


def test_crop_larger_than_source(tmp_path):
    """Test specifying cropped size larger than the source image size."""
    opt, img = get_test_opts_and_img(
        tmp_path, "crop_from_left_top(2000, 1800)", "larger"
    )
    args = ["image_snip.py", "--options-file", str(opt)]
    result = image_snip.main(args)
    assert result == 0
    # Should keep source image size, not scale to larger size.
    expected_size = (1920, 1440)
    assert Image.open(img).size == expected_size


def test_crop_zoom(tmp_path):
    opt, img = get_test_opts_and_img(tmp_path, "crop_zoom(800, 800)", "zoom")
    args = ["image_snip.py", "--options-file", str(opt)]
    result = image_snip.main(args)
    assert result == 0
    expected_size = (800, 800)
    assert Image.open(img).size == expected_size


def test_crop_center(tmp_path):
    opt, img = get_test_opts_and_img(
        tmp_path, "crop_from_center(1024, 768)", "center"
    )
    args = ["image_snip.py", "--options-file", str(opt)]
    result = image_snip.main(args)
    assert result == 0
    expected_size = (1024, 768)
    assert Image.open(img).size == expected_size


def test_crop_left_top(tmp_path):
    opt, img = get_test_opts_and_img(
        tmp_path, "crop_from_left_top(640, 480)", "left_top"
    )
    args = ["image_snip.py", "--options-file", str(opt)]
    result = image_snip.main(args)
    assert result == 0
    expected_size = (640, 480)
    assert Image.open(img).size == expected_size


def test_crop_right_top(tmp_path):
    opt, img = get_test_opts_and_img(
        tmp_path, "crop_from_right_top(640, 480)", "right_top"
    )
    args = ["image_snip.py", "--options-file", str(opt)]
    result = image_snip.main(args)
    assert result == 0
    expected_size = (640, 480)
    assert Image.open(img).size == expected_size


def test_crop_left_bottom(tmp_path):
    opt, img = get_test_opts_and_img(
        tmp_path, "crop_from_left_bottom(640, 480)", "left_bottom"
    )
    args = ["image_snip.py", "--options-file", str(opt)]
    result = image_snip.main(args)
    assert result == 0
    expected_size = (640, 480)
    assert Image.open(img).size == expected_size


def test_crop_right_bottom(tmp_path):
    opt, img = get_test_opts_and_img(
        tmp_path, "crop_from_right_bottom(640, 480)", "right_bottom"
    )
    args = ["image_snip.py", "--options-file", str(opt)]
    result = image_snip.main(args)
    assert result == 0
    expected_size = (640, 480)
    assert Image.open(img).size == expected_size


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

            {0}
            """
        ).format(test_source_image)
    )
    assert p.exists()

    args = [
        "image_snip.py",
        "--options-file",
        str(p),
    ]

    result = image_snip.main(args)
    assert result == 0
