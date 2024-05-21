"""
Generate questions from PDF file.
"""

import argparse
from typing import Optional, Sequence
from pdf2text import extract_text_in_pages
from text_processing_utils import process_text
from translator import DeepL, get_language


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
    parser = argparse.ArgumentParser(description="Generate questions from PDF")
    parser.add_argument("pdf", help="Path to PDF file")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = get_args(argv)

    # extract text from PDF
    pages = extract_text_in_pages(args.pdf)
    text = str("\n".join(pages.values()))

    # translate text to English if it is not already in English
    if (source_language := get_language(text)) != "en":
        print("Translating text to English...")
        translator = DeepL()
        text = translator.translate_text(text[:1000], source_language)

    # extract topics from text
    topics = extract_topics(text)
    

    # test: remove "YILDIZ TEKNİK ÜNİVERSİTESİ" and "BİLGİSAYAR MÜHENDİSLİĞİ BÖLÜMÜ" from the text along with consecutive new lines
    # text = text.replace("YILDIZ TEKNİK ÜNİVERSİTESİ", "")
    # text = text.replace("BİLGİSAYAR MÜHENDİSLİĞİ BÖLÜMÜ", "")
    # text = re.sub(r"\n\n+", "\n\n", text)

    # print(
    #     get_gemma_response(
    #         "Generate 10 *multiple choice* questions from the following text along with their answers: \n"
    #         + text,
    #         streamer="TextStreamer",
    #     )
    # )

    # Plan:
    # preprocess text
    # save text to a dataset
    # identify main topics from txt
    # providing the dataset to the model, generate questions for each topic separately

    # how to query pdf dataset ? https://www.youtube.com/watch?v=5Ghv-F1wF_0
    # how to identify topics from text ? https://www.youtube.com/watch?v=ZkAFJwi-G98

    return 0


if __name__ == "__main__":
    exit(main())
