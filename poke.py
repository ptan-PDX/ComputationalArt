import requests
import pyrebase
from PIL import Image
from urllib.request import urlopen
import io
config = {
    "apiKey": "AIzaSyC4pPPvGTTMpXnFogm6f71JOxNg3wSL2wk",
    "authDomain": "style-playground.firebaseapp.com",
    "databaseURL": "https://style-playground.firebaseio.com",
    "projectId": "style-playground",
    "storageBucket": "style-playground.appspot.com",
    "messagingSenderId": "213787329993",
    "appId": "1:213787329993:web:4b6220c697de9ad4c75418"
}
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()

for i in range(200, 215):
    input_url = f'https://raw.githubusercontent.com/HybridShivam/Pokemon/master/assets/images/{i}.png'
    r = requests.post(
        "https://api.deepai.org/api/fast-style-transfer",
        data={
            'content': input_url,
            'style': 'https://firebasestorage.googleapis.com/v0/b/style-playground.appspot.com/o/results%2FStarry-Night-Van-Gogh-Which-Stars-GoogleArtProject.jpg?alt=media&token=751726f1-c426-482e-8148-a93bc9074573',
        },
        headers={'api-key': '88871471-feb8-4eb7-adec-7e3da5d954dd'}
    )
    image_file_path = f'result_images/{i}.png'
    re = requests.get(r.json()['output_url'], timeout=4.0)
    if re.status_code != requests.codes.ok:
        assert False, 'Status code error: {}.'.format(r.status_code)

    with Image.open(io.BytesIO(re.content)) as im:
        im.save(image_file_path)
    # print(r.json()['output_url'])
    #img = Image.open(urlopen(r.json()['output_url']))
    imgurl = storage.child(f'results/{i}.png').put(image_file_path)
    print(f'done with {i}')
