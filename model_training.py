# model_training.py

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
import pickle

# --- Load the saved data from the previous step ---
df = pd.read_csv('cleaned_data.csv')
X = df['clean_text'].dropna()
y = df['is_abusive'].loc[X.index] # Ensure y matches the cleaned X

# Split data (using the same split to maintain consistency)
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Set hyperparameters (must be the same as in the previous step)
vocab_size = 10000
max_length = 100
oov_token = "<oov>"

# Re-initialize and fit the tokenizer to get the same sequences
tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)
tokenizer.fit_on_texts(X_train)

# Pad the sequences
X_train_padded = pad_sequences(tokenizer.texts_to_sequences(X_train), maxlen=max_length, padding='post', truncating='post')
X_test_padded = pad_sequences(tokenizer.texts_to_sequences(X_test), maxlen=max_length, padding='post', truncating='post')

# --- Build the Model ---
embedding_dim = 16
model = Sequential([
    Embedding(vocab_size, embedding_dim, input_length=max_length),
    Bidirectional(LSTM(64, return_sequences=True)),
    Bidirectional(LSTM(32)),
    Dropout(0.5),
    Dense(64, activation='relu'),
    Dropout(0.5),
    Dense(1, activation='sigmoid')
])

# Compile the model
model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

# Print a summary of the model's architecture
model.summary()

# --- Train the Model ---
num_epochs = 10
history = model.fit(
    X_train_padded,
    y_train,
    epochs=num_epochs,
    validation_data=(X_test_padded, y_test),
    verbose=1
)

# --- Save the trained model and the tokenizer ---
# Save the model
model.save('bullying_detection_model.h5')

# Save the tokenizer
with open('tokenizer.pickle', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

print("\nModel and tokenizer saved successfully.")
