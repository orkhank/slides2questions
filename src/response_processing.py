import re
from typing import List, Optional

import nltk
from nltk.tokenize import sent_tokenize

from utils import remove_markdown


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
    llm_response_no_boiler_plate = llm_response_no_markdown.replace(
        ":\n\n", ".\n"
    )

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
