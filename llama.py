import argparse
from typing import Optional, Sequence
from llm_utils import get_gemma_response


def main(argv: Optional[Sequence[str]] = None) -> int:
    print(get_gemma_response("Write a poem about love."))
    print(get_gemma_response("What is the meaning of life?"))
    return 0


if __name__ == "__main__":
    exit(main())
