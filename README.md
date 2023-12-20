# audioset-downloader

cli for easily building datasets of audio files from google's AudioSet.

**Update may 2023**: metadata has been extended with number of views, likes, comments, availability

## Installation

```bash
pip install audioset-downloader
```

note that you'll need to have `ffmpeg` installed on your system.

## Features

- filter by class names (union or intersection)
- filter by set (train [balanced, unbalanced], eval)
- limit number of downloads
- select most viewed / most liked

## Usage

```
Usage: audioset-dl [OPTIONS]

  download examples of a specific class from google's AudioSet

Options:
  -o, --output-dir TEXT          target directory for the downloads
                                 (default='./')
  -c, --class-name TEXT          the name of the class to download
                                 (default=Snoring)this option can be repeated
                                 to select examples at the intersection of
                                 multiple classese.g. `-c Music -c
                                 Techno`(list of available classes can be
                                 printed out with the command `audioset-
                                 classes`)
  -u, --class-union              toggle whether class names should intersect
                                 (default) or not
  -m, --mixed                    if provided, the downloaded examples will be
                                 instances of `--class-name` and possibly some
                                 other classes. Otherwise (default behaviour),
                                 downloaded examples have only `--class-name`
                                 as single label.
  -xe, --exclude-eval-set        if provided, exclude examples from the eval
                                 set (default=False)
  -xb, --exclude-balanced-set    if provided, exclude examples from the
                                 balanced set (default=False)
  -xu, --exclude-unbalanced-set  if provided, exclude examples from the
                                 unbalanced set (default=False)
  -n, --n-examples INTEGER       number of examples to download (default=all
                                 matching)
  -f, --full-source              if provided, download full examples instead
                                 of 10 sec. segments (default=False)
  -mv, --most-viewed             if --n-examples is provided, only the n most
                                 viewed examples will be downloaded
  -ml, --most-liked              if --n-examples is provided, only the n most
                                 liked examples will be downloaded
  --help                         Show this message and exit.
```

you can also print the available classes names with

```bash
audioset-classes
```

## References

- AudioSet Homepage:
    https://research.google.com/audioset/index.html
- Dataset classes content:
    https://research.google.com/audioset/dataset/index.html
    
## License

MIT


