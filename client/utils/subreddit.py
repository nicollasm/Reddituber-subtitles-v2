import json
from os.path import exists
import sys

from utils import settings
from utils.console import print_step, print_substep


def get_subreddit_undone(submissions: list, subreddit, times_checked=0):
    """_summary_

    Args:
        submissions (list): List of posts that are going to potentially be generated into a video
        subreddit (praw.Reddit.SubredditHelper): Chosen subreddit

    Returns:
        Any: The submission that has not been done
    """
    # recursively checks if the top submission in the list was already done.
    if not exists(f"{settings.cwd}/video_creation/data/videos.json"):
        with open(f"{settings.cwd}/video_creation/data/videos.json", "w+") as f:
            json.dump([], f)
    with open(
        f"{settings.cwd}/video_creation/data/videos.json", "r", encoding="utf-8"
    ) as done_vids_raw:
        done_videos = json.load(done_vids_raw)
    for submission in submissions:
        if already_done(done_videos, submission):
            continue
        if submission.over_18 and not settings.config["settings"]["allow_nsfw"]:
            print_substep("NSFW Post Detected. Skipping...")
            continue

        if submission.stickied:
            print_substep("This post was pinned by moderators. Skipping...")
            continue

        if settings.config["settings"][
            "storymode"
        ] and submission.subreddit.display_name.lower().startswith("ask"):
            print_substep(
                f"you are using {submission.subreddit.display_name.lower()} subreddit with storymode it will cause"
                "errors as they do not have post content mostly",
                "red",
            )

        if (
            submission.num_comments
            <= int(settings.config["reddit"]["thread"]["min_comments"])
            and not settings.config["settings"]["storymode"]
        ):
            print_substep(
                f'This post has under the specified minimum of comments  \
                ({settings.config["reddit"]["thread"]["min_comments"]}). Skipping...'
            )
            continue
        if settings.config["settings"]["storymode"] and not submission.selftext:
            print("No post text found skipping...")
            continue
        if settings.config["settings"]["storymode"]:
            if len(submission.selftext) > (
                settings.config["settings"]["storymode_max_length"]
            ):
                print("Post is longer so skipping !! ", len(submission.selftext))
                continue

            if len(submission.selftext) < (
                settings.config["settings"]["storymode_min_length"]
            ):
                print("Post is short so skipping !! ", len(submission.selftext))
                continue

        return submission
    print("all submissions have been done going by top submission order")
    VALID_TIME_FILTERS = [
        "day",
        "hour",
        "month",
        "week",
        "year",
        "all",
    ]  # set doesn't have __getitem__
    index = times_checked + 1
    if index == len(VALID_TIME_FILTERS):
        print(
            "all time filters have been checked you absolute madlad \n if you are seeing this message more and more check change settings like storymode_max_length,storymode_min_length,min_comments,storymode "
        )
        sys.exit(1)

    return get_subreddit_undone(
        subreddit.top(
            time_filter=VALID_TIME_FILTERS[index],
            limit=(50 if int(index) == 0 else index + 1 * 50),
        ),
        subreddit,
        times_checked=index,
    )  # all the videos in hot have already been done


def already_done(done_videos: list, submission) -> bool:
    """Checks to see if the given submission is in the list of videos

    Args:
        done_videos (list): Finished videos
        submission (Any): The submission

    Returns:
        Boolean: Whether the video was found in the list
    """

    for video in done_videos:
        if video["id"] == str(submission):
            return True
    return False
