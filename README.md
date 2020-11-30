# ComputationalArt

# Computational Art Studio

Computational Art Studio written in Python, using Flask framework and Deep AI style transfer API for image processing: 1. Style Transfer 2. Color Harmonization 3. Gallery of Style Transfer.

For a live demo, please visit this
[link](https://computationalartstudio.herokuapp.com/). The App has been deployed to Heroku.

## Getting started

This project includes three Python files:

- `app.py`: for route to different pages and style transfer and gallery function.
- `color.py`: Blueprint (or module) for color harmonization function. Process GET request and return color harmonization page. Process POST request to harmonize the image user upload.
- `wheel.py`: A color harmonization API written in Python. Please check this research paper [link](https://igl.ethz.ch/projects/color-harmonization/harmonization.pdf) for more details about color harmonization.
- `templates`: Jinja2 html templates.
- `static/colorhar_results`: uploads folder to store images user will upload for color harmonization. results folder to store result images of color harmonization.

Other files have been included for Heroku deployment: `requirements.txt`, `Aptfile`and `Procfile`.

## Dependencies

`flask` with its dependencies (`werkzeug`, `jinja2`, `markupsafe`, `itsdangerous`), It is recommended to use the provided `requirements.txt` file:

```
sudo pip install -r requirements.txt
```

## Web application

To test the app locally, run `flask run` and then you will find a link in your console, use ctrl + click to open that link in your browser.

Use the `Browse` button to upload the desired image.

If successful, you will be able to preview your uploaded image on the same page.

- For color harmonization, your uploaded image and the processed image will be provided to you at the same time.

- For Style transfer, you will see a button show up along with your uploaded image, and then you can click on that button, and after about 15 seconds, you will see the result image(Your uploaded image in Van Gogh Starry Night style).

- In the Gallery page, you will see 30 pokemon images in Van Gogh Starry Night style.

## Issues

Report any issue to the GitHub issue tracker.

## Thanks

Image-api [link](https://github.com/gxercavins/image-api)
Deep AI: https://deepai.org/machine-learning-model/fast-style-transfer
Flask official documentation
Jinja2 documentation
Bootstrap

## Inspiration

Google Arts & Culture [link](https://artsandculture.google.com/)
How old do I look [link](https:www.how-old.net/)
Make Me zombie [link](http://makemezombie.com/)
