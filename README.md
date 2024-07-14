# slides2questions

 a code repo to generate questions from a given slide or study material

> [!WARNING]  
> This project is still in development and may not work as expected.
>Please report any issues you encounter.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

1. Clone the repo

   ```sh
   git clone
    ```

1. Install the required packages

   ```sh
   pip install -r requirements.txt
   ```

1. Set up environment variables

   ```sh
   cp .env.example .env
   ```

   replace the placeholder `GOOGLE_API_KEY` with your own key in the `.env` file. You can get the key from [here](https://makersuite.google.com/app/apikey).

## Usage

1. Put the PDF files you want to generate questions from in a directory. Let's say the directory is `pdfs/`.

1. Run the following command

    ```sh
    python src/cli.py pdfs/
    ```

    or

    ```sh
    python src/cli.py pdfs/ --extract-text-from-images
    ```

1. The questions will be generated in the `questions_and_answers.json` file in current directory by default. You can change the output file by using the `--output` option.

    ```sh
    python src/cli.py pdfs/ --output my_questions.json
    ```

### Options

   ```sh
   > python src/cli.py -h 

    usage: pdf2questions [-h] [--verbose] [--extract-text-from-images] [--number-of-topics NUMBER_OF_TOPICS] [--passes-over-corpus PASSES_OVER_CORPUS]
                        [--max-answers MAX_ANSWERS] [--min-answers MIN_ANSWERS] [--correct-answers CORRECT_ANSWERS]
                        pdf_directory

    Generate questions from PDF

    positional arguments:
    pdf_directory         Directory containing PDF files

    options:
    -h, --help            show this help message and exit
    --verbose, -v         Print more information (default: False)

    PDF options:
    --extract-text-from-images, -e
                            Extract text from images in the PDF (slower, requires `pip install rapidocr-onnxruntime`) (default: False)

    LDA options:
    --number-of-topics NUMBER_OF_TOPICS, -n NUMBER_OF_TOPICS
                            Number of topics to extract from the text (default: 10)
    --passes-over-corpus PASSES_OVER_CORPUS, -p PASSES_OVER_CORPUS
                            Number of passes over the corpus when training the LDA model (higher values may improve the quality of the topics but also
                            increase the training time) (default: 5)

    Multiple choice question options:
    --max-answers MAX_ANSWERS, -m MAX_ANSWERS
                            Maximum number of answers to generate for each question (default: 5)
    --min-answers MIN_ANSWERS, -i MIN_ANSWERS
                            Minimum number of answers to generate for each question (default: 4)
    --correct-answers CORRECT_ANSWERS, -c CORRECT_ANSWERS
                            Number of correct answers to generate for each question (default: 1)
   ```
