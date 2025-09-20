# data_preprocessing.py

import pandas as pd
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# --- Part 1: Load and Create Abusive Column ---
# Make sure your 'train.csv' is in the same directory as this file
df = pd.read_csv('train.csv')

# Create a single 'is_abusive' column from all toxic labels
df['is_abusive'] = df['toxic'] + df['severe_toxic'] + df['obscene'] + df['threat'] + df['insult'] + df['identity_hate']
df['is_abusive'] = df['is_abusive'].apply(lambda x: 1 if x > 0 else 0)

# Keep only the text and the new label column
df = df[['comment_text', 'is_abusive']]

# --- Part 2: Preprocess the Text ---
# Download necessary NLTK data (do this once)
nltk.download('stopwords')
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    # Your preprocessing function goes here (lowercase, remove punctuation, etc.)
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\d+', '', text)
    words = text.split()
    words = [word for word in words if word not in stop_words]
    words = [lemmatizer.lemmatize(word) for word in words]
    return ' '.join(words)

# Apply the preprocessing function
df['clean_text'] = df['comment_text'].apply(preprocess_text)

# Display the final, cleaned data
print(df.head())
print("\nDataFrame size:", df.shape)

# You can save the cleaned data for later use if you want
df.to_csv('cleaned_data.csv', index=False)
