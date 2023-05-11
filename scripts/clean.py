from src.main import audioset_dl
import pytest
from pytube import YouTube
import pandas as pd
import os
import numpy as np
from tqdm import tqdm


def first_with(itrbl, key):
    return next(item[key] for item in itrbl if key in item)


if __name__ == '__main__':
    root = "../src/"
    file = "eval_segments"
    eval = pd.read_csv(os.path.join(root, "csv", f"{file}.csv"), header=2, quotechar='"',
                       skipinitialspace=True)
    eval = eval.iloc[:500]
    eval["private"] = np.zeros((len(eval),), dtype=bool)
    eval["unavailable"] = np.zeros((len(eval),), dtype=bool)
    eval["views"] = np.zeros((len(eval),), dtype=int)
    eval["likes"] = np.zeros((len(eval),), dtype=int)
    eval["rating"] = np.zeros((len(eval),), dtype=float)
    eval["comments"] = np.zeros((len(eval),), dtype=int)
    success, fail = 0, 0
    pbar = tqdm(total=len(eval))
    # eval["has_content"] = np.ones((len(eval),), dtype=bool)
    for i, video_id in enumerate(eval["# YTID"]):
        yt = YouTube(f"v={video_id}")
        unavailable = yt.vid_info["playabilityStatus"]["status"] == "ERROR"
        eval["unavailable"].iat[i] = unavailable
        if unavailable:
            fail += 1
            continue
        try:
            is_private = yt.vid_info["videoDetails"]['isPrivate']
            eval["private"].iat[i] = is_private
            if is_private:
                fail += 1
        except Exception as e:
            pass
        # is_owner_viewing = yt.vid_info["videoDetails"]['isOwnerViewing']
        ratings = yt.rating
        if ratings is not None:
            eval["rating"].iat[i] = ratings
        try:
            views = yt.views
            eval["views"].iat[i] = views
        except Exception as e:
            pass
        try:
            contents = yt.initial_data["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"]
        except Exception as e:
            # eval["has_content"].iat[i] = False
            continue
        try:
            likes_txt = first_with(
                first_with(
                    contents, "videoPrimaryInfoRenderer")["videoActions"]["menuRenderer"]["topLevelButtons"],
                "segmentedLikeDislikeButtonRenderer") \
                ["likeButton"]["toggleButtonRenderer"]["toggledText"]["accessibility"]["accessibilityData"]["label"]
            likes = int(likes_txt.strip(" likes").replace(",", ""))
            eval["likes"].iat[i] = likes
        except Exception as e:
            pass
        try:
            comments_txt = first_with(
                first_with(contents, "itemSectionRenderer")["contents"],
                "commentsEntryPointHeaderRenderer")["commentCount"]["simpleText"]
            n_comments = 0
            for mark, mult in [("M", 1e6), ("K", 1e3), ("", 1)]:
                if mark in comments_txt:
                    comments_txt = comments_txt.replace(mark, "")
                    n_comments = int(float(comments_txt) * mult)
                    break
            eval["comments"].iat[i] = n_comments
        except Exception as e:
            pass
        pbar.set_postfix_str(f"failed={fail}")
        pbar.update(1)
    eval.to_csv(os.path.join(root, f"{file}-cleaned.csv"))