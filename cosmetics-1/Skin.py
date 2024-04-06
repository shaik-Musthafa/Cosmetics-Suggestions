import streamlit as st
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model
model = load_model("keras_Model.h5", compile=False)

# Load the labels
class_names = open("labels.txt", "r").readlines()

# Set up the page with a different colorful background
st.markdown(
    """
    <style>
        body {
            background: linear-gradient(45deg, #FFD700, #FF69B4); /* Gradient of Gold and HotPink */
        }
        .main-container {
            background-color: #ffffff; /* White */
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            margin-top: 50px;
        }
        .image-container {
            text-align: center;
            margin-top: 20px;
        }
        .predicted-class {
            font-size: 30px;
            color: #FF4500; /* OrangeRed */
            margin-top: 10px;
        }
        .confidence-score {
            font-size: 20px;
            color: #1E90FF; /* DodgerBlue */
            margin-top: 10px;
        }
        .file-uploader {
            background-color: #FF1493; /* DeepPink */
            color: #ffffff; /* White */
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            cursor: pointer;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title('Skin Image Classification')

# Create file upload option for image classification with a different colorful button
uploaded_image = st.file_uploader("Choose an image for classification", type=["jpg", "jpeg", "png"], key="file_uploader", help="Allowed file types: jpg, jpeg, png",)

# Add a markdown element with the specified class for styling
if uploaded_image is not None:
    image = Image.open(uploaded_image).convert("RGB")

    # Resize the image to be at least 224x224 and then crop from the center
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

    # Turn the image into a numpy array
    image_array = np.asarray(image)

    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

    # Create the array of the right shape to feed into the Keras model
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized_image_array

    # Predict using the image classification model
    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]

    # Display prediction and confidence score with a different colorful design
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<div class="image-container">', unsafe_allow_html=True)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="predicted-class">Predicted Class: {}</div>'.format(class_name[2:]), unsafe_allow_html=True)
    st.markdown('<div class="confidence-score">Confidence Score: {:.2f}</div>'.format(confidence_score), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    