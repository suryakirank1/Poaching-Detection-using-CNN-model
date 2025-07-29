import os
from flask import Flask, render_template, request
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import CategoricalCrossentropy
from twilio.rest import Client
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_folder():
    if request.method == 'POST':
        folder_path = request.form['folder_path']  # Get user input for folder path
        if os.path.exists(folder_path):  # Check if the folder exists
            # Load the machine learning model
            try:
                new_model1 = load_model(r"C:\\Users\\Surya Kiran K\\Desktop\\poachingdetectionVER7.h5", compile=False)
                new_model1.compile(optimizer='adam', loss=CategoricalCrossentropy(reduction='mean'))
            except Exception as e:
                error = f"Error loading model: {e}"
                return render_template('index.html', error=error)

            poacher = False
            person = 0
            noperson = 0

            # SMS INTEGRATION
            try:
                response = requests.get("http://ip-api.com/json/").json()
                message1 = f"The region of poaching is {response['region']} {response['city']} latitude is {response['lat']} longitude is {response['lon']}"
            except requests.exceptions.RequestException as e:
                error = f"Error retrieving location: {e}"
                return render_template('index.html', error=error)

            # Process images in the folder
            for picture in os.listdir(folder_path):
                valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
                if any(picture.endswith(ext) for ext in valid_extensions):
                    testingimg = cv2.imread(os.path.join(folder_path, picture))
                    if testingimg is not None:
                        pic1 = tf.image.resize(testingimg, (256, 256))
                        pic1 = tf.cast(pic1, tf.float32)  # Ensure proper casting
                        solution = new_model1.predict(np.expand_dims(pic1, 0))

                        if solution > 0.5:
                            print(f'Poacher is present warning: {picture}')
                            poacher = True
                            person += 1
                        else:
                            print(f'No poacher is present: {picture}')
                            noperson += 1
                    else:
                        print(f"Error loading image: {picture}")
            
            # Send SMS if poaching is detected
            finalmessage = person > (person + noperson) * 0.10
            outputinscreen = "Poaching is present and SMS regarding poaching is sent to concerned authorities" if finalmessage else "Poaching is not present and animals are safe"

            if finalmessage and poacher:
                SID = "your sid "
                auth_token = "auth token"
        
                target_phone_number = '+phone number'
                messaging_service_sid = 'msg service id generate from twilio '

                try:
                    cl = Client(SID, auth_token)
                    cl.messages.create(body=message1, to=target_phone_number, messaging_service_sid=messaging_service_sid)
                except Exception as e:
                    error = f"Error sending SMS: {e}"
                    return render_template('index.html', error=error)

            return render_template('index.html', prediction=outputinscreen)
        else:
            error = "Folder path does not exist."
            return render_template('index.html', error=error)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
