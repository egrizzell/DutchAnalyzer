LANG_CODES_TO_NAMES = {
    "en": {
        "standard": "english",
        "en_name": "english",
        "nl_name": "engels"
    },
    "eng": {
        "standard": "english",
        "en_name": "english",
        "nl_name": "engels"
    },
    "nl": {
        "standard": "dutch",
        "en_name": "dutch",
        "nl_name": "nederlands"
    },
    "nld": {
        "standard": "dutch",
        "en_name": "dutch",
        "nl_name": "nederlands"
    },
    "simple": {
        "standard": "simple_english",
        "en_name": "simple english",
        "nl_name": "eenvoudig engels"
    },
    "ang": {
        "standard": "old_english",
        "en_name": "old english",
        "nl_name": "oudengels"
    },
    "enm": {
        "standard": "middle_english",
        "en_name": "middle english",
        "nl_name": "middelengels"
    },
    "dum": {
        "standard": "middle_dutch",
        "en_name": "middle dutch",
        "nl_name": "middelnederlands"
    },
    "odt": {
        "standard": "old_dutch",
        "en_name": "old dutch",
        "nl_name": "oudnederlands"
    },
    "nds": {
        "standard": "low_saxon",
        "en_name": "low german / low saxon",
        "nl_name": "nedersaksisch"
    },
    "nds-nl": {
        "standard": "dutch_low_saxon",
        "en_name": "dutch low saxon",
        "nl_name": "nedersaksisch (nederland)"
    },
    'lim': {
        'standard': 'limburgish',
        'en_name': 'limburgish',
        'nl_name':'limburgs'
    },
    'osx': {
        'standard': 'pre_dutch',
        'en_name':'pre-dutch',
        'nl_name':'oudsaksisch'
        }
    }

LANG_NAMES_TO_CODES = {
        # English
    "english": "en",
    "engels": "en",
    "eng": "en",
    "modern english": "en",
    "modern_engels": "en",
    "modern engels": "en",

    # Simple English
    "simple":"simple",
    "simple english": "simple",
    "simple_english": "simple",
    "simplified english": "simple",
    "eenvoudig engels": "simple",

    # Dutch
    "dutch": "nl",
    "nederlands": "nl",
    "nld": "nl",
    "nl":"nl",

    # Old English
    "old english": "ang",
    "old_english": "ang",
    "anglo-saxon": "ang",
    'angelsaksisch': "ang",
    "oudengels": "ang",

    # Middle English
    "middle english": "enm",
    "middle_english": "enm",
    "middelengels": "enm",
    "middenengels": "enm",

    # Middle Dutch
    "middle dutch": "dum",
    "middle_dutch": "dum",
    "middelnederlands": "dum",

    # Old Dutch
    "old dutch": "odt",
    "old_dutch": "odt",
    "oudnederlands": "odt",
    
    # Low Saxon
    "low saxon": "nds",
    "low_saxon": "nds",
    "low german": "nds",
    "platduits": "nds",
    "nedersaksisch": "nds",

    # Dutch Low Saxon
    "dutch low saxon": "nds-nl",
    "dutch_low_saxon": "nds-nl",
    "nedersaksisch (nederland)": "nds-nl",
    'limburgs': 'lim',
    'oudsaksisch':'osx',
    'pre-dutch':'osx'
    }


POS_INFO = {
    "adj": {
        "nl_name": "bijvoeglijk naamwoord",
        "nl_abbr": "bn",
        "en_name": "adjective"
    },
    "adv": {
        "nl_name": "bijwoord",
        "nl_abbr": "bw",
        "en_name": "adverb"
    },
    
    "adv_phrase": {
        "nl_name": "bijwoordelijke bepaling",
        "nl_abbr": "bwb",
        "en_name": "adverbial phrase"
    },
    "article": {
        "nl_name": "lidwoorden",
        "nl_abbr": "lidw",
        "en_name": "article"
    },

    "circumpos": {
        "nl_name": "omzetsel",
        "nl_abbr": "oz",
        "en_name": "circumposition"
    },
    "conj": {
        "nl_name": "voegwoord",
        "nl_abbr": "vw",
        "en_name": "conjunction"
    },
    "contraction": {
        "nl_name": "samentrekking",
        "nl_abbr": "sam",
        "en_name": "contraction"
    },
    "det": {
        "nl_name": "bepaler",
        "nl_abbr": "bep",
        "en_name": "determiner"
    },
    "intj": {
        "nl_name": "tussenwerpsel",
        "nl_abbr": "tw",
        "en_name": "interjection"
    },
    "noun": {
        "nl_name": "zelfstandig naamwoord",
        "nl_abbr": "zn",
        "en_name": "noun"
    },
    "num": {
        "nl_name": "telwoord",
        "nl_abbr": "twl",
        "en_name": "numeral"
    },
    "particle": {
        "nl_name": "partikel",
        "nl_abbr": "part",
        "en_name": "particle"
    },
    "postp": {
        "nl_name": "achterzetsel",
        "nl_abbr": "az",
        "en_name": "postposition"
    },
    "pron": {
        "nl_name": "voornaamwoord",
        "nl_abbr": "vnw",
        "en_name": "pronoun"
    },
    "prep": {
        "nl_name": "voorzetsel",
        "nl_abbr": "vz",
        "en_name": "preposition"
    },
    
    "prep_phrase": {
        "nl_name": "voorzetselgroep",
        "nl_abbr": "vzg",
        "en_name": "prepositional phrase"
    },
    "verb": {
        "nl_name": "werkwoord",
        "nl_abbr": "ww",
        "en_name": "verb"
    },

    # --- Affixes ---
    "prefix": {
        "nl_name": "voorvoegsel",
        "nl_abbr": "vvg",
        "en_name": "prefix"
    },
    "suffix": {
        "nl_name": "achtervoegsel",
        "nl_abbr": "avg",
        "en_name": "suffix"
    },
    "infix": {
        "nl_name": "invoegsel",
        "nl_abbr": "ivg",
        "en_name": "infix"
    },
    "interfix": {
    "nl_name": "tussenvoegsel",
    "nl_abbr": "tvg",
    "en_name": "interfix"
},
    
    "circumfix": {
        "nl_name": "omsluitend affix",
        "nl_abbr": "oag",
        "en_name": "circumfix"
    }
}
    
    
