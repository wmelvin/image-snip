# image_snip #

**image_snip.py** is a command-line utility for applying the same crop and/or zoom operations to a batch of image files. It could be a *batch-of-one*, but why not just use an image editor like Photoshop or GIMP for that?

This Python program evolved (a little) from a one-off utility script used to process batches of images where the same areas were cropped. The original script started with hard-coded paths. Later an *options file* was added so the a set of operations could be applied to different sets of image files.

This is a simple application of Python and [Pillow](https://python-pillow.org/). There are other, more powerful, options such as [Automating GIMP](https://www.gimp.org/tutorials/Automate_Editing_in_GIMP/).


## Options File ##

The options file contains the following items:
- Settings
- Process Instructions
- Image list (one or more file names)

Any line starting with a pound sign (**#**) is treated as a **comment**. Only whole-line comments are supported.

The following **Settings** can be specified in the options file:

Save the modified images to the given folder path:
- `output_folder: path`

Add a *date_time* tag to the output file name. The setting value specifies the resolution of the time part:
- `timestamp_mode: [n]`
  - `1` = Add *date_time* to the second.
  - `2` = Add *date_time* to the microsecond.

If no *timestamp_mode* is specified, the output file is named with "*-crop*" appended to the source file name.

The following **Process Instructions** can be specified in the options file:

These crop the image to the given *width* and *height* (in pixels) starting from the corner (or center) as stated in the instruction's name:
- `crop_from_center(width, height)`
- `crop_from_left_bottom(width, height)`
- `crop_from_left_top(width, height)`
- `crop_from_right_bottom(width, height)`
- `crop_from_right_top(width, height)`

Crop from any part of the image using the given [box coordinates](https://pillow.readthedocs.io/en/stable/handbook/concepts.html#coordinate-system):
- `crop_to_box(x1, y1, x2, y2)`

Resize (zoom) the image to fill the entire target area, then crop to the given *width* and *height*:
- `crop_zoom(width, height)`

Create an animated GIF using all images with the given display *duration* (in milliseconds) for each frame. The GIF file is created after all other instructions have been applied to the list of images, and the modified versions of those images have been saved. It is given the same file name as the last image in the list but with a *.gif* extension.
- `animated_gif(duration)`


**Example options file:**

```
  #  options-1.txt

  output_folder: ./output

  timestamp_mode: 1

  crop_from_left_bottom(1920, 500)
  crop_from_right_bottom(700, 500)
  crop_to_box(100, 100, 500, 400)
  crop_zoom(600, 600)

  ./images/example-1-1920x1440.jpg
```

The set of one or more *process instructions* are applied to each image listed in the options file. The example above has only one image, but the original use-case for this tool had many images to which the same operations were applied. Also, the series of process instructions is just an example of combining multiple instructions. It is not a useful combination. In practice, only one or two operations are needed (perhaps one kind of *crop* and maybe a *zoom*).


**Example including animated GIF:**

```
output_folder: ./output

crop_to_box(416, 90, 1370, 530)

# Make an animated GIF with frame duration of 2 seconds (2000 ms).

animated_gif(2000)

~/Pictures/screenshot-220207_132358.jpg
~/Pictures/screenshot-220207_132400.jpg
~/Pictures/screenshot-220207_132402.jpg
```

## Command Line Help/Usage ##

```
usage: image_snip.py [-h] [--overwrite] [--template] opt_file

Modifies images (crop, resize, and more) and saves the modified versions as
.jpg files. An options (plain text) file is required to specify the process
instructions and list of image files.

positional arguments:
  opt_file     Name of 'options file' containing a list of process
               instructions and image file names, one per line.

optional arguments:
  -h, --help   show this help message and exit
  --overwrite  Overwrite existing output files. By default, existing files are
               not replaced.
  --template   Write available options, as comment lines, to the specified
               options file to use as a template. If the file already exists
               the template comments are appended to the file.
```
