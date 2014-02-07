
import argparse
from skimage import io
import Image
import sys
import os

filename = '/Users/victor/Google Drive/TAP-NY Newsletter Photos/February Newsletter Photos/Skiing.jpg'

def save_image_as(image, saveAs):

    image.save(saveAs, "JPEG")

def rename_image_filename(filename, suffix):
    dirname = os.path.dirname(filename)
    name, ext = os.path.basename(filename).split(".")
    return os.path.join(dirname, name + "_" + suffix + "." + ext)

def scale_width(width, height, new_height):
    return width*new_height/height 

def fit_to_thumbnail(image):
    # 500 x 300
    # rescale to width 500
    width, height = image.size
    new_width = scale_width(width, height, 300)
    image.thumbnail((new_width,300), Image.ANTIALIAS)    
    return image

def fit_to_slider(imagefile):
    # 960 x 395
    # scale to height 395
    # resize to width 960, center
    # make background black
    
    width, height = image.size
    new_width = scale_width(width, height, 395)
    image.thumbnail((new_width, 395), Image.ANTIALIAS)
    newImage = Image.new("RGB", (960, 395))
    left = (960-image.size[0])/2
    newImage.paste(image, (left, 0))
    return newImage


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("function", help="thumbnail | slider")
    parser.add_argument("-i", dest="filename", required=True, help="input image file", metavar="FILE")
    args = parser.parse_args()

    function = args.function
    filename = args.filename
    image = Image.open(filename)
    if function == "slider":
        new_image = fit_to_slider(image)
    elif function == "thumbnail":
        new_image = fit_to_thumbnail(image)
    else:
        print "not valid function: please use thumbnail | slider"
        sys.exit(1)

    save_as = rename_image_filename(filename, function)
    save_image_as(new_image, save_as)

