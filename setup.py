from setuptools import setup, find_packages
import os


with open('src/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.0.1'


with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt'), "r", encoding="utf-8") as f:
    REQUIRES = [ln.strip() for ln in f.readlines() if ln.strip()]

PACKAGES = find_packages(exclude=('tests', 'tests.*'))


kwargs = {
    'name': 'audioset_downloader',
    'version': version,
    'description': 'cli to download examples of a specific class from google AudioSet',
    'author': 'Antoine Daurat',
    'author_email': 'ktonalberlin@gmail.com',
    'url': 'https://github.com/ktonal/audioset-downloader',
    'download_url': 'https://github.com/ktonal/audioset-downloader',
    'license': 'MIT',
    "keywords": "audioset dataset sound deep-learning",
    'python_requires': '>=3.6',
    'install_requires': REQUIRES,
    'package_data': {"src": ["ontology.json", "class_names.txt", "csv/eval_segments.csv",
                             "csv/balanced_train_segments.csv", "csv/unbalanced_train_segments.csv"]},
    'packages': PACKAGES,
    "entry_points": {
        'console_scripts': [
            'audioset-dl=src.main:download_cli',
            'audioset-classes=src.main:print_classes',
        ]}

}

setup(**kwargs)
