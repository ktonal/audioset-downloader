from youtube_dl import YoutubeDL
import pandas as pd
import datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed


if __name__ == '__main__':
    OUTPUT_DIR = "outputs"
    CLASS_NAME = "Snoring"
    # Whether examples with multiple classes should be ignored:
    strict = True
    eval_set = True
    balanced_set = True
    unbalanced_set = True

    ontology = pd.read_json("ontology.json")
    audioset = pd.DataFrame()
    if eval_set:
        eval_ = pd.read_csv("csv/eval_segments.csv", header=2, quotechar='"', skipinitialspace=True)
        eval_["dir"] = "eval"
        audioset = pd.concat((audioset, eval_))
    if balanced_set:
        balanced = pd.read_csv("csv/balanced_train_segments.csv", header=2, quotechar='"', skipinitialspace=True)
        balanced["dir"] = "balanced"
        audioset = pd.concat((audioset, balanced))

    if unbalanced_set:
        unbalanced = pd.read_csv("csv/unbalanced_train_segments.csv", header=2, quotechar='"', skipinitialspace=True)
        unbalanced["dir"] = "unbalanced"
        audioset = pd.concat((audioset, unbalanced))

    cls_id = ontology.id[ontology.name.str.contains(CLASS_NAME)].item()
    cls_exmp = audioset.positive_labels.str.contains(cls_id)


    def _download(exmp):
        if strict and exmp.positive_labels != cls_id:
            return
        print(exmp)
        start, end = dt.timedelta(seconds=exmp.start_seconds), dt.timedelta(seconds=exmp.end_seconds)
        dler = YoutubeDL({
            "quiet": True,
            "format": "bestaudio", "outtmpl": f"{OUTPUT_DIR}/{CLASS_NAME}/{exmp.dir}/%(title)s.%(ext)s",
            "external_downloader": "ffmpeg",
            "external_downloader_args": ["-ss", str(start), "-to", str(end), "-loglevel", "panic"]
        })
        try:
            dler.extract_info(exmp._1)
        except:
            pass

    pool = ThreadPoolExecutor(max_workers=200)
    futures = [pool.submit(_download, exmp) for exmp in audioset[cls_exmp].itertuples()]
    as_completed(futures, timeout=None)
