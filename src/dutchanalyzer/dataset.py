from pathlib import Path

from loguru import logger
from tqdm import tqdm
import typer

from dutchanalyzer.config import PROCESSED_DATA_DIR, RAW_DATA_DIR
from urllib.request import urlretrieve

app = typer.Typer()


@app.command()
def pull_url_data(urls):
    pass

@app.command()
def main(sources):
    pass


if __name__ == "__main__":
    sources = {'kaikki': 
                    {'Dutch_uncompressed': 
                        {   'post_processed': 'https://kaikki.org/dictionary/Dutch/kaikki.org-dictionary-Dutch.jsonl',
                            'raw': 'https://kaikki.org/dictionary/downloads/nl/nl-extract.jsonl',
                            'error_file': 'https://kaikki.org/dictionary/downloads/nl/nl-extract.errors',
                            'log': 'https://kaikki.org/dictionary/downloads/nl/nl-extract.log'
                        },

                    'English_uncompressed':
                        {   'post_processed': 'https://kaikki.org/dictionary/English/kaikki.org-dictionary-English.jsonl',
                            'raw': 'https://kaikki.org/dictionary/raw-wiktextract-data.jsonl',
                            'error_file': 'https://kaikki.org/dictionary/wiktextract-error-data.json',
                            'lua': 'https://kaikki.org/dictionary/wiktionary-modules.tar',
                            'templates': 'https://kaikki.org/dictionary/wiktionary-templates.tar',
                        },
                            
                        
                    }
                }
    app()
    
