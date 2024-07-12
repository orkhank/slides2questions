from abc import ABC, abstractmethod
from typing import Optional

import googletrans  # type: ignore
import googletrans.models


class Translator(ABC):
    @abstractmethod
    def translate_text(
        self, text: str, source_language: Optional[str], target_language: str
    ) -> str:
        pass


class Google(Translator):
    def __init__(self):
        self.translator = googletrans.Translator()

    def translate_text(
        self,
        text: str,
        source_language: str = "auto",
        target_language: str = "en",
    ) -> str:
        if target_language not in googletrans.LANGUAGES:
            raise ValueError(f"Language {target_language} is not supported")
        if len(text) == 0:
            raise ValueError("Text is empty")
        if not isinstance(text, str):
            raise ValueError("Text is not a string")

        translated_text = self.translator.translate(
            text, src=source_language, dest=target_language
        )

        # sanity check
        assert isinstance(translated_text, googletrans.models.Translated)

        return translated_text.text

    def get_supported_languages(self):
        return googletrans.LANGUAGES

    def detect_language(self, text: str) -> str:
        translated_text = self.translator.translate(
            text[: min(1000, len(text))]
        )
        return translated_text.src


def get_language(text: str) -> str:
    translator = Google()
    language = translator.detect_language(text)

    # map code to full language name
    return googletrans.LANGUAGES[language]
