"""
Generate questions from PDF file.
"""

import argparse
import os
import sys
from typing import List, Optional, Sequence

from tqdm import tqdm
from topic_extraction import extract_topics_in_weighted_phrases
from deep_translator import GoogleTranslator

# from translator import DeepL, get_language

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_core.documents.base import Document

from translator import get_language
from utils import (
    export_questions_and_answers,
    extract_answers,
    extract_questions,
    get_page_contents,
    guess_topic_from_weighted_phrases,
)
from rag import get_retrieval_qa_chain, execute_query, process_llm_response


def get_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """
    Parse command line arguments.

    Args
    ----
    argv : Optional[Sequence[str]]
        Arguments to parse. If None, sys.argv[1:] is used.

    Returns
    -------
    argparse.Namespace
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Generate questions from PDF",
        prog="pdf2questions",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "pdf_directory", help="Directory containing PDF files", type=str
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print more information",
    )

    pdf_options = parser.add_argument_group("PDF options")
    pdf_options.add_argument(
        "--extract-text-from-images",
        "-e",
        action="store_true",
        help="Extract text from images in the PDF (slower, "
        "requires `pip install rapidocr-onnxruntime`)",
    )
    lda_options = parser.add_argument_group("LDA options")
    lda_options.add_argument(
        "--number-of-topics",
        "-n",
        help="Number of topics to extract from the text",
        type=int,
        default=10,
    )
    lda_options.add_argument(
        "--passes-over-corpus",
        "-p",
        help="Number of passes over the corpus when training the LDA model "
        "(higher values may improve the quality of the topics but also increase "
        "the training time)",
        type=int,
        default=5,
    )

    # multi choice question options
    multi_choice_options = parser.add_argument_group("Multiple choice question options")
    # TODO: add option to generate a fixed number of questions for each topic
    # multi_choice_options.add_argument(
    #     "--max-questions",
    #     "-q",
    #     help="Maximum number of questions to generate for each topic",
    #     type=int,
    #     default=5,
    # )

    multi_choice_options.add_argument(
        "--max-answers",
        "-m",
        help="Maximum number of answers to generate for each question",
        type=int,
        default=5,
    )
    multi_choice_options.add_argument(
        "--min-answers",
        "-i",
        help="Minimum number of answers to generate for each question",
        type=int,
        default=4,
    )
    multi_choice_options.add_argument(
        # number of correct answers
        "--correct-answers",
        "-c",
        help="Number of correct answers to generate for each question",
        type=int,
        default=1,
    )

    args = parser.parse_args(argv)

    # validate arguments

    if args.correct_answers < 1 or args.max_answers < 1 or args.min_answers < 1:
        parser.error(
            "Number of correct answers, maximum number of answers, "
            "and minimum number of answers must be at least 1"
        )

    if args.correct_answers > args.min_answers:
        parser.error(
            "Number of correct answers must be less than "
            "or equal to the minimum number of answers"
        )

    if args.min_answers > args.max_answers:
        parser.error(
            "Minimum number of answers must be less than "
            "or equal to the maximum number of answers"
        )

    return args


def extract_and_translate_topics(
    docs: List[Document],
    *,
    number_of_topics: int = 10,
    passes_over_corpus: int = 5,
    verbose: bool = False,
) -> List[str]:
    page_contents = [page_content for page_content in get_page_contents(docs)]

    # translate text to English if it is not already in English
    if (source_language := get_language("\n".join(page_contents))) != "english":
        translator = GoogleTranslator()
        translated_docs = [
            translator.translate(doc, target="en")
            for doc in tqdm(
                page_contents,
                desc=f"Translating text from {source_language.capitalize()} to English",
                unit="page",
                len=len(page_contents),
            )
        ]
        page_contents = translated_docs
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
    guessed_topics = []
    for i, weighted_phrase in enumerate(weighted_phrases):
        guessed_topic = guess_topic_from_weighted_phrases(
            weighted_phrase, guessed_topics
        )
        guessed_topic = guessed_topic.replace("\n", "")
        if verbose:
            print(f"Educated guess for topic {i + 1}: {guessed_topic}")
        guessed_topics.append(guessed_topic)

    # TODO: cache topics
    # cache_topics(docs, guessed_topics)

    return guessed_topics


def generate_multi_choice_answers(
    guessed_topics: List[str],
    questions: List[List[str]],
    retrieval_query_chain,
    *,
    min_number_of_answers: int = 4,
    max_number_of_answers: int = 5,
    number_of_correct_answers: int = 1,
    verbose: bool = False,
) -> List[List[List[str]]]:
    answers = []

    negative_response = (
        "I can't"  # this is the response given when no answers are generated
    )
    for topic, question_list in zip(guessed_topics, questions):
        if not question_list:
            # no questions were generated for this topic
            answers.append([])
            continue

        answer_list = []
        answers.append(answer_list)

        for j, question in enumerate(question_list):
            query = (
                "Your task is to generate multiple choice answers for "
                f"the following question about {topic!r}. "
                "The multiple choice answers should be relevant to the question, "
                f"but only **{number_of_correct_answers}** should be correct. "
                f"If you can't generate any answers reply with {negative_response!r}. "
                f"Make sure to provide **only {number_of_correct_answers} correct answers**."
                "Do not include the question itself. "
                f"Make sure to provide at least {min_number_of_answers} and "
                f"at most **{max_number_of_answers}** answers. "
                # "If the question is too general, try to provide answers that are specific. "
                # "If the question is too specific, try to provide answers that are general. "
                "Make sure the answers start with a capital letter "
                "(for example, 'A) Answer', 'B) Answer', etc.). "
                "Try to provide answers that are not too similar to each other. "
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

    return answers


def generate_questions(
    guessed_topics,
    retrieval_qa_chain,
    *,
    verbose=False,
):
    negative_response = "I can't"

    questions = []
    for i, guessed_topic in enumerate(guessed_topics):
        # generate questions for each topic
        if verbose:
            print(f"Generating questions for topic {i + 1}: {guessed_topic}")
        query = (
            "Generate questions from the provided text about the following topic. "
            f"If you can't generate any questions reply with {negative_response!r}: {guessed_topic}"
        )
        response = execute_query(retrieval_qa_chain, query)
        if verbose:
            process_llm_response(response)
            extracted_questions = extract_questions(
                response["result"], negative_response
            )
            print(f"Extracted questions: {extracted_questions}")
        questions.append(extracted_questions)

    return questions

    # how to query pdf dataset ? https://www.youtube.com/watch?v=5Ghv-F1wF_0
    # how to identify topics from text ? https://www.youtube.com/watch?v=ZkAFJwi-G98


def generate_correct_answers(
    guessed_topics,
    questions,
    answers,
    number_of_correct_answers,
    retrieval_qa_chain,
    *,
    verbose=False,
) -> List[List[Optional[str]]]:
    correct_answers = []

    negative_response = "I can't"

    for guessed_topic, question_list, answer_list in zip(
        guessed_topics, questions, answers
    ):
        if not question_list:
            # no questions were generated for this topic
            correct_answers.append([])
            continue

        correct_answer_list = []
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
                f"Choose the correct answers to the following question about {guessed_topic!r}. "
                f"If you none of the answers are correct reply with {negative_response!r}. "
                "Otherwise, provide the correct answers chosen from the list of answers. "
                "Respond with only the letter corresponding to the correct answers "
                "(for example, 'A, B'; 'A'; 'B' etc.). "
                f"Make sure to provide **only {number_of_correct_answers} correct answers**. "
                "Do not include the question nor the full answers. "
                f"Question: {question}"
                f"Answers: {answers_to_question}"
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

    return correct_answers


def main(argv: Optional[Sequence[str]] = None) -> int:
    # this prevents OpenMP from crashing
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

    args = get_args(argv)

    # extract text from PDF
    pdf_loader = PyPDFDirectoryLoader(
        args.pdf_directory,
        glob="*.pdf",
        extract_images=args.extract_text_from_images,
    )
    docs = pdf_loader.load()

    if args.verbose:
        # print information about the PDF
        print(f"Number of pages: {len(docs)}")

    guessed_topics = extract_and_translate_topics(
        docs,
        number_of_topics=args.number_of_topics,
        passes_over_corpus=args.passes_over_corpus,
        verbose=args.verbose,
    )

    # save text to a dataset
    retrieval_qa_chain = get_retrieval_qa_chain(docs)

    questions = generate_questions(
        guessed_topics,
        retrieval_qa_chain,
        verbose=args.verbose,
    )

    # generate the answers to the questions
    answers = generate_multi_choice_answers(
        guessed_topics,
        questions,
        retrieval_qa_chain,
        min_number_of_answers=args.min_answers,
        max_number_of_answers=args.max_answers,
        number_of_correct_answers=args.correct_answers,
        verbose=args.verbose,
    )

    correct_answers = generate_correct_answers(
        guessed_topics,
        questions,
        answers,
        args.correct_answers,
        retrieval_qa_chain,
        verbose=args.verbose,
    )

    # save the questions and answers to a file
    export_questions_and_answers(guessed_topics, questions, answers, correct_answers)

    return 0


if __name__ == "__main__":
    sys.exit(main())
