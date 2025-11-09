from dotenv import load_dotenv
from dutchanalyzer.config import INTERIM_DATA_DIR, EXTERNAL_DATA_DIR, PROCESSED_DATA_DIR
from pathlib import Path
import os
from dutchanalyzer.config import *
import re
import tqdm
from functools import partial
from typing import Any

if not hasattr(os, "pathconf"):
    os.pathconf = lambda *args, **kwargs: 255

from wikitextprocessor import Wtp, WikiNode, NodeKind, Page
import wikitextprocessor.dumpparser as dumpparser
from wikitextprocessor.dumpparser import process_dump
from wikitextprocessor.dumpparser import save_pages_to_file

from wiktextract import (
    WiktextractContext,
    WiktionaryConfig,
    parse_wiktionary,
)

def main():
    pass

if __name__ == "__main__":
    en_dump_path = 'data/raw/wiktionary/en_dump/enwiktionary-20251025-pages-articles.xml.bz2'

    config = WiktionaryConfig(
        dump_file_lang_code="en",
        capture_language_codes=["en", "nl"],
        capture_translations=True,
        capture_pronunciation=True,
        capture_linkages=True,
        capture_compounds=True,
        capture_redirects=True,
        capture_examples=True,
        capture_etymologies=True,
        capture_descendants=True,
        capture_inflections=True,
    )
    wxr = WiktextractContext(Wtp(), config)

    RECOGNIZED_NAMESPACE_NAMES = [
        "Main",
        "Category",
        "Appendix",
        "Project",
        "Thesaurus",
        "Module",
        "Template",
        "Reconstruction"
    ]

    namespace_ids = {
        wxr.wtp.NAMESPACE_DATA.get(name, {}).get("id")
        for name in RECOGNIZED_NAMESPACE_NAMES
    }