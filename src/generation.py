import time
from typing import List, Optional

from google.api_core.exceptions import ResourceExhausted
from langchain_core.documents.base import Document

from rag import execute_query, process_llm_response
from response_processing import extract_answers, extract_questions
from topic_extraction import extract_topics_in_weighted_phrases
from utils import (detect_language, get_page_contents,
                   guess_topic_from_weighted_phrases, translate_page_contents)


def generate_multi_choice_answers(
    guessed_topics: List[str],
    questions: List[List[str]],
    retrieval_query_chain,
    *,
    min_number_of_answers: int = 4,
    max_number_of_answers: int = 5,
    number_of_correct_answers: int = 1,
    verbose: bool = False,
    sleep_time: int = 1,
) -> List[List[List[str]]]:
    answers: List[List[List[str]]] = []

    negative_response = (
        "I can't"  # this is the response given when no answers are generated
    )
    for topic, question_list in zip(guessed_topics, questions):
        if not question_list:
            # no questions were generated for this topic
            answers.append([])
            continue

        answer_list: List[List[str]] = []
        answers.append(answer_list)

        for j, question in enumerate(question_list):
            query = (
                "Your task is to generate multiple choice answers for "
                f"the following question about {topic!r}. "
                "The multiple choice answers should be relevant to the "
                f"question, but only **{number_of_correct_answers}** should "
                f"be correct. If you can't generate any answers reply with "
                f"{negative_response!r}. Make sure to provide **only "
                f"{number_of_correct_answers} correct answers**. Do not "
                f"include the question itself. Make sure to provide at least "
                f"{min_number_of_answers} and at most "
                f"**{max_number_of_answers}** answers. "
                # "If the question is too general, "
                # "try to provide answers that are specific. "
                # "If the question is too specific, "
                # "try to provide answers that are general. "
                "Make sure the answers start with a capital letter "
                "(for example, 'A) Answer', 'B) Answer', etc.). "
                "Try to provide answers that are not "
                "too similar to each other. "
                "The generated answers should not be too long or verbose. "
                f"Question: {question}"
            )
            response = execute_query(retrieval_query_chain, query)
            answer = extract_answers(
                response["result"],
                negative_response=negative_response,
                max_number_of_answers=max_number_of_answers,
            )
            if verbose:
                print(f"Question {j + 1}: {question}")
                print(f"Response: {response['result']}")
                print(f"Multiple choice answers: {answer}")
            answer_list.append(answer)

            time.sleep(sleep_time)

    return answers


def generate_questions(
    guessed_topics,
    retrieval_qa_chain,
    *,
    verbose=False,
    sleep_time=1,
):
    negative_response = "I can't"

    questions = []
    for i, guessed_topic in enumerate(guessed_topics):
        # generate questions for each topic
        if verbose:
            print(f"Generating questions for topic {i + 1}: {guessed_topic}")
        query = (
            "Generate questions from the provided "
            "text about the following topic. "
            "If you can't generate any questions reply "
            f"with {negative_response!r}. The Topic: {guessed_topic}"
        )
        try:
            response = execute_query(retrieval_qa_chain, query)
            extracted_questions = extract_questions(
                response["result"], negative_response
            )
            if verbose:
                process_llm_response(response)
                print(f"Extracted questions: {extracted_questions}")
            questions.append(extracted_questions)
        except ResourceExhausted:
            print(f"Failed to generate questions for topic {guessed_topic}")
            questions.append([])

        time.sleep(sleep_time)

    return questions


def generate_correct_answers(
    guessed_topics,
    questions,
    answers,
    number_of_correct_answers,
    retrieval_qa_chain,
    *,
    verbose=False,
    sleep_time=1,
) -> List[List[Optional[str]]]:
    correct_answers: List[List[Optional[str]]] = []

    negative_response = "I can't"

    for guessed_topic, question_list, answer_list in zip(
        guessed_topics, questions, answers
    ):
        if not question_list:
            # no questions were generated for this topic
            correct_answers.append([])
            continue

        correct_answer_list: List[Optional[str]] = []
        correct_answers.append(correct_answer_list)

        for j, (question, answers_to_question) in enumerate(
            zip(question_list, answer_list)
        ):
            if not answers_to_question:
                # no answers were generated for this question
                correct_answer_list.append(None)
                continue

            # generate the correct answers to the question
            query = (
                f"Choose the correct answers to the following question "
                f"about {guessed_topic!r}. If you none of the answers are "
                f"correct reply with {negative_response!r}. Otherwise, "
                "provide the correct answers chosen from the list of answers. "
                "Respond with only the letters corresponding to the correct "
                "answers (for example, 'A, B'; 'A'; 'B' etc.). "
                f"Make sure to provide **only {number_of_correct_answers} "
                "correct answers**. Do not include the question nor the full "
                "answers. \n"
                f"Question: {question}\n"
                f"Answers: {answers_to_question}\n"
            )
            response = execute_query(retrieval_qa_chain, query)

            # extract the correct answers
            if negative_response.lower() in response["result"].lower():
                correct_answer = None
            else:
                correct_answer = response["result"]

            if verbose:
                print(f"Question {j + 1}: {question}")
                print(f"Response: {response['result']}")
                print(f"Correct answer: {correct_answer}")

            correct_answer_list.append(correct_answer)

            time.sleep(sleep_time)

    return correct_answers


def extract_and_translate_topics(
    docs: List[Document],
    *,
    number_of_topics: int = 10,
    passes_over_corpus: int = 5,
    verbose: bool = False,
    sleep_time: int = 1,
) -> List[str]:
    page_contents = [page_content for page_content in get_page_contents(docs)]

    # translate text to English if it is not already in English
    if (
        source_language := detect_language("\n".join(page_contents))
    ) != "english":
        page_contents = translate_page_contents(page_contents, source_language)
    elif verbose:
        print("Text is already in English (no translation needed)")

    # extract topics from text
    if verbose:
        print("Extracting topics from text")
    weighted_phrases = extract_topics_in_weighted_phrases(
        page_contents,
        number_of_topics=number_of_topics,
        passes_over_corpus=passes_over_corpus,
    )

    # convert topics to human-readable format
    guessed_topics: List[str] = []
    for i, weighted_phrase in enumerate(weighted_phrases):
        guessed_topic = guess_topic_from_weighted_phrases(
            weighted_phrase, guessed_topics
        )
        guessed_topic = guessed_topic.replace("\n", "")
        if verbose:
            print(f"Educated guess for topic {i + 1}: {guessed_topic}")
        guessed_topics.append(guessed_topic)

        time.sleep(sleep_time)

    # TODO: cache topics
    # cache_topics(docs, guessed_topics)

    return guessed_topics
