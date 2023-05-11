import internetarchive as ia
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

if __name__ == '__main__':
    pool = ThreadPoolExecutor(max_workers=50)
    r = [*ia.search_items("clubnight").iter_as_results()]
    futures = [pool.submit(f.download, destdir="outputs") for x in r for f in ia.get_files(x["identifier"], glob_pattern="*mp3")]
    print("starting downloads")
    for _ in tqdm(as_completed(futures), total=len(futures)):
        continue


