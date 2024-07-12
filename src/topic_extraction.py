import re
from collections import Counter
from itertools import chain
from typing import List, Tuple

import gensim
import spacy
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel, LdaModel
from gensim.parsing.preprocessing import preprocess_documents


def prepare_corpus(
    documents: List[str],
) -> Tuple:
    # texts = preprocess_documents_with_spacy(documents)
    texts = preprocess_documents(documents)

    # remove words that appear in more than 50% of the documents
    frequency = Counter(chain.from_iterable(texts))

    # remove words that appear in more than 50% of the documents
    texts = [
        [word for word in line if frequency[word] / len(texts) <= 0.5]
        for line in texts
    ]

    # create bigrams
    bigram = gensim.models.Phrases(texts)

    texts = [bigram[line] for line in texts]

    dictionary = Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    return corpus, dictionary, texts


def extract_topics_in_weighted_phrases(
    documents: List[str],
    *,
    number_of_topics: int = 10,
    passes_over_corpus: int = 5
) -> List[str]:
    """
    Extract topics from a list of documents using LDA.

    Args
    ----
    documents : List[str]
        List of documents.
    number_of_topics : int, optional
        Number of topics to extract, by default 10
    passes_over_corpus : int, optional
        Number of passes over the corpus, by default 5

    Returns
    -------
    List[str]
        List of topics, represented as weighted phrases.
    """
    corpus, dictionary, texts = prepare_corpus(documents)

    lda_model = LdaModel(
        corpus,
        id2word=dictionary,
        num_topics=number_of_topics,
        passes=passes_over_corpus,
        # number of workers
    )

    coherence_model_lda = CoherenceModel(
        model=lda_model, texts=texts, dictionary=dictionary, coherence="c_v"
    )
    coherence_lda = coherence_model_lda.get_coherence()
    print(
        "\nFinished training LDA model with coherence score: ", coherence_lda
    )

    topics = lda_model.print_topics(num_words=10)

    weighted_phrases = [topic[1] for topic in topics]

    return weighted_phrases


def preprocess_documents_with_spacy(documents, banned_chars):
    nlp = spacy.load("en_core_web_sm")

    stop_words = nlp.Defaults.stop_words
    for stopword in stop_words:
        lexeme = nlp.vocab[stopword]
        lexeme.is_stop = True

    # remove banned characters
    documents = [re.sub("|".join(banned_chars), "", doc) for doc in documents]

    texts = []
    for doc in documents:
        article = []
        for w in nlp(doc):
            # if it's not a stop word or punctuation mark,
            # add it to our article!
            if (
                w.text != "\n"
                and not w.is_stop
                and not w.is_punct
                and not w.like_num
                and not w.is_space
                and not w.is_currency
                and not w.like_url
                and not w.is_quote
                and not w.is_bracket
                and not w.is_left_punct
                and not w.is_right_punct
                and not w.is_digit
            ):
                # we add the lematized version of the word
                article.append(w.lemma_.lower())
        texts.append(article)
    return documents
