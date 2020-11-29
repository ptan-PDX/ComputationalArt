from flask import Flask, request, render_template, send_from_directory, redirect
from flask import abort, redirect, url_for
import requests
import os
import pyrebase

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# Import and register colorhar_page Blueprint. Blueprint is a concept in Flask, which is used to create components in an application.
from color import colorhar_page
app.register_blueprint(colorhar_page)

# Config firebase database which is used in Style Transfer.
config = {
    "apiKey": "AIzaSyC4pPPvGTTMpXnFogm6f71JOxNg3wSL2wk",
    "authDomain": "style-playground.firebaseapp.com",
    "databaseURL": "https://style-playground.firebaseio.com",
    "projectId": "style-playground",
    "storageBucket": "style-playground.appspot.com",
    "messagingSenderId": "213787329993",
    "appId": "1:213787329993:web:4b6220c697de9ad4c75418"
}

# FLASK_ENV=development FLASK_APP=app.py python -m flask run
firebase = pyrebase.initialize_app(config)

# Firebase storage for Style Transfer.
storage = firebase.storage()


@app.route('/')
@app.route('/home')
def home():
    kwargs = {
        'title': 'Home',
        'jumbotron': {
            "header": "Image Playground",
            "bg_image": url_for('static', filename='/images/bg1450496.jpg'),
            "text": " "
        },
        'homePageContents': [{
            'Title': "Style Transer",
            "Text": "Neural Style Transfer (NST) refers to a class of software algorithms that manipulate digital images, or videos, in order to adopt the appearance or visual style of another image. NST algorithms are characterized by their use of deep neural networks for the sake of image transformation. Common uses for NST are the creation of artificial artwork from photographs, for example by transferring the appearance of famous paintings to user-supplied photographs. Several notable mobile apps use NST techniques for this purpose, including DeepArt and Prisma. This method has been used by artists and designers around the globe to develop new artwork based on existent style(s). --Wikipedia Neural Style Transfer",
            "imagePath": url_for('static', filename='/images/styleTransfer.jpeg'),
            "Link": "/styletransfer",
            "Action": "+ Go Style Transfer"
        },
            {
            "Title": "Color Harmonization",
            "Text": "In color theory, color harmony refers to the property that certain aesthetically pleasing color combinations have. These combinations create pleasing contrasts and consonances that are said to be harmonious. These combinations can be of complementary colors, split-complementary colors, color triads, or analogous colors. Color harmony has been a topic of extensive study throughout history, but only since the Renaissance and the Scientific Revolution has it seen extensive codification. Artists and designers make use of these harmonies in order to achieve certain moods or aesthetics.--Wikipedia Neural Style Transfer",
            "imagePath": url_for('static', filename='/images/colorHar.png'),
            "Link": "/colorhar",
            "Action": "+ Go Color Harmonization"
        },
            {
            "Title": "Gallery",
            "Text": "In our Gallery, you can look at style transfer and color harmonization products.",
            "imagePath": url_for('static', filename='/images/gallery.png'),
            "Link": "/gallery",
            "Action": "+ Go to gallery"
        }
        ]
    }
    return render_template('home.html', **kwargs)


img_url_global = ''
@app.route("/styletransfer", methods=['GET', 'POST'])
def styletransfer():
    global img_url_global
    kwargs = {
        'title': 'Style Transfer',
        'jumbotron': {
            "header": "Style Transfer",
            "bg_image": "static/images/styleTransfer.jpeg",
            "text": "Research paper: https://openaccess.thecvf.com/content_cvpr_2016/papers/Gatys_Image_Style_Transfer_CVPR_2016_paper.pdf"

        }
    }
    if request.method == 'POST':
        formid = request.args.get('formid', 1, type=int)

        if formid == 2:
            filename = request.form['image']
            r = requests.post(
                "https://api.deepai.org/api/fast-style-transfer",
                data={
                    'content': img_url_global,
                    'style': 'https://firebasestorage.googleapis.com/v0/b/style-playground.appspot.com/o/results%2FStarry-Night-Van-Gogh-Which-Stars-GoogleArtProject.jpg?alt=media&token=751726f1-c426-482e-8148-a93bc9074573',
                },
                headers={'api-key': '88871471-feb8-4eb7-adec-7e3da5d954dd'}
            )
            print(r.json()['output_url'])
            return render_template('styletransfer.html', **kwargs, image_name=filename, result_image_name=r.json()['output_url'])
            # return send_image('temp.png')
        else:
            target = os.path.join(APP_ROOT, 'static/images/')

            # create image directory if not found
            if not os.path.isdir(target):
                os.mkdir(target)

            # retrieve file from html file-picker
            upload = request.files.getlist("file")[0]
            print("File name: {}".format(upload.filename))
            filename = upload.filename

            # file support verification
            ext = os.path.splitext(filename)[1]
            if (ext == ".jpg") or (ext == ".png") or (ext == ".bmp"):
                print("File accepted")
            else:
                return render_template("error.html", message="The selected file is not supported"), 400

            # save file
            destination = "/".join([target, filename])
            print("File saved to to:", destination)
            upload.save(destination)
            #path_on_cloud = "user_upload/foo.jpg"
            path_local = destination
            imgurl = storage.child(f'user_upload/{filename}').put(path_local)
            img_url = storage.child(
                f'user_upload/{filename}').get_url(imgurl['downloadTokens'])
            img_url_global = img_url
            print(f'imagge global is {img_url_global}')
            print(f'imagge currently got  is {img_url}')
            return render_template('styletransfer.html', **kwargs, image_name=img_url)
    return render_template('styletransfer.html', **kwargs)


@app.route("/gallery")
def gallery():
    response = requests.get('https://restcountries.eu/rest/v2/all')
    kwargs = {
        'title': 'Gallery',
        'jumbotron': {
            "header": "Computational Art Gallery",
            "bg_image": "static/images/bg1450496.jpg",
            "text": "Style Transfer selected images from PokéAPI"

        },
        'recipes': response.json()
    }
    return render_template('gallery.html', **kwargs)


@app.route('/about')
def about():
    kwargs = {
        'title': 'About',
        'jumbotron': {
            "header": "AI & Art",
            "bg_image": "static/images/bg1450496.jpg",
            "text": ""
        },
        'aboutPageContents': [{
            'Title': "AI & Art",
            "Text": " Text for AI & Art"

        },
            {
            "Title": "References",
            "Text": " "

        },
            {
            "Title": "Thanks",
            "Text": ""

        }
        ]
    }
    return render_template('about.html', **kwargs)
