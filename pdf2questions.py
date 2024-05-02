import argparse
import re
from typing import Optional, Sequence, get_args
from pdf2text import extract_text_in_pages
from llm_utils import get_gemma_response
import transformers


def get_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate questions from PDF")
    parser.add_argument("pdf", help="Path to PDF file")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = get_args(argv)

    pages = extract_text_in_pages(args.pdf)
    text = "\n".join(pages.values())

    # test: remove "YILDIZ TEKNİK ÜNİVERSİTESİ" and "BİLGİSAYAR MÜHENDİSLİĞİ BÖLÜMÜ" from the text along with consecutive new lines
    # text = text.replace("YILDIZ TEKNİK ÜNİVERSİTESİ", "")
    # text = text.replace("BİLGİSAYAR MÜHENDİSLİĞİ BÖLÜMÜ", "")
    # text = re.sub(r"\n\n+", "\n\n", text)

    text = text[:20000]

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
