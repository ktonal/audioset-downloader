import io
import sys
from youtube_dl import YoutubeDL
import pandas as pd
import datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed
import click
from tqdm import tqdm
from contextlib import redirect_stderr


@click.command()
@click.option("--output-dir", "-o", type=str, default="./",
              help="target directory for the downloads (default='./')")
@click.option("--class-name", "-c", type=str, default="Snoring",
              help="the name of the class to download (default=Snoring)"
                   "(list of available classes can be printed out with the command `audioset-classes`)")
@click.option("--mixed", "-m", default=False, is_flag=True,
              help="if provided, the downloaded examples will be instances of `--class-name` "
                   "and possibly some other classes."
                   " Otherwise (default behaviour), downloaded examples have only `--class-name` as single label.")
@click.option("--exclude-eval-set", "-xe", is_flag=True,
              help="if provided, exclude examples from the eval set (default=False)")
@click.option("--exclude-balanced-set", "-xb", is_flag=True,
              help="if provided, exclude examples from the balanced set (default=False)")
@click.option("--exclude-unbalanced-set", "-xu", is_flag=True,
              help="if provided, exclude examples from the unbalanced set (default=False)")
def download_cli(*args, **kwargs):
    """download examples of a specific class from google's AudioSet"""
    audioset_dl(*args, **kwargs)


@click.command()
def print_classes():
    with open("class_names.txt", "r") as f:
        cls = f.read()
    print(cls)


def audioset_dl(
        output_dir="outputs",
        class_name="Snoring",
        mixed=False,
        exclude_eval_set=False,
        exclude_balanced_set=False,
        exclude_unbalanced_set=False,
):
    ontology = pd.read_json("ontology.json")
    audioset = pd.DataFrame()
    if not exclude_eval_set:
        eval_ = pd.read_csv("csv/eval_segments.csv", header=2, quotechar='"', skipinitialspace=True)
        eval_["dir"] = "eval"
        audioset = pd.concat((audioset, eval_))
    if not exclude_balanced_set:
        balanced = pd.read_csv("csv/balanced_train_segments.csv", header=2, quotechar='"', skipinitialspace=True)
        balanced["dir"] = "balanced"
        audioset = pd.concat((audioset, balanced))

    if not exclude_unbalanced_set:
        unbalanced = pd.read_csv("csv/unbalanced_train_segments.csv", header=2, quotechar='"', skipinitialspace=True)
        unbalanced["dir"] = "unbalanced"
        audioset = pd.concat((audioset, unbalanced))

    cls_id = ontology.id[ontology.name.str.contains(class_name)].item()
    cls_exmp = audioset.positive_labels.str.contains(cls_id)

    def _download(exmp):
        if not mixed and exmp.positive_labels != cls_id:
            return
        start, end = dt.timedelta(seconds=exmp.start_seconds), dt.timedelta(seconds=exmp.end_seconds)
        dler = YoutubeDL({
            "quiet": True, "ignoreerrors": True,
            "format": "bestaudio", "outtmpl": f"{output_dir}/{class_name}/{exmp.dir}/%(title)s.%(ext)s",
            "external_downloader": "ffmpeg",
            "external_downloader_args": ["-ss", str(start), "-to", str(end), "-loglevel", "panic"]
        })
        try:
            with redirect_stderr(io.StringIO()):
                dler.extract_info(exmp._1)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            pass

    pool = ThreadPoolExecutor(max_workers=200)
    futures = [pool.submit(_download, exmp) for exmp in audioset[cls_exmp].itertuples()]
    for _ in tqdm(as_completed(futures, timeout=None), total=cls_exmp.sum(), file=sys.stdout, ncols=88):
        continue
