
import os
from flask import Flask, render_template, Blueprint, request
from wheel import harmonize_image

colorhar_page = Blueprint('colorhar_page', __name__,
                          template_folder='templates')

ALLOWED_EXTENSIONS = set(['.png','.jpg','.jpeg','.gif'])

@colorhar_page.route('/colorhar', methods=['GET', 'POST'])
def colorhar():
    kwargs = {
        'title': 'Color Harmonization',
        'jumbotron': {
            "header": "Color Harmonization",
            "bg_image": "static/images/colorHarJ.png",
            "text": "Add text"
        }
    }

    if request.method == 'GET':
        return render_template('colorhar.html', **kwargs)
    elif request.method == 'POST':
        uploads_dir = "static/colorhar_results/uploads/"
        results_dir = "static/colorhar_results/results/"

        # create image directory if not found
        if not os.path.isdir(uploads_dir):
            os.mkdir(uploads_dir)

        # retrieve file from html file-picker
        upload = request.files.getlist("file")[0]
        print("File name: {}".format(upload.filename))
        filename = upload.filename

        # file support verification
        ext = os.path.splitext(filename)[1]
        print("ext=", ext)
        if ext in ALLOWED_EXTENSIONS:
            print("File accepted")
        else:
            return render_template("error.html", message="The selected file is not supported"), 400

        # save file
        destination = os.path.join(uploads_dir, filename)
        print("File saved to to:", destination)
        upload.save(destination)
        kwargs['image_name'] = destination
        print("destination=", destination)

        image_fpath_harmonized = os.path.join(results_dir, filename)
        har_result = harmonize_image(destination, image_fpath_harmonized)
        kwargs['result_image_name']= image_fpath_harmonized
        kwargs.update(har_result)

        return render_template('colorhar.html', **kwargs)
