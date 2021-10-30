
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


def test_crop_to_box(tmp_path):
    """Test crop_to_box(x1, y1, x2, y2)."""
    p = options_file_with_proc(tmp_path, "crop_to_box(200, 100, 900, 500)")
    args = ["image_snip.py", "--options-file", str(p)]
    result = image_snip.main(args)
    assert result == 0


def test_crop_larger_than_source(tmp_path):
    """Test specifying cropped size larger than the source image size."""
    p = options_file_with_proc(tmp_path, "crop_from_left_top(2000, 1800)")
    args = ["image_snip.py", "--options-file", str(p)]
    result = image_snip.main(args)
    assert result == 0


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
