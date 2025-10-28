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
    sources = {'kaikki': {'Dutch': {'post_processed': ''}}}
    app()
    
