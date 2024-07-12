from textwrap import dedent
import functools
import re
from typing import Generator, List, Optional
from langchain_core.documents.base import Document
import google.generativeai as genai
from nltk.tokenize import sent_tokenize
import nltk


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


def extract_questions(llm_response: str, negative_response: str) -> List[str]:
    """
    Extract questions from the LLM response.

    Args
    ----
    llm_response (str): LLM response.
    negative_response (str): Text to
        check if the response is negative.

    Returns
    -------
    List[str]
        List of questions extracted from the LLM response.
    """
    # check if the response is negative
    if negative_response.lower() in llm_response.lower():
        return []

    llm_response_no_markdown = remove_markdown(llm_response)

    # remove newlines
    llm_response_no_boiler_plate = llm_response_no_markdown.replace(":\n\n", ".\n")

    # remove "(...)" at the end of lines
    llm_response_no_references = re.sub(
        r"\(.*\) *\n+", "", llm_response_no_boiler_plate
    )

    nltk.download("punkt", quiet=True, force=False, raise_on_error=True)

    return [
        sentence
        for sentence in sent_tokenize(llm_response_no_references)
        if sentence.endswith("?")
    ]


def export_questions_and_answers(
    guessed_topics: List[str],
    questions: List[List[str]],
    answers: List[List[List[str]]],
    correct_answers: List[List[Optional[str]]],
    *,
    file_path: str = "questions_and_answers.json",
) -> None:
    """
    Export the questions and answers to a json file.

    Args
    ----
    guessed_topics (List[str]): List of guessed topics.
    questions (List[List[str]]): List of questions.
    answers (List[List[List[str]]): List of answers.
    correct_answers (List[List[Optional[str]]]): List of correct answers.
    file_path (str): File path.
    """
    import json

    data = []
    for topic, question_list, answer_list, correct_answer_list in zip(
        guessed_topics, questions, answers, correct_answers
    ):
        if not question_list:
            continue

        data.append(
            {
                "topic": topic.strip(),
                "questions": [
                    {
                        "question": question.strip(),
                        "answers": answers_to_question,
                        "correct_answer": correct_answer.strip(),
                    }
                    for question, answers_to_question, correct_answer in zip(
                        question_list, answer_list, correct_answer_list
                    )
                    if answers_to_question and correct_answer is not None
                ],
            }
        )

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def extract_answers(
    llm_response: str,
    *,
    negative_response: str,
    max_number_of_answers,
) -> List[str]:
    """
    Extract answers from the LLM response.

    Args
    ----
    llm_response (str): LLM response.
    negative_response (str): Text to\
        check if the response is negative.
    max_number_of_answers (int): Maximum number of answers.
    verbose (bool, optional):\
        Whether to print the extracted answers.\
        By default False.

    Returns
    -------
    List[str]
        List of answers extracted from the LLM response.
    """
    # check if the response is negative
    if negative_response.lower() in llm_response.lower():
        return []

    llm_response_no_markdown = remove_markdown(llm_response)

    answers = [
        sentence.strip()
        for sentence in llm_response_no_markdown.split("\n")
        # add sentence if it starts with a letter and parantheses
        if re.match(r"^\s*[a-zA-Z]\s*\)", sentence)
    ]

    # return the first max_number_of_answers answers
    return answers[: min(max_number_of_answers, len(answers))]


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
        "Don't include these in your guess:\n\n" + "\n".join(excluded_topics) + "\n\n"
        if excluded_topics
        else ""
    )

    prompt = dedent(
        f"""\
        Guess the topic from the following weighted phrases. \
        Try to be as specific as possible. Reply only with your guess, don't add no boilerplate text. \
        {exclude_previous_topics_message}
        
        Weighted phrases:
        {weighted_phrases}

        Topic:"""
    )

    response = model.generate_content(prompt)

    return response.text
