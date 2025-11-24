from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
import os

# Load environment variables from .env file if it exists
load_dotenv()
# Get the path to the first data source from environment variables
# This should be set in the .env file or the environment

# Paths
PROJ_ROOT = Path(__file__).resolve().parents[2]
#logger.info(f"PROJ_ROOT path is: {PROJ_ROOT}")

DATA_DIR = PROJ_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"
RAW_KAIKKI_DIR = RAW_DATA_DIR / 'kaikki'
KAIKKI_EN_POSTPROCESSED_JSON = RAW_KAIKKI_DIR / 'en' / 'kaikki_en-postprocessed.jsonl'
WIKT_PREPROCESSING_DIR = INTERIM_DATA_DIR / 'preprocessing' / 'wikt'
WIKT_ANALYSIS_DIR = INTERIM_DATA_DIR / 'analysis'/ 'wikt' 
WIKT_CLEANING_DIR = INTERIM_DATA_DIR / 'cleaning' / 'wikt'

EER_DIR = WIKT_PREPROCESSING_DIR / 'en' / 'EER'
ENR_DIR = WIKT_PREPROCESSING_DIR / 'en' / 'ENR'
NER_DIR =  WIKT_PREPROCESSING_DIR / 'nl' / 'NER'
NNR_DIR =  WIKT_PREPROCESSING_DIR / 'nl' / 'NNR'


UTILITIES_DIR = PROJ_ROOT / 'src' / 'dutchanalyzer' / 'utilities'

EEF_FOLDER = WIKT_CLEANING_DIR / 'en' 
ENF_FOLDER = WIKT_CLEANING_DIR / 'en' 
NEF_FOLDER = WIKT_CLEANING_DIR / 'nl' 
NNF_FOLDER = WIKT_CLEANING_DIR / 'nl' 

EEF_FILE = EEF_FOLDER / 'EEF_V2.jsonl'
ENF_FILE = ENF_FOLDER / 'ENF_V2.jsonl'
NEF_FILE = NEF_FOLDER / 'NEF_V2.jsonl'
NNF_FILE = NNF_FOLDER / 'NNF_V2.jsonl'

try:
    from tqdm import tqdm

    logger.remove(0)
    logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)
except ModuleNotFoundError:
    pass