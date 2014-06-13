
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

def fit_to_thumbnail(image, width=500, height=300):
    # 500 x 300
    # rescale to width 500
    image.resize((width, height), Image.ANTIALIAS)    
    return image

def fit_to_slider(image, w=960, h=395):
    # 960 x 395
    # scale to height 395
    # resize to width 960, center
    # make background black
    
    width, height = image.size
    print "image size", image.size
    new_width = scale_width(width, height, h)
    image.thumbnail((new_width, h), Image.ANTIALIAS)
    newImage = Image.new("RGB", (w, h))
    left = (w-new_width)/2
    top = 0
    if h > height:
        print "image too small, resizing height"
        top = (h-height)/2
        image.resize((new_width, h), Image.ANTIALIAS)
    newImage.paste(image, (left, top))
    return newImage


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("function", help="thumbnail | slider")
    parser.add_argument("-i", dest="filename", required=True, help="input image file", metavar="FILE")
    parser.add_argument("-H", dest="height", type=int, default=395, required=False, help="height of new image")
    parser.add_argument("-W", dest="width", type=int, default=960, required=False, help="width of new image")
    args = parser.parse_args()

    function = args.function
    filename = args.filename
    height = args.height
    width = args.width
    image = Image.open(filename)
    if function == "slider":
        if height and width:
            new_image = fit_to_slider(image, width, height)
        else:
            new_image = fit_to_slider(image)
    elif function == "thumbnail":
        if height and width:
            new_image = fit_to_thumbnail(image, width, height)
        else:
            new_image = fit_to_thumbnail(image)
    else:
        print "not valid function: please use thumbnail | slider"
        sys.exit(1)

    save_as = rename_image_filename(filename, function)
    save_image_as(new_image, save_as)

