import functools
from textwrap import dedent
from typing import Generator, List, Optional

import google.generativeai as genai
import googletrans  # type: ignore
from langchain_core.documents.base import Document


@functools.lru_cache
def get_google_ai_model(
    max_output_tokens: Optional[int] = None,
) -> genai.GenerativeModel:
    """
    Get the Google AI model.

    Args
    ----
    max_output_tokens (Optional[int], optional):\
        Maximum number of tokens to generate.\
        If None, the default maximum number of tokens is used.\
        By default None.

    Returns
    -------
    genai.GenerativeModel
        Google AI model.
    """

    generation_config = genai.GenerationConfig(
        max_output_tokens=max_output_tokens,
    )
    return genai.GenerativeModel(
        "gemini-1.5-flash-latest",
        generation_config=generation_config,
    )


def remove_markdown(text: str) -> str:
    """
    Remove markdown from text.

    Args
    ----
    text (str): Text with markdown.

    Returns
    -------
    str
        Text without markdown.
    """

    from bs4 import BeautifulSoup
    from markdown import markdown

    html = markdown(text)
    return "".join(BeautifulSoup(html, "html.parser").findAll(string=True))


def get_page_contents(documents: List[Document]) -> Generator[str, None, None]:
    """
    Get the content of each page in the documents.

    Args
    ----
    documents (List[Document]): List of documents.

    Returns
    -------
    Generator[str, None, None]
        Generator of the content of each page in the documents.
    """
    return (doc.page_content for doc in documents)


def guess_topic_from_weighted_phrases(
    weighted_phrases: str, excluded_topics: List[str] = list()
) -> str:
    """
    Guess the topic from the weighted phrases.

    Args
    ----
    weighted_phrases (str): Weighted phrases.
    excluded_topics (List[str], optional):\
        Excluded topics. This is useful when the topic is\
        already known and should be excluded from the guesses,\
        by default [].

    Returns
    -------
    str
        Guessed topic.
    """
    # Guess the topic from the weighted phrases using the Google AI model
    model = get_google_ai_model(max_output_tokens=5)
    excluded_topics = [topic.lower() for topic in excluded_topics]
    exclude_previous_topics_message = (
        "Don't include these in your guess:\n\n"
        + "\n".join(excluded_topics)
        + "\n\n"
        if excluded_topics
        else ""
    )

    prompt = dedent(
        f"""
        Guess the topic from the following weighted phrases.
        Try to be as specific as possible.
        Reply only with your guess, don't add no boilerplate text.
        {exclude_previous_topics_message}

        Weighted phrases:
        {weighted_phrases}

        Topic:"""
    )

    response = model.generate_content(prompt)

    return response.text


def detect_language(text: str) -> str:
    translator = googletrans.Translator()
    language = translator.translate(text[: min(1000, len(text))]).src

    # map language code to full name
    return googletrans.LANGUAGES[language]
