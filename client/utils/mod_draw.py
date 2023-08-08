import textwrap
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw


def get_font_size(text:str,font) -> Tuple[int,int]:
    
    left, top, right, bottom = font.getbbox(text)
    width, height = right - left, bottom - top
    return width, height

def smart_MText(
    text: str,
    max_w: int,
    font,  #
    path:str|Path ,
    txt_clr="white",
    bg_clr="black",
    line_spacing=10,
    padding_block: int = 20,
    padding_inline: int = 5,
    align="c",
    stroke_width=3,
    stroke_fill="black", 
    *args,
    **kwargs,
) -> None:
    """

    Generates the multiline text on image and save it


    
    """

    uniq_char = set(text)
    avg_font_w = sum(get_font_size(char,font)[0] for char in uniq_char) / len(uniq_char)

    max_char_count = int((max_w + padding_inline) / (avg_font_w))
    texts = textwrap.wrap(text, max_char_count)
    text_wh = (get_font_size(s,font) for s in texts)
    w, h = map(list, zip(*text_wh))

    im_w = min(max_w, max(w)) + (padding_inline * 2)
    im_h = (
        sum(h) + (line_spacing * max(len(h) - 1, 0)) + (padding_block * 2)
    )  
    im = Image.new("RGBA", (im_w, im_h), bg_clr)
    canvas = ImageDraw.Draw(im)
    y = padding_block

    for i, t in enumerate(texts):
        if align == "c":
            x = (im_w - w[i]) / 2
        elif align == "l":
            x = padding_inline
        elif align == "r":
            x = im_w - w[i]
        else:
            raise ValueError("Wrong algin type must be 'r' , 'l' or 'c' ")
        
        canvas.multiline_text
        canvas.text(
            (x, y),
            t,
            txt_clr,
            font,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,  # TODO
        )

        y += line_spacing + h[i]
    im.save(path)
