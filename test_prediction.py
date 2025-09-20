# test_prediction.py

import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import numpy as np

# Load the saved model and tokenizer
model = tf.keras.models.load_model('bullying_detection_model.h5')
with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

# Set the same hyperparameters
max_length = 100

def predict_message(message):
    # Preprocess the message (you can reuse the preprocess_text function)
    # For now, we'll keep it simple:
    message_sequence = tokenizer.texts_to_sequences([message])
    message_padded = pad_sequences(message_sequence, maxlen=max_length, padding='post', truncating='post')

    # Get the prediction
    prediction = model.predict(message_padded)[0][0]

    # Return the prediction and a user-friendly label
    if prediction > 0.5:
        return f"Abusive ({prediction:.2f})"
    else:
        return f"Not Abusive ({prediction:.2f})"

# Test some example messages
print(f"Message: 'You are so mean!' -> Prediction: {predict_message('You are so mean!')}")
print(f"Message: 'I hope you have a great day.' -> Prediction: {predict_message('I hope you have a great day.')}")
print(f"Message: 'You look so ugly.' -> Prediction: {predict_message('You look so ugly.')}")
