from flask import Flask, render_template, request, send_from_directory
import os
from PIL import Image

app = Flask(__name__)

# Define the upload and processed image directories
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed_images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["PROCESSED_FOLDER"] = PROCESSED_FOLDER

# Function to process an image (pipeline)
from rembg import remove
from PIL import Image, ImageChops, ImageOps
def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    #Bounding box given as a 4-tuple defining the left, upper, right, and lower pixel coordinates.
    #If the image is completely empty, this method returns None.
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)

def process_image(im):
  # Open the input image
  input_image = Image.open(im)

  # Remove the background
  nobg_image = remove(input_image)

  #Trim blank areas
  trimmed = trim(nobg_image)

  # Contain the image in a box of size 1024
  contained_im = ImageOps.contain(trimmed, (1048,1048))
  return contained_im

'''
def process_image(image_path):
    img = Image.open(image_path)
    img_resized = img.resize((300, 300))  # Resize the image to 300x300
    return img_resized
'''

@app.route("/", methods=["GET", "POST"])
def upload_and_process():
    if request.method == "POST":
        # Get uploaded files
        uploaded_files = request.files.getlist("file")
        processed_image_filenames = []

        # Process each uploaded image
        for file in uploaded_files:
            if file.filename != "":
                # Save the uploaded image temporarily
                filename = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                file.save(filename)

                # Process the image
                processed_image = process_image(filename)

                # Save the processed image
                basename,ext = os.path.splitext(file.filename)
                processed_filename = os.path.join(app.config["PROCESSED_FOLDER"], basename + '.png')
                processed_image.save(processed_filename)
                processed_image_filenames.append(basename + '.png')

                # Clean up temporary files
                os.remove(filename)

        return render_template("download.html", processed_image_filenames=processed_image_filenames)
    return render_template("upload.html")

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(app.config["PROCESSED_FOLDER"], filename)

if __name__ == "__main__":
    app.run(debug=True)
