# -*- coding: utf-8 -*-
"""Salinan dari DATA MINING KEL 6 FIX.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1_bUC0Uip47VE8UOlGGA4AUrWq8ApgcDl
"""

!pip install google-play-scraper
!pip install nltk
!pip install python-crfsuite
!pip install Sastrawi

# Commented out IPython magic to ensure Python compatibility.
# Library untuk mengambil ulasan dari Google Play Store
from google_play_scraper import Sort, reviews

# Library untuk manipulasi data
import numpy as np
import pandas as pd

# Library untuk visualisasi data
import matplotlib.pyplot as plt
import seaborn as sns

# Pengaturan untuk tampilan plot
# %matplotlib inline
plt.style.use('ggplot')
sns.set_style('whitegrid')

## Library untuk preprocessing teks
import csv
import re  # Untuk pencocokan pola teks menggunakan regular expressions
import nltk
import string  # Untuk manipulasi string, seperti menghapus tanda baca
from nltk.corpus import stopwords  # Untuk mengakses kata-kata umum yang biasanya dihapus
from nltk.tokenize import word_tokenize, sent_tokenize  # Untuk tokenisasi kata dan kalimat
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory  # Library stemming Bahasa Indonesia

## Library untuk proses vectorization teks
from sklearn.feature_extraction.text import TfidfVectorizer  # Mengubah teks menjadi TF-IDF
from sklearn.feature_extraction.text import TfidfTransformer  # Transformasi teks menjadi TF-IDF

## Library untuk membangun model klasifikasi
from sklearn.model_selection import train_test_split  # Membagi dataset menjadi data latih dan uji
from sklearn.metrics import classification_report  # Menghasilkan laporan klasifikasi
from sklearn.naive_bayes import MultinomialNB  # Algoritma Naive Bayes untuk data berbentuk count atau TF-IDF
from sklearn.naive_bayes import BernoulliNB  # Algoritma Naive Bayes untuk data biner
from sklearn.naive_bayes import GaussianNB  # Algoritma Naive Bayes untuk data berbasis distribusi Gaussian

## Library untuk evaluasi model
from sklearn.metrics import confusion_matrix  # Untuk membuat matriks kebingungan (confusion matrix)
from sklearn.metrics import accuracy_score  # Untuk menghitung akurasi model

# Mengatur tampilan maksimal kolom data frame di pandas
pd.set_option('max_colwidth', 180)

# Library untuk membuat visualisasi WordCloud
from wordcloud import WordCloud

# Melakukan download library NLTK tambahan
from nltk.corpus import stopwords  # Mengimpor daftar stopwords untuk teks
import nltk
nltk.download('stopwords')  # Mengunduh daftar stopwords NLTK
from nltk.stem import WordNetLemmatizer  # Untuk proses lemmatization
nltk.download('wordnet')  # Mengunduh data wordnet untuk proses lemmatization

# Library untuk memproses file (unggah/unduh)
from google.colab import files

review, continuation_token = reviews(
    'id.bni.wondr',
    lang = 'id',
    country = 'id',
    sort = Sort.NEWEST,
    count = 27000
)

app_reviews_df= pd.DataFrame(review)
app_reviews_df

app_reviews_df.to_csv('wonderbybni_review.csv', index=False)

df = pd.read_csv('wonderbybni_review.csv')
df.head()

df.isnull().sum()

df.dropna(axis=1, inplace=True)

len(df.index)

df.drop(['reviewId'], axis=1, inplace=True)

df.drop(['userName'], axis=1, inplace=True)

df.drop(['userImage'], axis=1, inplace=True)

df.drop(['thumbsUpCount'], axis=1, inplace=True)

df.drop(['at'], axis=1, inplace=True)

df.isnull().sum()

from wordcloud import WordCloud

wc=WordCloud(background_color='white', width=1000, height=1000).generate(' '.join(df['content']))
plt.figure(figsize=(5,5))
plt.imshow(wc)

def clean_text(text):
  # mengubah semua karakter huruf menjadi huruf kecil
  text = text.lower()
  # menghilangkan punctuation
  text = re.sub('@[^\s]+', '', text)
  # menghilangkan angka
  text = re.sub('\d+', '', text)
  # menghilangkan URL
  text = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', text)
  text = re.sub(r'(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w\.-]*)*\/?\s', '', text)
  # menghilangkan Hastag
  text = re.sub(r'#[^\s]+', '', text)
  # menghilangkan Huruf Tunggal
  text = re.sub(r'\b[a-zA-Z]\b', '', text)
  return text

clean = lambda x: clean_text(x)

dfx = pd.DataFrame(df.content.apply(clean))
dfx

positive_lexicon = set(pd.read_csv("positive.tsv", sep="\t", header=None)[0])
negative_lexicon = set(pd.read_csv("negative.tsv", sep="\t", header=None)[0])

def determine_sentiment(text):
  positive_count = sum(1 for word in text.split() if word in positive_lexicon)
  negative_count = sum(1 for word in text.split() if word in negative_lexicon)
  if positive_count > negative_count:
    return "Positive"
  elif positive_count < negative_count:
    return "Negative"
  else:
    return "neutral"

df['sentiment'] = df['content'].apply(determine_sentiment)
df.head()

from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

# Inisialisasi penghapus stopword
factory = StopWordRemoverFactory()
stopword_remover = factory.create_stop_word_remover()

# Fungsi untuk menghapus stopword
def remove_stopwords_sastrawi(text):
    return stopword_remover.remove(text)

# Terapkan ke kolom 'content'
df['content'] = df['content'].apply(remove_stopwords_sastrawi)

def remove_emoji(text):
    # Regular expression untuk mendeteksi emoji
    emoji_pattern = re.compile(
        "[\U00010000-\U0010ffff\U00002000-\U00002BFF\U00003000-\U00003FFF"
        "\U00004000-\U00004FFF\U00005000-\U00005FFF\U00006000-\U00006FFF"
        "\U00007000-\U00007FFF\U00008000-\U00008FFF\U00009000-\U00009FFF"
        "\U0000A000-\U0000AFFF\U0000B000-\U0000BFFF\U0000C000-\U0000CFFF"
        "\U0000D000-\U0000DFFF\U0000E000-\U0000EFFF\U0000F000-\U0000FFFF"
        "\U00010000-\U0010FFFF]", flags=re.UNICODE)

    # Hapus emoji dari teks
    return re.sub(emoji_pattern, '', text)

# Contoh penggunaan:
df['content'] = df['content'].apply(remove_emoji)

df.head()

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

factory = StemmerFactory()
stemmer = factory.create_stemmer()

df['content'] = df['content'].apply(stemmer.stem)

df.to_csv('wonderbybnistemmed.csv', index=False)

df.to_csv('review_wonderbybni.csv', index=False)

"""--------------------------------------------------------------------------------"""

df = pd.read_csv('wonderbybnistemmed.csv')

len(df.index)

df.isnull().sum()

df.dropna(axis=0, inplace=True)

len(df.index)

df.head()

import nltk
nltk.download('punkt_tab')  # Mengunduh tokenizer model

from nltk.tokenize import word_tokenize

# Fungsi untuk tokenisasi
def tokenize_text(text):
    return word_tokenize(text)

# Contoh penggunaan
df['content'] = df['content'].apply(tokenize_text)

df.head()

df['sentiment'].value_counts()

"""**RUN DARI SINI**"""

df = pd.read_csv('sentiment_review.csv')

from sklearn.preprocessing import LabelEncoder

# Misalnya kolom sentiment ada di dataframe df
sentiments = df['sentiment']

# Inisialisasi LabelEncoder
label_encoder = LabelEncoder()

# Transformasikan label menjadi angka
df['sentiment_encoded'] = label_encoder.fit_transform(sentiments)

# Melihat hasil encoding
print(df[['sentiment', 'sentiment_encoded']].head())

# Jika ingin melihat mapping label ke angka
label_mapping = dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_)))
print("Mapping Label ke Angka:", label_mapping)

df.to_csv('sentiment_review_fix.csv', index=False)

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# Misalkan X adalah fitur (content yang sudah diubah menjadi vektor), dan y adalah label (sentiment_encoded)
X = df['content']  # Kolom input teks
y = df['sentiment_encoded']  # Kolom label target (0 atau 1)

# Membagi data menjadi training dan testing set (80% training, 20% testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

from sklearn.feature_extraction.text import TfidfVectorizer

# Inisialisasi TF-IDF Vectorizer
tfidf = TfidfVectorizer(max_features=10000)  # Gunakan 10000 fitur paling signifikan

# Fit dan transform X_train dan transform X_test
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

# Inisialisasi model
nb_model = MultinomialNB()

# Melatih model
nb_model.fit(X_train_tfidf, y_train)

# Prediksi data uji
y_pred = nb_model.predict(X_test_tfidf)

# Evaluasi
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))

df.head()

df['sentiment'].value_counts()

# Hitung value counts dengan persentase
value_counts = df['sentiment'].value_counts(normalize=True) * 100

value_counts

df = pd.read_csv('sentiment_review.csv')

df.isnull().sum()

# Inisialisasi Logistic Regression
lr_model = LogisticRegression(random_state=42)

# Melatih model dengan data training
lr_model.fit(X_train_tfidf, y_train)

# Prediksi pada data uji
y_pred = lr_model.predict(X_test_tfidf)

# Menghitung akurasi
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}")

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:")
print(cm)

# Classification Report (Precision, Recall, F1-score)
print("Classification Report:")
print(classification_report(y_test, y_pred))

from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score

# Inisialisasi SVM dengan linear kernel
svm_model = SVC(kernel='linear', random_state=42)

# Melatih model
svm_model.fit(X_train_tfidf, y_train)

# Prediksi dan evaluasi
y_pred = svm_model.predict(X_test_tfidf)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:")
print(classification_report(y_test, y_pred))

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# Inisialisasi Random Forest
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)

# Melatih model
rf_model.fit(X_train_tfidf, y_train)

# Prediksi dan evaluasi
y_pred = rf_model.predict(X_test_tfidf)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:")
print(classification_report(y_test, y_pred))

!git init
!git remote add origin https://github.com/berlianadr08/streamlit-app.git
!git add .
!git commit -m "Initial commit"
!git branch -M main
!git push -u origin main

!git config --global user.name "berlianadr08"
!git config --global user.email "nimadeberliana812@gmail.com"

!git branch -m main

!git push -u origin main

!git remote -v

!git status

!git add .

!git commit -m "Initial commit"

!git branch -m main

!git push -u origin main

!git init
!git remote add origin https://github.com/berlianadr08/streamlit-app.git
!git add .
!git commit -m "Initial commit"
!git branch -M main
!git push -u origin main

!git remote remove origin
!git remote add origin https://github.com/berlianadr08/streamlit-app.git

!git push https://github.com/berlianadr08/streamlit-app.git

!git remote -v

!git push https://berlianadr08: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@github.com/berlianadr08/streamlit-app.git

!git status

!git add .
!git commit -m "Initial commit"

!git push -u origin main

!pip install streamlit

import streamlit as st

st.title("Streamlit App")
st.write("Aplikasi ini dideploy dari GitHub ke Streamlit!")

import streamlit as st

st.title("Aplikasi Streamlit Anda")
st.write("Selamat datang di aplikasi yang dideploy dari Google Colab!")

# Tambahkan komponen aplikasi lainnya
st.write("Ini adalah aplikasi demo menggunakan Streamlit.")

import os

os.system("pip install google-play-scraper")
