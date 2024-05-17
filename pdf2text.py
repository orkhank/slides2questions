from io import StringIO
import sys
from typing import BinaryIO, Container, Optional, Sequence, cast

from pdfminer.pdfinterp import (
    PDFResourceManager,
    PDFPageInterpreter,
)
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from pdfminer.utils import FileOrName, open_filename
import argparse


def get_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract text from PDF")
    parser.add_argument("pdf", help="Path to PDF file")
    return parser.parse_args(argv)


def extract_text_in_pages(
    pdf_file: FileOrName,
    password: str = "",
    page_numbers: Optional[Container[int]] = None,
    maxpages: int = 0,
    caching: bool = True,
    codec: str = "utf-8",
    laparams: Optional[LAParams] = None,
) -> dict:
    """Parse and return the text contained in a PDF file.

    :param pdf_file: Either a file path or a file-like object for the PDF file
        to be worked on.
    :param password: For encrypted PDFs, the password to decrypt.
    :param page_numbers: List of zero-indexed page numbers to extract.
    :param maxpages: The maximum number of pages to parse
    :param caching: If resources should be cached
    :param codec: Text decoding codec
    :param laparams: An LAParams object from pdfminer.layout. If None, uses
        some default settings that often work well.
    :return:
    """
    pages = {}
    if laparams is None:
        laparams = LAParams()

    with open_filename(pdf_file, "rb") as fp:
        fp = cast(BinaryIO, fp)  # we opened in binary mode
        rsrcmgr = PDFResourceManager(caching=caching)

        for i, page in enumerate(
            PDFPage.get_pages(
                fp,
                page_numbers,
                maxpages=maxpages,
                password=password,
                caching=caching,
            )
        ):
            with StringIO() as output_string:
                device = TextConverter(
                    rsrcmgr, output_string, codec=codec, laparams=laparams
                )
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                interpreter.process_page(page)
                pages[i] = output_string.getvalue()

    return pages


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = get_args(argv)

    print(extract_text_in_pages(args.pdf))
    for page, text in extract_text_in_pages(args.pdf).items():
        print(f"Page {page + 1}:")
        print(text)
        print()

    return 0


if __name__ == "__main__":
    exit(main())
