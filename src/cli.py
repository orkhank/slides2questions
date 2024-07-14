"""
Generate questions from PDF file.
"""

import argparse
import os
import sys
import time
from typing import List, Optional, Sequence

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_core.documents.base import Document

from generation import (
    generate_correct_answers,
    generate_multi_choice_answers,
    generate_questions,
)
from rag import get_retrieval_qa_chain
from response_processing import export_questions_and_answers
from topic_extraction import extract_topics_in_weighted_phrases
from utils import (
    detect_language,
    get_page_contents,
    guess_topic_from_weighted_phrases,
    translate_page_contents,
)


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
        "--output",
        "-o",
        help="Output file for the questions and answers",
        type=str,
        default="questions_and_answers.json",
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
        "(higher values may improve the quality of the topics but also "
        "increase the training time)",
        type=int,
        default=5,
    )

    # multi choice question options
    multi_choice_options = parser.add_argument_group(
        "Multiple choice question options"
    )
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

    llm_options = parser.add_argument_group("LLM options")

    llm_options.add_argument(
        "--llm-model",
        help="LLM model to use for generating questions and answers",
        type=str,
        default="gemini-1.5-flash-latest",
    )
    llm_options.add_argument(
        "--max-retries",
        help="The maximum number of retries to make when generating.",
        type=int,
        default=6,
    )

    args = parser.parse_args(argv)

    # validate arguments

    if (
        args.correct_answers < 1
        or args.max_answers < 1
        or args.min_answers < 1
    ):
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

    if os.path.isdir(args.pdf_directory) is False:
        parser.error("The specified PDF directory does not exist")

    return args


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


def main(argv: Optional[Sequence[str]] = None) -> int:
    # this prevents OpenMP from crashing
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    load_dotenv()

    args = get_args(argv)

    # extract text from PDF
    pdf_loader = PyPDFDirectoryLoader(
        args.pdf_directory,
        glob="*.pdf",
        extract_images=args.extract_text_from_images,
    )
    docs = pdf_loader.load()

    if not docs:
        print("No PDF files found")
        return 1

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
    retrieval_qa_chain = get_retrieval_qa_chain(
        docs, llm_model_name=args.llm_model, max_retries=args.max_retries
    )

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
    export_questions_and_answers(
        guessed_topics,
        questions,
        answers,
        correct_answers,
        file_path=args.output,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
