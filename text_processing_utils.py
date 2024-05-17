from typing import Container, Optional, Sequence
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer
import gensim
import argparse
import functools
import transformers
import torch


def tokenize_text(text: str) -> list[str]:
    return word_tokenize(text)


def lemmatize_token(text: str, pos: str = "v") -> str:
    lemmatizer = WordNetLemmatizer()
    return lemmatizer.lemmatize(text, pos)


def stem_token(text: str) -> str:
    stemmer = PorterStemmer()
    return stemmer.stem(text)


def remove_stopwords(text):
    stop_words = set(stopwords.words("english"))
    word_tokens = tokenize_text(text)
    filtered_text = [word for word in word_tokens if word.lower() not in stop_words]
    return " ".join(filtered_text)


def process_text(text: str) -> list[str]:
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS:
            result.append(lemmatize_token(stem_token(token)))

    return result
