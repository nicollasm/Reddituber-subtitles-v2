#!/usr/bin/env python

from typing import List, Tuple

from rich.console import Console

from TTS.GTTS import GTTS
from TTS.TikTok import TikTok
from TTS.aws_polly import AWSPolly
from TTS.elevanlabs import elevenlabs
from TTS.engine_wrapper import TTSEngine
from TTS.pyttsx import pyttsx
from TTS.streamlabs_polly import StreamlabsPolly
from TTS.edgetts import edge
from utils import settings
from utils.console import print_table, print_step

console = Console()

TTSProviders = {
    "GoogleTranslate": GTTS,
    "AWSPolly": AWSPolly,
    "StreamlabsPolly": StreamlabsPolly,
    "TikTok": TikTok,
    "pyttsx": pyttsx,
    "edge"  : edge ,
    "ElevenLabs": elevenlabs,
}


def save_text_to_mp3(reddit_obj)  -> Tuple[int | float, list[int], List[list[float]]]:
    """Saves text to MP3 files.

    Args:
        reddit_obj (): Reddit object received from reddit API in reddit/subreddit.py

    Returns:
        tuple[int,int]: (total length of the audio, the number of comments audio was generated for)
    """

    voice = settings.config["settings"]["tts"]["voice_choice"]
    if not str(voice).casefold() in map(lambda _: _.casefold(), TTSProviders):
        while True:
            print_step("Please choose one of the following TTS providers: ")
            print_table(TTSProviders)
            voice = input("\n")
            if voice.casefold() in map(lambda _: _.casefold(), TTSProviders):
                break
            print("Unknown Choice")
            
    text_to_mp3 = TTSEngine(
            get_case_insensitive_key_value(TTSProviders, voice), reddit_obj , max_length = settings.config["settings"]["len"]
        )
    return text_to_mp3.run()


def get_case_insensitive_key_value(input_dict, key):
    return next(
        (
            value
            for dict_key, value in input_dict.items()
            if dict_key.lower() == key.lower()
        ),
        None,
    )
