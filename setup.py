from setuptools import setup
import os

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt'), "r", encoding="utf-8") as f:
    REQUIRES = [ln.strip() for ln in f.readlines() if ln.strip()]


kwargs = {
    'name': 'audioset_downloader',
    'version': "0.0.1",
    'description': 'cli to download examples of a specific class from google AudioSet',
    'author': 'Antoine Daurat',
    'author_email': 'ktonalberlin@gmail.com',
    'url': 'https://github.com/ktonal/audioset-downloader',
    'download_url': 'https://github.com/ktonal/audioset-downloader',
    'license': 'MIT',
    "keywords": "audioset dataset sound deep-learning",
    'python_requires': '>=3.6',
    'install_requires': REQUIRES,
    'packages': "./",
    "entry_points": {
        'console_scripts': [
            'audioset-dl=main:download_cli',
            'audioset-classes=main:print_classes',
        ]}

}

setup(**kwargs)
