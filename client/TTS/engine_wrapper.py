
import os
import re
from pathlib import Path
from typing import Any, List, Literal, Tuple

from rich.progress import track
from translators import translate_text

from utils import posttextparser, settings
from utils.console import print_step, print_substep
from utils.voice import getduration, sanitize_text


class TTSEngine:
    """Calls the given TTS engine to reduce code duplication and allow multiple TTS engines.

    Args:
        tts_module            : The TTS module. Your module should handle the TTS itself and saving to the given path under the run method.
        reddit_object         : The reddit object that contains the posts to read.
        path (Optional)       : The unix style path to save the mp3 files to. This must not have leading or trailing slashes.
        max_length (Optional) : The maximum length of the mp3 files in total.

    Notes:
        tts_module must take the arguments text and filepath.
    """

    def __init__(
        self,
        tts_module,
        reddit_object: dict,
        max_length: int,
        path: str = "assets/temp/",  #TODO cwd
        last_clip_length: int = 0,
    ) -> None:
        self.tts_module = tts_module()
        self.reddit_object = reddit_object

        self.redditid = re.sub(r"[^\w\s-]", "", reddit_object["thread_id"])
        self.path = path + self.redditid + "/mp3"  #TODO cwd
        self.max_length = max_length
        self.length = 0
        self.last_clip_length = last_clip_length
        self.durations: List[list[float]] = [[], [],[]]  #story , comment , title

    def run(self) -> Tuple[float, list[int], List[List[float]]]:

        Path(self.path).mkdir(parents=True, exist_ok=True)
        print_step("Saving Text to MP3 files...")
        if settings.config["settings"]["allow_title"]:
            self.call_tts("title",
                          process_text(self.reddit_object["thread_title"]),
                          "title")

        counter = [
            0, 0
        ]  #first for story second for comment num # TODO add for title

        if settings.config["settings"]["storymode"]:
            if settings.config["settings"]["style"] == 0:
                print_substep("Collecting audio ...","green")
                self.safe_call_tts("postaudio",
                                   self.reddit_object["thread_post"], "story")
                counter[0] += 1

            elif settings.config["settings"]["style"] == 1:
                for idx, text in track(
                        enumerate(self.reddit_object["thread_post"]),"dowloading audio.. ",len(self.reddit_object["thread_post"])):

                    self.safe_call_tts(f"postaudio-{idx}", text, "story")
                    counter[0] += 1

        if settings.config["settings"]["allow_comment"]:

            for idx, comment in track(
                    enumerate(self.reddit_object["comments"]),
                                                    "Downloading audio...",
                                                    total=self.reddit_object["comments"].__len__()):
                
                # ! Stop creating mp3 files if the length is greater than max length.
                if settings.config["settings"]["auto_selection"] and (
                        self.length > self.max_length) and (idx > 1):
                    self.length -= self.last_clip_length
                    del self.durations[1][-1] #story , comment , title
                    counter[1] -= 1
                    break
                
                self.safe_call_tts(idx, comment["comment_body"], "comment")
                counter[1] += 1

        print_substep("Saved Text to MP3 files successfully.",
                      style="bold green")

        # self.length += settings.config["silence"]["before_audio"] *idx # excluding title

        return self.length, counter, self.durations

    def safe_call_tts(self, fname: str | int, text: str,
                      type: Literal["story", "comment", "title"]) -> None:
        """
        lenght safe method to call TTS

        @parm ``fname``
        @parm ``text``
        @parm ``type``
        """
        if not len(text) > self.tts_module.max_chars:
            return self.call_tts(fname, process_text(text), type)

        self.split_post(text, fname, type)

    def split_post(self, text: str, fname, type: str) -> None:
        split_files = []
        split_text = [
            x.group().strip() for x in re.finditer(
                r" *(((.|\n){0," + str(self.tts_module.max_chars) +
                                                                "})(\.|.$))", # type: ignore idk
                text 
            )
        ]

        
        # split_text = posttextparser.posttextparser(text=text) #TODO
        idy = None
        for idy, text_cut in enumerate(split_text):
            newtext = process_text(text_cut)
            # print(f"{idx}-{idy}: {newtext}\n")

            if not newtext or newtext.isspace():
                print(
                    "newtext was blank because sanitized split text resulted in none"
                )
                continue
            
            self.call_tts(f"{fname}-{idy}.part", newtext, type, False)
        with open(f"{self.path}/list.txt", "w") as f:
            for idz in range(0, len(split_text)):
                f.write("file " + f"'{fname}-{idz}.part.mp3'" + "\n")
            split_files.append(
                str(f"{self.path}/{fname}-{idy}.part.mp3"))
            # f.write("file " + f"'silence.mp3'" + "\n")

        os.system(
            "ffmpeg -f concat -y -hide_banner -loglevel warning -safe 0 "
            + "-i " + f"{self.path}/list.txt " + "-c copy " +
            f"{self.path}/{fname}.mp3")
            
        
        self.update_durations(fname,type)


        try:
            for i in range(0, len(split_files)):
                os.unlink(split_files[i])
        except FileNotFoundError as e:
            print("File not found: " + e.filename)
        except OSError:
            print("OSError")

    def call_tts(self, filename: Any, text:str, type:str|None, update_time = True) -> None:

        self.tts_module.run(text, filepath=f"{self.path}/{filename}.mp3")

        if update_time:
            self.update_durations(filename,type)


    def update_durations(self,filename,type) -> None:

        clip_dur = getduration(f"{self.path}/{filename}.mp3")
        self.last_clip_length = clip_dur
        self.length += clip_dur

        if type == "story":
            self.durations[0].append(clip_dur)
        elif type == "comment":
            self.durations[1].append(clip_dur)
        elif type == "title":
            self.durations[2].append(clip_dur)
        else:
            raise TypeError("wrong type audio")
        
    # def make_sub(self):


def process_text(text: str, clean: bool = True) -> str:
    lang = settings.config["reddit"]["thread"]["post_lang"]
    new_text = sanitize_text(text) if clean else text
    if lang:
        print_substep("Translating Text...")
        translated_text = translate_text(text, to_language=lang)
        assert isinstance(translated_text,
                          str), "tranlator returned wrong type"
        new_text = sanitize_text(translated_text)
    return new_text
