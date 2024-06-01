import os
import sys
from typing import Optional
import googletrans.models
from load_dotenv import load_dotenv
import deepl
from abc import ABC, abstractmethod
import googletrans  # type: ignore


class Translator(ABC):
    @abstractmethod
    def translate_text(
        self, text: str, source_language: Optional[str], target_language: str
    ) -> str:
        pass


class DeepL(Translator):
    def __init__(self, auth_key: Optional[str] = None) -> None:
        if auth_key is None:
            load_dotenv()
            self.auth_key = os.getenv("DEEPL_AUTH_KEY")
            if self.auth_key is None:
                raise ValueError("DeepL API key is not provided")
        else:
            self.auth_key = auth_key

        self.translator = deepl.Translator(self.auth_key)

    def translate_text(
        self,
        text: str,
        source_language: Optional[str] = None,
        target_language: str = "EN-US",
    ) -> str:
        if (
            source_language is not None
            and source_language.upper() not in self.get_source_languages()
        ):
            raise ValueError(f"Language {source_language} is not supported")
        if len(text) == 0:
            raise ValueError("Text is empty")
        if not isinstance(text, str):
            raise ValueError("Text is not a string")

        translated_text = self.translator.translate_text(
            text, source_lang=source_language, target_lang=target_language
        )

        # sanity check
        assert isinstance(translated_text, deepl.TextResult)

        return translated_text.text

    def get_source_languages(self):
        return {lang.code for lang in self.translator.get_source_languages()}

    def get_target_languages(self):
        return {lang.code for lang in self.translator.get_target_languages()}

    def get_usage(self):
        return self.translator.get_usage()


class Google(Translator):
    def __init__(self):
        self.translator = googletrans.Translator()

    def translate_text(
        self, text: str, source_language: str = "auto", target_language: str = "en"
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
        translated_text = self.translator.translate(text[:min(1000, len(text))])
        return translated_text.src


def get_language(text: str) -> str:
    translator = Google()
    language = translator.detect_language(text)

    # map code to full language name
    return googletrans.LANGUAGES[language]


def main():
    translator = DeepL()
    print(translator.translate_text("Hello, how are you?", "DE"))
    translator = Google()
    print(translator.translate_text("Hello, how are you?", "de"))


if __name__ == "__main__":
    sys.exit(main())
