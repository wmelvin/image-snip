import shutil
from datetime import datetime
from pathlib import Path
from textwrap import dedent

from PIL import Image, ImageFont

import image_snip

test_source_image = Path("./images/example-1-1920x1440.jpg")

test_source_image_2 = Path("./images/example-2-400x400.jpg")
test_source_image_3 = Path("./images/example-3-400x400.jpg")
test_source_image_4 = Path("./images/example-4-400x400.jpg")


def get_test_opts_and_img(opt_path: Path, process_instruction: str, image_tag: str):
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


def test_crop_to_box(tmp_path, monkeypatch):
    """Test crop_to_box(x1, y1, x2, y2)."""
    opt, img = get_test_opts_and_img(
        tmp_path, "crop_to_box(200, 100, 900, 500)", "crop_to_box"
    )

    #  Use monkeypatch once to test args are taken from sys.argv if not passed
    #  directly to main.
    args = ["image_snip", str(opt)]
    monkeypatch.setattr("sys.argv", args)
    result = image_snip.main()

    assert result == 0
    expected_size = (700, 400)
    assert Image.open(img).size == expected_size


def test_crop_to_box_same_size(tmp_path):
    """Test crop_to_box where box is same size as source image."""
    opt, img = get_test_opts_and_img(
        tmp_path, "crop_to_box(0, 0, 1920, 1440)", "crop_to_box"
    )

    args = [str(opt)]
    result = image_snip.main(args)

    assert result == 0
    expected_size = (1920, 1440)
    assert Image.open(img).size == expected_size


def test_crop_larger_than_source(tmp_path):
    """Test specifying cropped size larger than the source image size."""
    opt, img = get_test_opts_and_img(
        tmp_path, "crop_from_left_top(2000, 1800)", "larger"
    )

    args = [str(opt)]
    result = image_snip.main(args)

    assert result == 0
    # Should keep source image size, not scale to larger size.
    expected_size = (1920, 1440)
    assert Image.open(img).size == expected_size


def test_crop_zoom(tmp_path):
    opt, img = get_test_opts_and_img(tmp_path, "crop_zoom(800, 800)", "zoom")

    args = [str(opt)]
    result = image_snip.main(args)

    assert result == 0
    expected_size = (800, 800)
    assert Image.open(img).size == expected_size


def test_crop_center(tmp_path):
    opt, img = get_test_opts_and_img(tmp_path, "crop_from_center(1024, 768)", "center")

    args = [str(opt)]
    result = image_snip.main(args)

    assert result == 0
    expected_size = (1024, 768)
    assert Image.open(img).size == expected_size


def test_crop_left_top(tmp_path):
    opt, img = get_test_opts_and_img(
        tmp_path, "crop_from_left_top(640, 480)", "left_top"
    )

    args = [str(opt)]
    result = image_snip.main(args)

    assert result == 0
    expected_size = (640, 480)
    assert Image.open(img).size == expected_size


def test_crop_right_top(tmp_path):
    opt, img = get_test_opts_and_img(
        tmp_path, "crop_from_right_top(640, 480)", "right_top"
    )

    args = [str(opt)]
    result = image_snip.main(args)

    assert result == 0
    expected_size = (640, 480)
    assert Image.open(img).size == expected_size


def test_crop_left_bottom(tmp_path):
    opt, img = get_test_opts_and_img(
        tmp_path, "crop_from_left_bottom(640, 480)", "left_bottom"
    )

    args = [str(opt)]
    result = image_snip.main(args)

    assert result == 0
    expected_size = (640, 480)
    assert Image.open(img).size == expected_size


def test_crop_right_bottom(tmp_path):
    opt, img = get_test_opts_and_img(
        tmp_path, "crop_from_right_bottom(640, 480)", "right_bottom"
    )

    args = [str(opt)]
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

    args = [str(p)]
    result = image_snip.main(args)

    assert result == 0


def test_animated_gif(tmp_path):
    d = tmp_path / "testopts"
    d.mkdir()
    p = d / "test-animated-gif.txt"
    p.write_text(
        dedent(
            """
            #  test-animated-gif
            output_folder: ./output/tests
            timestamp_mode: 2

            crop_from_left_top(300, 300)

            animated_gif(2000)

            {0}
            {1}
            {2}
            """
        ).format(test_source_image_2, test_source_image_3, test_source_image_4)
    )
    assert p.exists()

    args = [str(p)]
    result = image_snip.main(args)

    assert result == 0


def test_animated_gif_only(tmp_path):
    d = tmp_path / "testopts"
    d.mkdir()
    p = d / "test-animated-gif-only.txt"
    p.write_text(
        dedent(
            """
            #  test-animated-gif-only
            output_folder: ./output/tests
            timestamp_mode: 2

            animated_gif(2000)

            {0}
            {1}
            {2}
            """
        ).format(test_source_image_2, test_source_image_3, test_source_image_4)
    )
    assert p.exists()

    args = [str(p)]
    result = image_snip.main(args)

    assert result == 0


def test_add_text_footer():
    """
    Test add_text_footer().
    This only tests that the image is expanded to hold the footer text.
    The actual text is not tested.
    This test requires specifying a font file, making it system-dependent.
    """

    # Create a blank image
    image = Image.new("RGB", (100, 100), color=(128, 128, 128))

    # Define the parameters.
    text = "Test"
    font = ImageFont.truetype("LiberationMono-Regular.ttf", 12)
    font_size = 15
    numbering = 0
    file_num = 0
    file_count = 0

    # Call the function
    new_image = image_snip.add_text_footer(
        image, text, font, font_size, numbering, file_num, file_count
    )

    # Check the new image's size. Note: The expected size was determined
    # by an initial failed assertion.
    assert new_image.size == (100, 147)


def test_add_a_border(tmp_path):
    dir_path = tmp_path / "test_border"
    dir_path.mkdir()
    out_path = dir_path / "output"
    out_path.mkdir()
    opt_file = dir_path / "test-add-border.txt"
    img_file = dir_path / "a.jpg"
    out_file = out_path / "a-crop.png"

    opt_file.write_text(
        dedent(
            """
            output_folder: {0}

            output_format: PNG

            # border(width, R, G, B)
            border(4, 0, 0, 0)

            {1}
            """
        ).format(out_path, img_file)
    )
    assert opt_file.exists()

    #  Create a new image with white background.
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    img.save(img_file)
    assert img_file.exists()

    args = [str(opt_file)]
    result = image_snip.main(args)

    assert result == 0

    assert out_file.exists()

    out_img = Image.open(out_file)

    assert out_img.size == (100, 100), "Should be original size"

    assert out_img.getpixel((3, 3)) == (0, 0, 0), "Should be black border"
    assert out_img.getpixel((4, 4)) == (255, 255, 255), "Should be original color"


def test_add_a_border_default_color(tmp_path):
    dir_path = tmp_path / "test_border_default"
    dir_path.mkdir()
    out_path = dir_path / "output"
    out_path.mkdir()
    options_file = dir_path / "test-add-border.txt"
    image_file = dir_path / "a.png"
    output_file = out_path / "a-crop.png"

    options_file.write_text(
        dedent(
            """
            output_folder: {0}

            # border(width)
            border(4)

            {1}
            """
        ).format(out_path, image_file)
    )
    assert options_file.exists()

    #  Create a new image with white background.
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    img.save(image_file)
    assert image_file.exists()

    args = [str(options_file)]
    result = image_snip.main(args)

    assert result == 0

    assert output_file.exists()

    out_img = Image.open(output_file)

    assert out_img.size == (100, 100), "Should be original size"

    assert (
        out_img.getpixel((3, 3)) == image_snip.FOOTER_BACKGROUND_RGB
    ), "Should be default color border"

    assert out_img.getpixel((4, 4)) == (255, 255, 255), "Should be original color"


def test_output_format(tmp_path):
    dir_path = tmp_path / "test_output_format"
    dir_path.mkdir()
    out_path = dir_path / "output"
    out_path.mkdir()
    options_file = dir_path / "test-output-format.txt"
    #  Source image is .png
    image_file = dir_path / "a.png"
    #  Output image should be .jpg
    output_file = out_path / "a-crop.jpg"

    options_file.write_text(
        dedent(
            """
            output_folder: {0}

            output_format: JPG

            crop_to_box(10, 10, 90, 90)

            {1}
            """
        ).format(out_path, image_file)
    )
    assert options_file.exists()

    #  Create a new image with white background.
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    img.save(image_file)
    assert image_file.exists()

    args = [str(options_file)]
    result = image_snip.main(args)

    assert result == 0

    assert output_file.exists()
