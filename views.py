from django.shortcuts import render

# chat/views.py

import os
import json
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import numpy as np
import re
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Message  # Import the Message model from this app

# --- AI Model Loading ---
MODEL_PATH = os.path.join(settings.BASE_DIR, 'bullying_detection_model.h5')
TOKENIZER_PATH = os.path.join(settings.BASE_DIR, 'tokenizer.pickle')
MAX_LENGTH = 100

model, tokenizer = None, None

try:
    model = tf.keras.models.load_model(MODEL_PATH)
    with open(TOKENIZER_PATH, 'rb') as handle:
        tokenizer = pickle.load(handle)
    print("TensorFlow model and tokenizer loaded successfully.")
except Exception as e:
    print(f"Error loading model or tokenizer: {e}")

# --- AI Preprocessing Function ---
try:
    import nltk
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
except Exception:
    print("NLTK data not available, please run `nltk.download('stopwords')` and `nltk.download('wordnet')`.")
    def preprocess_text(text): return text.lower()

def preprocess_text(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\d+', '', text)
    words = text.split()
    words = [word for word in words if word not in stop_words]
    words = [lemmatizer.lemmatize(word) for word in words]
    return ' '.join(words)


def generate_suggestions(text):
    """Generate a couple of polite alternatives for flagged text.
    This is a lightweight heuristic: replace known profane words with softer synonyms
    and produce a censored version. For production, replace with an LLM or
    a better paraphrasing service.
    """
    # small sample mapping; extend as needed
    # Map common profane/harsh tokens to softer alternatives. Keep these non-abusive.
    synonyms = {
        'idiot': 'unpleasant person',
        'stupid': 'uninformed',
        'ugly': 'unattractive',
        'hate': 'dislike',
        # Do NOT map self-harm words to violent alternatives; handle them specially below.
        'dumb': 'not thoughtful',
        'shut': 'please be quiet',
        'asshole': 'rude person',
        'fuck': 'damn',
        'shit': 'crap',
        'moron': 'uninformed person',
    }

    tokens = text.split()
    # Normalize tokens for lookup
    norm = [t.lower().strip(string.punctuation) for t in tokens]
    # Extended profanity list (small curated set). This is used as a conservative filter
    extra_profanities = {
        'bitch','bastard','dick','crap','damn','ass','fag','retard','slut','whore',
        'idiot','stupid','ugly','hate','dumb','shut','asshole','fuck','shit','moron'
    }

    # Build a unified set of profane tokens we will proactively sanitize
    profanity_keys = set(synonyms.keys()) | extra_profanities

    # Build suggestion 1: replace known profane words with soft synonyms; unknown profane words -> a neutral placeholder
    s1_parts = []
    for t, n in zip(tokens, norm):
        if n in profanity_keys:
            s1_parts.append(synonyms.get(n, 'someone'))
        else:
            s1_parts.append(t)
    s1 = ' '.join(s1_parts)

    # Ensure s1 contains no profane tokens: sanitize any remaining profane words using a neutral placeholder
    s1_tokens = s1.split()
    s1_sanitized = []
    for t in s1_tokens:
        tn = t.lower().strip(string.punctuation)
        if tn in profanity_keys:
            # prefer a synonym if available, otherwise a neutral word
            s1_sanitized.append(synonyms.get(tn, 'someone'))
        else:
            s1_sanitized.append(t)
    s1 = ' '.join(s1_sanitized)

    # suggestion 2: censored/protective version (replace profane tokens with '***') for any profane tokens
    s2_parts = [ ('***' if n in profanity_keys else t) for t, n in zip(tokens, norm) ]
    s2 = ' '.join(s2_parts)
    # suggestion 3: produce a genuinely non-abusive, helpful paraphrase
    lower_tokens = [t.lower().strip(string.punctuation) for t in tokens]
    suicidal_keywords = {'kill', 'suicide', 'die', "kill-yourself", 'killyourself'}
    if any(k in lower_tokens for k in suicidal_keywords):
        # For self-harm content, do NOT echo or paraphrase; provide a concise safety message.
        help_msg = (
            "That sounds serious. If you or someone is at risk, please contact emergency services or a crisis line now."
        )
        return [help_msg, '***', help_msg]

    # Otherwise, return safe alternatives: offer immediate non-abusive paraphrases first,
    # then a sanitized soft-substitution, and finally a censored form.
    polite1 = "This isn't nice — try saying it another way."
    polite2 = "Could you rephrase that more politely?"
    # Return polite paraphrases first to avoid echoing the original abusive text
    return [polite1, polite2, s1, s2]

# --- API views to handle requests ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT"])
def chat_api(request):
    if request.method == 'GET':
        messages = list(Message.objects.values())
        return JsonResponse(messages, safe=False)

    elif request.method == 'POST':
        if not model or not tokenizer:
            return JsonResponse({'error': 'AI model not loaded'}, status=500)

        try:
            data = json.loads(request.body)
            user_text = data.get('text', '')
            force_send = bool(data.get('force', False))

            clean_text = preprocess_text(user_text)
            text_sequence = tokenizer.texts_to_sequences([clean_text])
            text_padded = pad_sequences(text_sequence, maxlen=MAX_LENGTH, padding='post', truncating='post')

            prediction = model.predict(text_padded, verbose=0)[0][0]
            is_abusive = bool(prediction > 0.5)

            if is_abusive and not force_send:
                # return flagged status with suggestions, allow client to present UI to user
                suggestions = generate_suggestions(user_text)
                return JsonResponse({'status': 'flagged', 'is_abusive': True, 'suggestions': suggestions}, status=200)

            # either not abusive or sender forced the send
            new_message = Message.objects.create(
                sender_id=data.get('sender') or data.get('senderId', 'unknown'),
                sender=data.get('sender') or data.get('senderName', 'unknown'),
                text=user_text,
                is_abusive=is_abusive,
                is_starred=data.get('isStarred', False),
            )
            return JsonResponse({'status': 'success', 'id': new_message.id, 'is_abusive': is_abusive}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            message_id = data.get('id')
            if not message_id:
                return JsonResponse({'error': 'Message ID is required'}, status=400)
            
            message = Message.objects.get(id=message_id)
            if 'is_starred' in data:
                message.is_starred = data['is_starred']
            if 'is_reported' in data:
                message.is_reported = data['is_reported']
            message.save()
            return JsonResponse({'status': 'success', 'id': message.id}, status=200)
        except Message.DoesNotExist:
            return JsonResponse({'error': 'Message not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
