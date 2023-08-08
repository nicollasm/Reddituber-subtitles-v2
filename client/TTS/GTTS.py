#!/usr/bin/env python3
import random
from typing import List

from gtts import gTTS

from utils import settings


class GTTS:
    def __init__(self) -> None:
        self.max_chars = 5000
        self.voices:List[str] = []
        self.has_sub = False

    def run(self, text, filepath) -> None:
        tts = gTTS(
            text=text,
            lang=settings.config["reddit"]["thread"]["post_lang"] or "en",
            slow=False,
        )
        tts.save(filepath)

    def randomvoice(self) -> str:
        return random.choice(self.voices)
