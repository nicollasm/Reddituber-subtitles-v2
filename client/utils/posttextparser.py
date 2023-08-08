import re
import subprocess

import spacy    

from utils import settings
from utils.console import print_step, takeinput
from utils.voice import sanitize_text


# working good
def posttextparser(text, tried = False) -> list[str]:
    if settings.config["pereference"]["manual_text_correct"]:
        text = takeinput(text)


    text = re.sub("\n", " ", text)
    try:
        nlp = spacy.load('en_core_web_sm')
    except OSError:
        print()
        if not tried:
            try:
            
                subprocess.call("python -m spacy download en_core_web_sm", shell=True)
                return posttextparser(text,True)
            except subprocess.CalledProcessError as e:
                raise e
            
        print_step("The spacy model can't load. You need to install it with \npython -m spacy download en_core_web_sm")

        exit()
    doc = nlp(text)
    newtext: list[str] = []
    # to check for space str
    for line in doc.sents:
        res = sanitize_text(line.text,False)
        if res and not res.isspace():
            newtext.append(line.text)
        # print(line.text)

    return newtext


def parseComment(text:str) -> str:



    if text.startswith(">"):
        t :list = text.split("\n")
        return "\n".join(t[1:])
    
    return "\n".join(text.split("\n")) 