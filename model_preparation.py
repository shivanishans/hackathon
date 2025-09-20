# model_preparation.py

import pandas as pd
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
import numpy as np

# Load the cleaned data you saved from the previous step
df = pd.read_csv('cleaned_data.csv')

# Drop any rows with missing values that might have been created during cleaning
df.dropna(inplace=True)

# Separate the features (text) and the labels (abusive or not)
X = df['clean_text']
y = df['is_abusive']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Set hyperparameters for tokenization
vocab_size = 10000
max_length = 100
oov_token = "<oov>"

# Initialize the tokenizer
tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)

# Fit the tokenizer on the training data
tokenizer.fit_on_texts(X_train)

# Convert the text to sequences of integers
X_train_sequences = tokenizer.texts_to_sequences(X_train)
X_test_sequences = tokenizer.texts_to_sequences(X_test)

# Pad the sequences to a uniform length
X_train_padded = pad_sequences(X_train_sequences, maxlen=max_length, padding='post', truncating='post')
X_test_padded = pad_sequences(X_test_sequences, maxlen=max_length, padding='post', truncating='post')

# Print the shape of the padded sequences to verify
print("Shape of training data:", X_train_padded.shape)
print("Shape of testing data:", X_test_padded.shape)
