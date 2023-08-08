from pathlib import Path
from typing import Any, Dict, List, Tuple

import ass
import stable_whisper
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import Page, sync_playwright

from utils import settings
from utils.console import print_step
from utils.imagenarator import imagemaker


def get_all_stlyings() -> Tuple[Tuple[int,...],Tuple[int,...],Dict[str,Any]] :
    """
    
    get all styling settings

    """
    theme = settings.config["settings"]["theme"]
    if theme == "dark":
        
        bgcolor = (*settings.config["image"]["dark_bg_color"], 0 if settings.config["image"]["bg_is_transparent"] \
                                                                    else settings.config["image"]["bg_trans"]) 
        txtcolor:Tuple[int,...]  = tuple(settings.config["image"]["dark_text_color"])
        # cookie_file = open(
        #     settings.cwd.joinpath("video_creation/data/cookie-dark-mode.json"), encoding="utf-8"
        # )
    else:
        # cookie_file = open( settings.cwd.joinpath("video_creation/data/cookie-light-mode.json"), encoding="utf-8")
        bgcolor = (255, 255, 255, 255)
        txtcolor = (0, 0, 0)

    return bgcolor, txtcolor , get_subtitle_styling()




def get_screenshots_of_reddit_posts(reddit_object: Dict, screenshot_num:List[int]) -> None:
    """
    Downloads screenshots of reddit posts as seen on the web. Downloads to assets/temp/png

    Args:
        reddit_object (Dict): Reddit object received from reddit/subreddit.py
        screenshot_num (int): Number of screenshots to download
    """

    print_step("Downloading screenshots of reddit posts...")

    reddit_id =  reddit_object["thread_id"]

    # ! Make sure the reddit screenshots folder exists
    Path(f"assets/temp/{reddit_id}/png").mkdir(parents=True, exist_ok=True)

    bgcolor, txtcolor, sub_styling = get_all_stlyings()
    

    if settings.config["settings"]["style"] == 1 :
            # print("transcribing")
            # for idx,item in enumerate(reddit_object["thread_post"]):
            imagemaker(theme=bgcolor, 
                       reddit_obj=reddit_object, 
                       txtclr=txtcolor,
                       )

    # if settings.config["settings"]["style"] == 0  :
        

    options = {}
    
    if not  settings.config["subtitle"]["auto_detect_sub_lang"] :
        options = {"language" : settings.config["reddit"]["thread"]["post_lang"] or "en"}

    word_level = False

    model = stable_whisper.load_model(settings.config["subtitle"]["model_choice"]) # {tiny.en,tiny,base.en,base,small.en,small,medium.en,medium,large-v1,large-v2,large}

    if (settings.config["settings"]["allow_title"] and
        settings.config["settings"]["allow_title_picture"] and
        settings.config["image"]["title_style"] == 0) : 

        sub_path = f'assets/temp/{reddit_id}/png/title.ass'
        result = model.transcribe(f'assets/temp/{reddit_id}/mp3/title.mp3',**options)# type: ignore
        result = result.split_by_length(settings.config["subtitle"]["characters_at_time"] ) # type: ignore
        result.to_ass(sub_path,word_level=word_level ,highlight_color="03fcec",suppress_word_ts=True, **sub_styling)
    
        add_animation(sub_path)
        checkForMannulCheck(settings.config["subtitle"]["mannual_sub_correction"], "Check the substitles in \n" + sub_path )


    if settings.config["settings"]["storymode"] and settings.config["settings"]["style"] == 0 :

        sub_path = f'assets/temp/{reddit_id}/png/postaudio.ass'
        result = model.transcribe(f'assets/temp/{reddit_id}/mp3/postaudio.mp3',**options) # type: ignore
        result = result.split_by_length(settings.config["subtitle"]["characters_at_time"] )# type: ignore
        result.to_ass(sub_path,word_level=word_level ,suppress_word_ts=True, **sub_styling)
        add_animation(sub_path)
        checkForMannulCheck(settings.config["subtitle"]["mannual_sub_correction"], "Check the substitles in \n" + sub_path )

    if settings.config["settings"]["allow_comment"]:

        for i in range(screenshot_num[1]):

            sub_path = f'assets/temp/{reddit_id}/png/{i}.ass'
            result = model.transcribe(f'assets/temp/{reddit_id}/mp3/{i}.mp3',**options)# type: ignore
            result = result.split_by_length(settings.config["subtitle"]["characters_at_time"] )# type: ignore
            # result.merge_by_gap(.15, max_words=6)
            
            result.to_ass(sub_path,word_level=word_level, **sub_styling)# type: ignore
            add_animation(sub_path) 
            checkForMannulCheck(settings.config["subtitle"]["mannual_sub_correction"], "Check the substitles in \n" + sub_path )

    
    if (        settings.config["settings"]["allow_title"] and
                settings.config["settings"]["allow_title_picture"] and
                settings.config["image"]["title_style"] == 1
                ):
        
        render_page = render_title(reddit_object)
        make_screenshot(render_page, reddit_id)
    
def get_subtitle_styling() -> Dict[str , Any]:
    """

    Opens settings 

    """
    with open(
            f"{settings.cwd}/settings.ass", encoding="utf_8_sig"
        ) as f:
        doc = ass.parse(f)
    style =  doc.styles[0]

    stylings =  {
                "Fontname": style.fontname,
                "Fontsize": int(style.fontsize),
                "PrimaryColour": style.primary_color.to_ass(),
                "SecondaryColour": style.secondary_color.to_ass(),
                "OutlineColour": style.outline_color.to_ass(),
                "BackColour": style.back_color.to_ass(),
                "Bold": int(style.bold),
                "Italic": int(style.italic),
                "Underline": int(style.underline),
                "StrikeOut": int(style.strike_out),
                "ScaleX": style.scale_x,
                "ScaleY": style.scale_y,
                "Spacing": style.spacing,
                "Angle": style.angle,
                "BorderStyle": style.border_style,
                "Outline": style.outline,
                "Shadow": style.shadow,
                "Alignment": style.alignment,
                "MarginL": style.margin_l,
                "MarginR": style.margin_r,
                "MarginV": style.margin_v,
                "Encoding": style.encoding,
        }
    settings.sub_settings = stylings

    return stylings


def add_animation(file:str) -> None:

    if not  settings.config["subtitle"]["add_animation"] :
        return
    

    with open(file, encoding="utf_8_sig") as f:
        doc = ass.parse(f)
    f.close()

    #{\\fscx95\\fscy95\\t(0,150,\\fscx100\\fscy100)}
    #  \\fscx95  set scale to 95%
    #  \\fscy95  set scale to 95%
    # \\t(0,150,\\fscx100\\fscy100)} set the fscx95 fscy95 to 100 in 150ms

    for d in doc.events :
        d.text = "{\\fscx95\\fscy95\\t(0,150,\\fscx100\\fscy100)}" + d.text 

    with open (file,"w",encoding="utf_8_sig") as f :
        doc.dump_file(f)
    




def render_title(obj:Dict[str,Any]):


    title =obj["thread_title"]
    comment_num =obj.get("num_comments","99+")
    upvote_num  = obj.get("upvotes","99+")
    subreddit   = obj.get("subreddit", "")


    template_dir = 'template'
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('base.html')
    output_from_parsed_template = template.render(subreddit=subreddit,
                                                  title=title,
                                                  comment_num=comment_num,
                                                  upvote_num=upvote_num)
    # print(output_from_parsed_template)

    # to save the results
    scr_page = f"{settings.cwd}/{template_dir}/rendered.html"
    with open(scr_page, "w",encoding="utf-8") as fh:
        fh.write(output_from_parsed_template)
    return scr_page


def make_screenshot(scr_page,reddit_id):

    

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()#headless=False
        context = browser.new_context(device_scale_factor=3)
        page:Page = context.new_page()
        page.goto("file://"+scr_page)
        # page.set_viewport_size()
    
        page.locator("#title").screenshot(path=settings.cwd.joinpath("assets","temp",reddit_id,"png","title.png"),type='png',omit_background=True)
        context.close()
        browser.close()

def checkForMannulCheck(flag , msg )-> None:

    if flag:
        print(msg)
        input("Press any button to continue...")


# if any(
#     (
#         settings.config["image"]["title_style"] == 0 ,
#         settings.config["settings"]["allow_comment"]
#         )
#     ):

# download(cookie_file, screenshot_num, reddit_object)


# def get_cookie() -> None:
#     """
#     bot login into reddit
#     """
#     print_substep("Logging in to Reddit...")
#     with sync_playwright() as p:
#         browser = p.chromium.launch( headless=False)

#         context  = browser.new_context()

#         page = context.new_page()

#         page.goto("https://www.reddit.com/login", timeout=0)
        
#         page.wait_for_load_state()

#         page.locator('[name="username"]').fill(
#             settings.config["reddit"]["creds"]["username"]
#         )
#         page.locator('[name="password"]').fill(
#             settings.config["reddit"]["creds"]["password"]
#         )
#         page.locator("button[class$='m-full-width']").click()
#         page.wait_for_load_state()
#         # page.wait_for_timeout(5000)

#         login_error_div = page.locator(".AnimatedForm__errorMessage").first
#         if login_error_div.is_visible():
#             login_error_message = login_error_div.inner_text()
#             if login_error_message.strip() != "":           
#                 # The div contains an error message
#                 print_substep(
#                     "We are unable to sign in automatically try to sign in manaully",
#                     style="red",
#                 )
#             input("press any button when finished")
#             page.wait_for_load_state()

            

    
# def chk_credentials():

#     return os.path.exists("auth.json")
        
    

# def download(cookie_file, num, reddit_object: Dict[str,Any]) -> None:

#     screenshot_num : List[int]  = num
#     reddit_id = reddit_object["thread_id"]

#     with sync_playwright() as p:
#         print_substep("Launching Headless Browser...")

#         browser = p.chromium.launch( headless=False)  #headless=True  #to see chrome
#         W    : int = int(settings.config["settings"]["resolution_w"])
#         H    : int = int(settings.config["settings"]["resolution_h"])
#         lang : str = settings.config["reddit"]["thread"]["post_lang"]
        
        
#         dsf = (W // 600) + 1
#         context = browser.new_context(
#             locale= lang or "en-us",
#             device_scale_factor=dsf,
#         )
#         page =  context.new_page()

#         if not chk_credentials():
#             get_cookie()

#         # context.add_cookies()

#         page.set_viewport_size(ViewportSize(width=1920, height=1080))

        
#         # Handle the redesign
#         # Check if the redesign optout cookie is set
#         # if page.locator("#redesign-beta-optin-btn").is_visible():
#         #     # Clear the redesign optout cookie
#         #     clear_cookie_by_name(context, "redesign_optout")
#         #     # Reload the page for the redesign to take effect
#         #     page.reload()
#         # # Get the thread screenshot


#         page.goto(reddit_object["thread_url"], timeout=0)
#         page.set_viewport_size(ViewportSize(width=W, height=H))
#         page.wait_for_load_state()
#         page.wait_for_timeout(5000)

#         cookies = json.load(cookie_file)

#         context.add_cookies(cookies)  # load preference cookies
#         # Get the thread screenshot
#         # page = context.new_page()
#         # page.goto(reddit_object["thread_url"], timeout=0)
#         # page.set_viewport_size(ViewportSize(width=settings.config["settings"]["vwidth"], height=H))


#         # if reddit_object["is_nsfw"] :

#             # page.locator("#login-button").click()
#             # page.frame_locator("#SHORTCUT_FOCUSABLE_DIV iframe").get_by_placeholder("\n        Username\n      ").fill(settings.config["reddit"]["creds"]["username"])
#             # page.frame_locator("#SHORTCUT_FOCUSABLE_DIV iframe").get_by_placeholder("\n        Password\n      ").fill(settings.config["reddit"]["creds"]["password"])
#             # page.wait_for_load_state()
            
#             # page.frame_locator("#SHORTCUT_FOCUSABLE_DIV iframe").get_by_role("button", name="Log In").click()
#             # page.locator('[data-test-id="post-content"]').screenshot(path="assets/temp/test/png/title1.png")




#         if page.locator('[data-testid="content-gate"]').is_visible():

#             # This means the post is NSFW and requires to click the proceed button.

#             print_substep("Post is NSFW. You are spicy...")
#             page.locator('[data-testid="content-gate"] button').click()
#             page.wait_for_load_state()  # Wait for page to fully load

#         if page.locator('[data-click-id="text"] button').is_visible(): 
#             page.locator(
#                 '[data-click-id="text"] button'
#             ).click()  # Remove "Click to see nsfw" Button in Screenshot

#         ########################################################################################


#         # if reddit_object["thread_post"] and  len(reddit_object["thread_post"]) > 600: 
#         #     page.evaluate(
#         #         "()=>document.querySelector(\"[data-test-id='post-content'] div.RichTextJSON-root\").textContent = '';"
#         #         #   "[data-test-id='post-content'] div.RichTextJSON-root")
#         #     )


#         # TODO get the inner html with locator and inner html and put it back if have to take screenshot
        
#         # translate code

#         if settings.config["reddit"]["thread"]["post_lang"]:
#             print_substep("Translating post...")
#             texts_in_tl = ts.translate_text( # type: ignore
#                 reddit_object["thread_title"],
#                 to_language=settings.config["reddit"]["thread"]["post_lang"],
#             )

#             page.evaluate(
#                 "tl_content => document.querySelector('[data-test-id=\"post-content\"] > div:nth-child(3) > div > "
#                 "div').textContent = tl_content",
#                 texts_in_tl,
#             )
#         if page.locator('[data-test-id="post-content"]').is_visible(): 
#             page.locator('[data-test-id="post-content"]').screenshot(path=f"assets/temp/{reddit_id}/png/title.png")

        
#         if page.locator(f'#t3_{reddit_id}').is_visible(): 
#             page.locator(f'#t3_{reddit_id}').screenshot(path=f"assets/temp/{reddit_id}/png/title.png")

#         # if settings.config["settings"]["storymode"]: #TODO readd

#         #     try:  # new change
#         #         page.locator('[data-click-id="text"]').first.screenshot(
#         #             path=f"assets/temp/{reddit_id}/png/story_content.png"
#         #         )
#         #     except TimeoutError:
#         #         exit()
#         if settings.config["settings"]["allow_comment"] and settings.config["settings"]["style"] == 3:
#             for idx, comment in enumerate(
#                     track(reddit_object["comments"], "Downloading screenshots...",reddit_object["comments"].__len__())
#             ):
#                 # Stop if we have reached the screenshot_num
#                 if idx > screenshot_num[1]:
#                     break

#                 if page.locator('[data-testid="content-gate"]').is_visible():
#                     page.locator('[data-testid="content-gate"] button').click()
#                 page.goto(f'https://reddit.com{comment["comment_url"]}' , timeout=0)

#                 # translate code
#                 #document.querySelector("#t1_ji2hg0l > div.Comment.t1_ji2hg0l.P8SGAKMtRxNwlmLz1zdJu.HZ-cv9q391bm8s7qT54B3._1z5rdmX8TDr6mqwNv7A70U").style.width = "500px";
#                 if settings.config["reddit"]["thread"]["post_lang"]:
#                     comment_tl = ts.translate_text( # type: ignore
#                         comment["comment_body"],
#                         to_language=settings.config["reddit"]["thread"]["post_lang"],
#                     )
#                     page.evaluate(
#                         '([tl_content, tl_id]) => document.querySelector(`#t1_${tl_id} > div:nth-child(2) > div > '
#                         'div[data-testid="comment"] > div`).textContent = tl_content',
#                         [comment_tl, comment["comment_id"]],
#                     )
#                 try:
# #################################################################################################################
#                     page.locator(f"#t1_{comment['comment_id']}").screenshot(
#                         path=f"assets/temp/{reddit_id}/png/comment_{idx}.png"
#                     )
#                 except :# not work
#                     # print("sddddddddddFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")
#                     del reddit_object["comments"][idx]
#                     screenshot_num[1] -= 1
#                     print("TimeoutError: Skipping screenshot...")
#                     continue
                
#         browser.close()
        

#         # thread_post
        

#     print_substep("Screenshots downloaded Successfully.", style="bold green")


