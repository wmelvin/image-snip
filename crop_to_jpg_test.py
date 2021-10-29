
from textwrap import dedent

import crop_to_jpg


def get_options_path_for_proc(opt_path, process_instruction):
    d = opt_path / "testopts"
    d.mkdir()
    p = d / "test-options.txt"
    p.write_text(
        dedent(
            """
            output_folder: ./output/crop_to_jpg
            timestamp_mode: 2
            {0}
            ./images/test-1920x1440.jpg
            """
        ).format(process_instruction)
    )
    assert p.exists()
    return p


def test_crop_bigger(tmp_path):
    p = get_options_path_for_proc(tmp_path, "crop_from_left_top(2000, 1800)")
    args = ["crop_to_jpg.py", "--options-file", str(p)]
    result = crop_to_jpg.main(args)
    assert result == 0


def test_crop_zoom(tmp_path):
    p = get_options_path_for_proc(tmp_path, "crop_zoom(800, 800)")
    args = ["crop_to_jpg.py", "--options-file", str(p)]
    result = crop_to_jpg.main(args)
    assert result == 0


def test_crop_center(tmp_path):
    p = get_options_path_for_proc(tmp_path, "crop_from_center(1024, 768)")
    args = ["crop_to_jpg.py", "--options-file", str(p)]
    result = crop_to_jpg.main(args)
    assert result == 0


def test_crop_left_top(tmp_path):
    p = get_options_path_for_proc(tmp_path, "crop_from_left_top(640, 480)")
    args = ["crop_to_jpg.py", "--options-file", str(p)]
    result = crop_to_jpg.main(args)
    assert result == 0


def test_crop_right_top(tmp_path):
    p = get_options_path_for_proc(tmp_path, "crop_from_right_top(640, 480)")
    args = ["crop_to_jpg.py", "--options-file", str(p)]
    result = crop_to_jpg.main(args)
    assert result == 0


def test_crop_left_bottom(tmp_path):
    p = get_options_path_for_proc(tmp_path, "crop_from_left_bottom(640, 480)")
    args = ["crop_to_jpg.py", "--options-file", str(p)]
    result = crop_to_jpg.main(args)
    assert result == 0


def test_crop_right_bottom(tmp_path):
    p = get_options_path_for_proc(tmp_path, "crop_from_right_bottom(640, 480)")
    args = ["crop_to_jpg.py", "--options-file", str(p)]
    result = crop_to_jpg.main(args)
    assert result == 0


def test_options(tmp_path):
    # reload(crop_to_jpg)
    d = tmp_path / "testopts"
    d.mkdir()
    p = d / "test-options.txt"
    p.write_text(
        dedent(
            """
            #  test-options
            output_folder: ./output/crop_to_jpg
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
        "crop_to_jpg.py",
        "--options-file",
        str(p),
    ]

    result = crop_to_jpg.main(args)
    assert result == 0
