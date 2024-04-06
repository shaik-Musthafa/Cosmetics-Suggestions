import streamlit as st
from datetime import datetime
import cv2
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
import numpy as np
from tensorflow.keras.models import load_model
import os


##ef write_data_to_excel(k):
    #$f=open('attendance.csv','a')
    #dummy=str(datetime.now())
    #dummy=dummy.split(' ')
    #f.writelines([k+',',dummy[0]+',',dummy[1].split('.')[0]+'\r\n'])
    #f.close()

st.title('skin type cosmetic recomendation system')
run=st.checkbox('Run Camera')

FRAME_WINDOW=st.image([])
camera=cv2.VideoCapture(0)
#student_paths=os.listdir('students/')
#client=boto3.client('rekognition',aws_access_key_id=accessKey,aws_secret_access_key=secretAccessKey,region_name=region)

while run:
    _,frame=camera.read()
    frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    FRAME_WINDOW.image(frame)
    
    cv2.imwrite('./uploads/test.jpg',frame)
    #for i in student_paths:
       # imageSource=open('test.jpg','rb')
        #imageTarget=open('students/'+i,'rb')
        #response=client.compare_faces(SimilarityThreshold=70,SourceImage={'Bytes':imageSource.read()},TargetImage={'Bytes':imageTarget.read()})
        #st.write(response)
        # if response['FaceMatches']:
        #     result=i.split('.')[0]
        #     st.success('Face Identified as ' + result)
        #     write_data_to_excel(result)
        #     st.write('Your attendance Recorded, please do uncheck the box')
        #     st.write('Thank You')
        #     run=False
        #     break

    run=False
    break


model = load_model("keras_model.h5", compile=False)

# Load the labels
class_names = open("labels.txt", "r").readlines()

def model_predict(img_path, model,class_names):
    # Load and preprocess the image
    image = Image.open(img_path).convert("RGB")
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized_image_array
    
    # Make prediction
    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]
    
    return class_name[2:], confidence_score

c,cd=model_predict('./uploads/test.jpg',model,class_names)
print(c)