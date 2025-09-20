import os
import pickle
import string
import re
import numpy as np

from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow as tf

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'bullying_detection_model.h5')
TOKENIZER_PATH = os.path.join(os.path.dirname(__file__), 'tokenizer.pickle')
MAX_LENGTH = 100

# simple preprocessing roughly matching chat/views.preprocess_text
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    def preprocess_text(text):
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = re.sub(r'\d+', '', text)
        words = text.split()
        words = [word for word in words if word not in stop_words]
        words = [lemmatizer.lemmatize(word) for word in words]
        return ' '.join(words)
except Exception:
    def preprocess_text(text):
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = re.sub(r'\d+', '', text)
        return text

phrases = [
    "You are an idiot",
    "You are stupid",
    "I hate you",
    "Go kill yourself",
    "You're an asshole",
    "Fuck you",
    "You piece of shit",
    "Idiot",
    "moron",
    "I don't like you",
]

print('Loading tokenizer...')
with open(TOKENIZER_PATH, 'rb') as f:
    tokenizer = pickle.load(f)

print('Loading model...')
model = tf.keras.models.load_model(MODEL_PATH)

print('\nDiagnostics:')
for p in phrases:
    clean = preprocess_text(p)
    seq = tokenizer.texts_to_sequences([clean])
    padded = pad_sequences(seq, maxlen=MAX_LENGTH, padding='post', truncating='post')
    pred = float(model.predict(padded, verbose=0)[0][0])
    print(f"Phrase: '{p}'")
    print(f"  Clean: '{clean}'")
    print(f"  Seq: {seq}")
    print(f"  Pred: {pred:.8f}")
    print('')

# Suggest thresholds that would flag at least one phrase
preds = []
for p in phrases:
    clean = preprocess_text(p)
    seq = tokenizer.texts_to_sequences([clean])
    padded = pad_sequences(seq, maxlen=MAX_LENGTH, padding='post', truncating='post')
    preds.append(float(model.predict(padded, verbose=0)[0][0]))

print('Summary predictions:', [round(x,8) for x in preds])
print('Max prediction:', max(preds))
print('If you want these phrases flagged, set ABUSE_THRESHOLD <= max_prediction')
