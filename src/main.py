import io
import sys
from youtube_dl import YoutubeDL
import pandas as pd
import datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed
import click
from tqdm import tqdm
from contextlib import redirect_stderr
import os

__all__ = [
    "audioset_dl",
    "print_classes"
]

root = os.path.abspath(os.path.dirname(__file__))


@click.command()
@click.option("--output-dir", "-o", type=str, default="./",
              help="target directory for the downloads (default='./')")
@click.option("--class-name", "-c", type=str, default=["Snoring"], multiple=True,
              help="the name of the class to download (default=Snoring)"
                   "this option can be repeated to select examples at the intersection of multiple classes"
                   "e.g. `-c Music -c Techno`"
                   "(list of available classes can be printed out with the command `audioset-classes`)")
@click.option("--mixed", "-m", is_flag=True,
              help="if provided, the downloaded examples will be instances of `--class-name` "
                   "and possibly some other classes."
                   " Otherwise (default behaviour), downloaded examples have only `--class-name` as single label.")
@click.option("--exclude-eval-set", "-xe", is_flag=True,
              help="if provided, exclude examples from the eval set (default=False)")
@click.option("--exclude-balanced-set", "-xb", is_flag=True,
              help="if provided, exclude examples from the balanced set (default=False)")
@click.option("--exclude-unbalanced-set", "-xu", is_flag=True,
              help="if provided, exclude examples from the unbalanced set (default=False)")
@click.option("--n-examples", "-n", type=int, default=None,
              help="number of examples to download (default=all matching)")
@click.option("--full-source", "-f", is_flag=True,
              help="if provided, download full examples instead of 10 sec. segments (default=False)")
def download_cli(*args, **kwargs):
    """download examples of a specific class from google's AudioSet"""
    audioset_dl(*args, **kwargs)


@click.command()
def print_classes():
    with open(os.path.join(root, "class_names.txt"), "r") as f:
        cls = f.read()
    print(cls)


def audioset_dl(
        output_dir="outputs",
        class_name=("Snoring",),
        mixed=False,
        exclude_eval_set=False,
        exclude_balanced_set=False,
        exclude_unbalanced_set=False,
        n_examples=None,
        full_source=False
):
    output_dir = os.path.abspath(output_dir)
    ontology = pd.read_json(os.path.join(root, "ontology.json"))
    audioset = pd.DataFrame()
    if not exclude_eval_set:
        eval_ = pd.read_csv(os.path.join(root, "csv", "eval_segments.csv"), header=2, quotechar='"',
                            skipinitialspace=True)
        eval_["dir"] = "eval"
        audioset = pd.concat((audioset, eval_))
    if not exclude_balanced_set:
        balanced = pd.read_csv(os.path.join(root, "csv", "balanced_train_segments.csv"), header=2, quotechar='"',
                               skipinitialspace=True)
        balanced["dir"] = "balanced"
        audioset = pd.concat((audioset, balanced))

    if not exclude_unbalanced_set:
        unbalanced = pd.read_csv(os.path.join(root, "csv", "unbalanced_train_segments.csv"), header=2, quotechar='"',
                                 skipinitialspace=True)
        unbalanced["dir"] = "unbalanced"
        audioset = pd.concat((audioset, unbalanced))

    if mixed or len(class_name) > 1:
        cls_id = []
        for name in class_name:
            cls_id += [ontology.id[ontology.name.str.fullmatch(name)].item()]
        regex = ''.join(f"(?=.*{w})" for w in cls_id)
        regex = r'{}'.format(regex)
        cls_exmp = audioset.positive_labels.str.contains(regex, regex=True)
    else:
        cls_id = ontology.id[ontology.name.str.fullmatch(class_name[0])].item()
        cls_exmp = audioset.positive_labels.str.fullmatch(cls_id)

    def _download(exmp):
        if not mixed and exmp.positive_labels != cls_id:
            return
        start, end = dt.timedelta(seconds=exmp.start_seconds), dt.timedelta(seconds=exmp.end_seconds)
        dler = YoutubeDL({
            "quiet": True, "ignoreerrors": True,
            "format": "bestaudio", "outtmpl": f"{output_dir}/{exmp.dir}/%(title)s.%(ext)s",
            "external_downloader": "ffmpeg",
            "external_downloader_args": [*(("-ss", str(start), "-to", str(end)) if not full_source else tuple()),
                                         "-loglevel", "panic"]
        })
        try:
            with redirect_stderr(io.StringIO()):
                dler.extract_info(exmp._1)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            pass

    pool = ThreadPoolExecutor(max_workers=200)
    subset = audioset[cls_exmp]
    if n_examples is not None:
        subset = subset.sample(n=n_examples)
    futures = [pool.submit(_download, exmp) for exmp in subset.itertuples()]
    for _ in tqdm(as_completed(futures, timeout=None), total=cls_exmp.sum() if n_examples is None else n_examples,
                  file=sys.stdout, ncols=88):
        continue
