# -*- coding: utf-8 -*-
"""HW1-CSCI544.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LZCmYBj_NelvPZBNAind85nv946rb9Kl
"""

# ! pip install bs4 # in case you don't have it installed
# ! pip install contractions
# # Dataset: https://s3.amazonaws.com/amazon-reviews-pds/tsv/amazon_reviews_us_Beauty_v1_00.tsv.gz

# from google.colab import drive
# drive.mount('/content/drive')

import pandas as pd
import numpy as np
import nltk
import re
from bs4 import BeautifulSoup
# import os
# os.chdir('/content/drive/Shared drives/USC_CSCI544-Applied NLP/HWs/HW1') # where the files for this project are

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report
from sklearn.linear_model import Perceptron, LogisticRegression
from sklearn.svm import SVC
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('omw-1.4')
nltk.download('averaged_perceptron_tagger')

"""## Read Data"""

df=pd.read_table('amazon_reviews_us_Office_Products_v1_00.tsv', on_bad_lines='skip')

"""## Keep Reviews and Ratings"""

df = df[['review_body', 'star_rating']]

""" ## We form three classes and select 20000 reviews randomly from each class.


"""

## Create three class labels

df['star_rating'] = pd.to_numeric(df['star_rating'], errors='coerce')

# df['sentiment'] = np.where(df['star_rating'] <= 2, 0,  # Negative: 0
#                           np.where(df['star_rating'] > 3, 2, 1))  # Positive: 2, Neutral: 1

df = df.dropna(subset=['review_body'], how='all')

df['sentiment'] = np.where(df['star_rating'] > 3, 1, 0)  # Positive: 1, Negative: 0

# Print review counts per class
print("Before Discard")
print("Number of positive reviews:", df[df['sentiment'] == 1].shape[0])
print("Number of negative reviews:", df[df['sentiment'] == 0].shape[0])
print("Number of neutral reviews (discarded):", len(df[df['star_rating'] != 3]))

df = df[df['star_rating'] != 3]  # Discard neutral reviews (rating 3)

# Print review counts per class
print("\n\nAfter Discard")
print("Number of positive reviews:", df[df['sentiment'] == 1].shape[0])
print("Number of negative reviews:", df[df['sentiment'] == 0].shape[0])
print("Number of neutral reviews (discarded):", len(df[df['star_rating'] == 3]))

# Randomly select 20,000 positive reviews
positive_reviews = df[df['sentiment'] == 1].sample(100000, random_state=42)

# Randomly select 20,000 negative reviews
negative_reviews = df[df['sentiment'] == 0].sample(100000, random_state=42)

# Concatenate the selected reviews to form the downsized DataFrame
downsized_df = pd.concat([positive_reviews, negative_reviews])

# # Print the first few rows of the downsized DataFrame
# print("Downsized DataFrame:")
# print(downsized_df.head())

## Print review counts per class
print("Number of positive reviews:", downsized_df[downsized_df['sentiment'] == 1].shape[0])
print("Number of negative reviews:", downsized_df[downsized_df['sentiment'] == 0].shape[0])
print("Number of neutral reviews (discarded):", len(downsized_df[downsized_df['star_rating'] == 3]))

"""# Data Cleaning

# Pre-processing

## perform lemmatization, remove stop words, tokenize etc
"""

def clean_text(text):
    # Remove HTML tags
    if isinstance(text, str) and text:
      soup = BeautifulSoup(text, 'html.parser')
      text = soup.get_text()

      # Remove special characters and digits
      text = re.sub(r'[^a-zA-Z\s]', '', text)

      # Remove URLs
      text = re.sub(r'https?://\S+', '', text)

      # Convert to lowercase
      text = text.lower()

      # Tokenize
      words = nltk.word_tokenize(text)

      # Remove stop words
      stop_words = set(nltk.corpus.stopwords.words('english'))
      words = [word for word in words if word not in stop_words]

      # Lemmatize
      lemmatizer = WordNetLemmatizer()
      words = [lemmatizer.lemmatize(word) for word in words]

      return ' '.join(words)
    else:
      return ''  # Return an empty string for empty or non-string inputs

downsized_df['clean_review'] = downsized_df['review_body'].apply(clean_text)

# Print the average length of the cleaned reviews
print("Average length of cleaned reviews:", downsized_df['clean_review'].str.len().mean())

"""# TF-IDF Feature Extraction"""

tfidf_vectorizer = TfidfVectorizer()
X = tfidf_vectorizer.fit_transform(downsized_df['clean_review'])
y = downsized_df['sentiment']

# shape of the feature matrix
print("Shape of feature matrix (X):", X.shape)

## Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

"""# Perceptron"""

perceptron_classifier = Perceptron(max_iter=1000)
perceptron_classifier.fit(X_train, y_train)
y_pred_perceptron = perceptron_classifier.predict(X_test)
print("Perceptron Accuracy:", accuracy_score(y_test, y_pred_perceptron))
print("Perceptron Classification Report:\n", classification_report(y_test, y_pred_perceptron))

"""# Logistic Regression"""

logreg_classifier = LogisticRegression(multi_class='ovr')  # Handle multi-class classification
logreg_classifier.fit(X_train, y_train)
y_pred_logreg = logreg_classifier.predict(X_test)
print("Logistic Regression Accuracy:", accuracy_score(y_test, y_pred_logreg))
print("Logistic Regression Classification Report:\n", classification_report(y_test, y_pred_logreg))

"""# Naive Bayes"""

nb_classifier = MultinomialNB()
nb_classifier.fit(X_train, y_train)
y_pred_nb = nb_classifier.predict(X_test)
print("Naive Bayes Accuracy:", accuracy_score(y_test, y_pred_nb))
print("Naive Bayes Classification Report:\n", classification_report(y_test, y_pred_nb))

"""# SVM"""

svm_classifier = SVC(kernel='linear')
svm_classifier.fit(X_train, y_train)
y_pred_svm = svm_classifier.predict(X_test)
print("SVM Accuracy:", accuracy_score(y_test, y_pred_svm))
print("SVM Classification Report:\n", classification_report(y_test, y_pred_svm))