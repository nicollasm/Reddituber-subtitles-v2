from PIL import ImageFont
from rich.progress import track

from TTS.engine_wrapper import process_text
from utils import settings
from utils.mod_draw import smart_MText

# new sheme TODO
# def imagemaker(theme, reddit_obj: dict, txtclr, mktitle:bool, mkpost:bool, mkcoment:bool ) -> None:
def imagemaker(theme, reddit_obj: dict, txtclr) -> None:
    """
    Render Images for video
    """

    reddit_id = reddit_obj["thread_id"]
    font = ImageFont.truetype(
        f"fonts/{settings.config['fonts']['normal_font']}", settings.config["fonts"]["normal_font_size"]
    )

    if settings.config["settings"]["allow_title"]:
        title = reddit_obj["thread_title"]
        tfont = ImageFont.truetype(
            f"fonts/{settings.config['fonts']['title_font']}", settings.config["fonts"]["title_font_size"] 
        )

        smart_MText(
            text=process_text(title),
            max_w=settings.config["image"]["max_im_w_story"],
            font=tfont,
            path=f"assets/temp/{reddit_id}/png/title.png",
            txt_clr=txtclr,
            bg_clr=theme,
        )
        del tfont
    if settings.config["settings"]["storymode"]:
        posttext = reddit_obj["thread_post"]

        if isinstance(posttext, str):
            raise TypeError("style 2 require list or tuple containing str not str")

        for idx, text in track(enumerate(posttext), "Making post image..."):
            smart_MText(
                text=process_text(text),
                max_w=settings.config["image"]["max_im_w_story"],
                font=font,
                path=f"assets/temp/{reddit_id}/png/img{idx}.png",
                txt_clr=txtclr,
                bg_clr=theme,
            )

    if settings.config["settings"]["allow_comment"]:
        comments = reddit_obj["comments"]
        for idx, text in track(enumerate(comments), "Making Comment Image..."):
            smart_MText(
                text=process_text(text["comment_body"]),
                max_w=settings.config["image"]["max_im_w_story"],
                font=font,
                path=f"assets/temp/{reddit_id}/png/comment_{idx}.png",
                txt_clr=txtclr,
                bg_clr=theme,
            )
