# image_snip

**image_snip.py** is a command-line utility for applying the same crop and/or zoom operations to a batch of image files. It could be a *batch-of-one*, but why not just use an image editor like Photoshop or GIMP for that?

This Python program evolved from a one-off utility script used to process batches of images where the same areas were cropped. The original script started with hard-coded paths. Later an *options file* was added so the a set of operations could be applied to different sets of image files.

This is a limited application of Python and [Pillow](https://pypi.org/project/pillow/). There are other, more powerful, options available for scripted image processing (such as [Automating GIMP](https://www.gimp.org/tutorials/legacy/Automate_Editing_in_GIMP/)).


## Options File

The options file contains the following sections:

- **Settings** (settings override defaults and are optional)
- **Process Instructions** (at least one process instruction is required)
- **Image list** (one or more image file names)

Any line starting with a pound sign (**#**) is treated as a **comment**. Only whole-line comments are supported.

### Settings

The following **Settings** can be specified in the options file:

`output_folder:` *folder-path*

Save the modified images to the given folder path.

---

`new_name:` *base-file-name*

Give files a new name, instead of keeping the original file name in the output. If there is more than one file, a file number will be added after the base file name.

`new_name: *`

If the `new_name:` option is set to an asterisk, then the original file name is kept, without "*-crop*" appended.

---

`output_format:` *JPG* or *PNG*


Save the modified images with a different format than the original (`JPG` or `PNG` are supported).

---

`timestamp_mode:` *[n]*


Add a *date_time* tag to the output file name. The setting value specifies the resolution of the time part:

`1` = Add *date_time* to the second.
`2` = Add *date_time* to the microsecond.

If no *timestamp_mode* is specified, the output file is named with "*-crop*" appended to the source file name.


### Process Instructions

The following **Process Instructions** can be specified in the options file:

`crop_from_center(width, height)`

`crop_from_left_bottom(width, height)`

`crop_from_left_top(width, height)`

`crop_from_right_bottom(width, height)`

`crop_from_right_top(width, height)`

These crop the image to the given *width* and *height* (in pixels) starting from the corner (or center) as stated in the instruction's name.


---

`crop_to_box(x1, y1, x2, y2)`

Crop from any part of the image using the given [box coordinates](https://pillow.readthedocs.io/en/stable/handbook/concepts.html#coordinate-system):

---

`crop_zoom(width, height)`

Resize (zoom) the image to fill the entire target area, then crop to the given *width* and *height*:

---

`border(width)`

Add a border with a given width in pixels (default color):


---

`border(width, red, green, blue)`

Add a border with a given width in pixels and a specified RGB color:

---

`rounded(radius, padding)`

Round the corners with the given radius and padding (pixels) and a transparent background:

---

`rounded(radius, padding, red, green, blue)`

Round the corners with the given radius and padding (pixels) and a specified RGB background color:

---

`animated_gif(duration)`

Create an animated GIF using all images with the given display *duration* (in milliseconds) for each frame. The GIF file is created after all other instructions have been applied to the list of images, and the modified versions of those images have been saved. It is given the same file name as the last image in the list but with a *.gif* extension.

---

`text_footers("font-file-name", font-size, numbering)`

Add a text footer (caption):

**font-file-name** must be the name of a font that is available on the system.

**font-size** is an integer.

**numbering:** is an integer specifying one of the following options:
0 = No numbering
1 = Append the image number to caption.
2 = Append the image number / total images to caption.

To add a **Caption**, put the text on the line above an image file name and begin that line with a `>` (greater than) character. The caption is applied to all subsequent images until another caption, or a line with only a `>` (blank caption) is encountered.

### Example options file:

```
#  options-1.txt

output_folder: ./output

new_name: my-cropped-image

timestamp_mode: 1

crop_from_left_bottom(1920, 500)
crop_from_right_bottom(700, 500)
crop_to_box(100, 100, 500, 400)
crop_zoom(600, 600)

./images/example-1-1920x1440.jpg
```

The set of one or more *process instructions* are applied to each image listed in the options file. The example above has only one image, but the original use-case for this tool had many images to which the same operations were applied. Also, the series of process instructions is just an example of combining multiple instructions. It is not a useful combination. In practice, only one or two operations are needed (perhaps one kind of *crop* and maybe a *zoom*).

With the `new_name` option, the first part of the output file name will be *my-cropped-image* instead of *example-1-1920x1440*.


**Example including animated GIF and captions:**

```
#  options-2.txt

output_folder: ./output

crop_to_box(416, 90, 1370, 530)

# Add text footers for captions.

text_footers("LiberationMono-Bold.ttf", 16, 2)

# Make an animated GIF with frame duration of 2 seconds (2000 ms).

animated_gif(2000)

> Step 1: Open the application.
~/Pictures/screenshot-220207_132358.jpg

> Step 2: Do the thing with the stuff.
~/Pictures/screenshot-220207_132400.jpg

> Step 3: Save the work.
~/Pictures/screenshot-220207_132402.jpg
```

## Command Line Help / Usage

```
usage: image_snip [-h] [-o] [-t] opt_file

Modifies images (crop, resize, and more) and saves the modified versions as
.jpg files. An options (plain text) file is required to specify the process
instructions and list of image files.

positional arguments:
  opt_file         Name of 'options file' containing a list of process
                   instructions and image file names, one per line.

options:
  -h, --help       show this help message and exit
  -o, --overwrite  Overwrite existing output files. By default, existing
                   output files are not replaced. Does not allow overwriting
                   original files.
  -t, --template   Write available options, as comment lines, to the specified
                   options file to use as a template. If the file already
                   exists the template comments are appended to the file.
```
