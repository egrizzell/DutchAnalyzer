import os
from collections import OrderedDict
from types import new_class
from tqdm import tqdm
import re
from array import array
import ast
from itertools import groupby
import pandas as pd
import numpy as np
import ujson
from pathlib import Path
import datetime


def count_lines_with_progress(file_path, chunk_size=1024 * 1024):
    total_size = os.path.getsize(file_path)
    lines = 0
    longest_line = 0
    num_chunks_longest = 0
    current_chunks_count = 1
    with open(file_path, 'rb') as f, tqdm(total=total_size, unit='B', unit_scale=True, desc="Counting Lines") as pbar:
        while chunk := f.read(chunk_size):
            chunk_count = chunk.count(b'\n')
            
            lines += chunk_count
            pbar.update(len(chunk))
    return lines

def get_longest_line(file_path, chunk_size=1024 * 1024):
    total_size = os.path.getsize(file_path)
    lines = 0
    longest_line = 0
    longest_lines = []
    num_chunks_longest = 0
    current_chunks_count = 1
    current_line = 0
    lowest_chunks_per_line = 1000000
    with open(file_path, 'rb') as f, tqdm(total=total_size, unit='B', unit_scale=True, desc="Counting Lines") as pbar:
        current_chunk = b''
        last_chunk = b''
        while chunk := f.read(chunk_size):
            chunk_count = chunk.count(b'\n')
            if chunk_count < lowest_chunks_per_line:
                lowest_chunks_per_line = chunk_count
                longest_lines.append(((1, chunk_count), chunk))

            else:
                if chunk_count == 0:
                    if current_chunks_count == 1:
                        current_chunk = last_chunk
                    current_chunk += chunk
                    current_chunks_count += 1
                else:
                    last_chunk = chunk
                    if current_chunks_count > num_chunks_longest:
                        longest_line = current_chunk
                        num_chunks_longest =  current_chunks_count
                        longest_lines.append((current_chunks_count, current_chunk))
                        current_chunks_count = 1

            lines += chunk_count
            pbar.update(len(chunk))
            
    return lines, longest_lines
                
def check_has_valid_chars(text, num_to_check=2):
    allowed_letters = "a-zA-ZáéíóúÁÉÍÓÚèàòùÈÀÒÙëïöüËÏÖÜ"
    # punctuation (we escape it safely)
    allowed_punct = re.escape("'- .,;:")
    # combine safely; note the hyphen is at the *end* to avoid range issues
    allowed_chars = allowed_letters + allowed_punct + "-"
    try: 
        text = str(text).strip()
        first_chars = text[:num_to_check]  # take first one or two characters
        # check each character individually
        for ch in first_chars:
            if not re.match(f"[{allowed_chars}]", ch):
                return False
        return True
    except Exception as e: 
        print("Error:", e)
        return False
    
def has_cjk_or_arabic_fast(text: str, limit: int = 50) -> bool:
    """Return True if the first `limit` characters contain
    any Chinese, Japanese, Korean, or Arabic/Farsi character."""
    for ch in text[:limit]:
        cp = ord(ch)
        # CJK (Chinese/Japanese/Korean)
        if (
            0x4E00 <= cp <= 0x9FFF or  # CJK Unified Ideographs
            0x3400 <= cp <= 0x4DBF or  # CJK Ext A
            0xF900 <= cp <= 0xFAFF or  # CJK Compatibility
            0x3040 <= cp <= 0x30FF or  # Hiragana + Katakana
            0x31F0 <= cp <= 0x31FF or  # Katakana Extensions
            0xAC00 <= cp <= 0xD7AF or  # Hangul Syllables
            # Arabic / Farsi
            0x0600 <= cp <= 0x06FF or
            0x0750 <= cp <= 0x077F or
            0x08A0 <= cp <= 0x08FF or
            0xFB50 <= cp <= 0xFEFF
        ):
            return True  # stop immediately
    return False
    
def safe_dict(obj_str: str):
    if isinstance(obj_str, str):
        try:
            return ast.literal_eval(obj_str)
        except Exception:
            return ""       # fallback
        
def lookup_lang_code(lang):
    if not lang:
        return None
    lang = lang.lower()
    names_to_codes = {
        # English
    "english": "en",
    "engels": "en",
    "eng": "en",
    "modern english": "en",
    "modern_engels": "en",
    "modern engels": "en",

    # Simple English
    "simple english": "simple",
    "simple_english": "simple",
    "simplified english": "simple",
    "eenvoudig engels": "simple",

    # Dutch
    "dutch": "nl",
    "nederlands": "nl",
    "nld": "nl",

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
    'oudsaksisch':'osx'
    }
    return names_to_codes.get(lang)

def lookup_lang_from_code(lang_code):
    if not lang_code:
        return None
    
    codes_to_names = {
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
        'standard': 'limburgish'
    },
    'osx': {
        'standard': 'pre_dutch'
        }
    }
    if lang_code:
        name = codes_to_names.get(lang_code)
        if name:
            return name['standard']
        return None
    return None

def standardize_translation(obj: dict, lang_codes_to_keep=[], keep_no_lang=False, source='EEF', sense_index=-1) -> dict | None:
    if lang_codes_to_keep == []:
        lang_codes_to_keep = ['nl', 'en', 'simple', 'ang', 'dum', 'nds', 'odt', 'nds-nl', 'enm', 'eng', 'nld']

    word = obj.get('word', '')
    sense = obj.get('sense', '')

    if word == '' and sense == '':
        return None
    
    lang_code = obj.get('lang_code', '').lower()
    lang = obj.get('lang', '').lower()
    
    if lang_code == '':
        lang_code = obj.get('code', '').lower()
        
    new_translation = {}
    if keep_no_lang == False and lang_code == '' and lang == '':
        return None

    if lang_code == '' and lang == '':
        lang_code = 'unk'
        lang = 'unknown'

    elif lang == '':
        lang = lookup_lang_from_code(lang_code)

    elif lang_code == '':
        lang_code = lookup_lang_code(lang)

        if lang_code not in lang_codes_to_keep:
            return None
    
    standard_lang = lookup_lang_from_code(lang_code)
    if not standard_lang:
        return None    
    pos = obj.get('pos', '')
    new_translation = {'word': word,
                        'pos': pos,
                        'lang_code': lang_code,
                        'lang': lang,
                        'standard_lang': standard_lang}
    
    obj_items = sorted(obj.items())
    for key, val in obj_items:
        if key not in new_translation:
            new_translation[key] = val
    print(new_translation)
    return new_translation



def sort_dict(obj, exclude=[], prepend=[]):
    new_obj = {}
    if prepend:
        for p in prepend:
            if p in obj:
                new_obj[p] = obj[p]

    sorted_items = sorted(obj.items())
    for k, v in sorted_items:
        if k not in exclude and k not in prepend:
            new_obj[k] = v
    return new_obj

def sort_dict_list(obj: list, sort_by='word', sort_dicts=False, sort_dicts_kwargs={'exclude':[], 'prepend':['word']}) -> list:
    if not obj:
        return []
    sorted_obj = sorted(obj, key=lambda obj: obj[sort_by])
    if sort_dicts:
        for i, d in enumerate(sorted_obj):
            nd = sort_dict(d, sort_dicts_kwargs['exclude'], sort_dicts_kwargs['prepend'])
            sorted_obj[i] = nd
    return sorted_obj

def sort_translations(translations: list, sort_by='lang_code') -> list:
    if not translations:
        return []
    sorted_translations = sorted(translations, key=lambda translations: translations[sort_by])
    return sorted_translations
    
def filter_categories(obj: list, lang_code=''):
    new_categories = []
    if not obj or not isinstance(obj, list):
        return None
    
    for i, category in enumerate(obj):
        if isinstance(category, str):
            cut_cat = ''
            if category.startswith('Terms with') and category.endswith('translations') and 'incorrect' not in category:
                cut_cat = category.removeprefix('Terms with')
                cut_cat = cut_cat.removesuffix('translations')
                standard_lang = lookup_lang_code(cut_cat)
                if standard_lang:
                    new_categories.append(category)
              
            elif category.startswith('Woorden in het'):
                cut_cat = category.removeprefix('Woorden in het')
                standard_lang = lookup_lang_code(cut_cat)
                if standard_lang:
                    new_categories.append(category)
            
            elif category.startswith("Woorden met") and 'referenties' in category:
                continue
            elif "Woorden in het Nederlands met audioweergave" == category:
                continue
            elif 'examples' in category:
                continue
            else:
                new_categories.append(category)
    
    return new_categories



def sort_entry(obj, code=None, lang=None, standard_lang=None):
    new_obj = OrderedDict()
    if not obj or not isinstance(obj, [dict, OrderedDict]):
        return None
    new_obj['word'] = obj.pop('word', '')
    new_obj['pos'] = obj.pop('pos', '')
    if code:
        new_obj['lang_code'] = code
    else:
        code = obj.pop('lang_code', '')
        new_obj['lang_code'] = code
        obj.pop('lang_code', '')
    if lang:
        new_obj['lang'] = lang
        obj.pop('lang', '')
    else: 
        new_obj['lang'] = obj.pop('lang', '')
    
    if standard_lang:
        new_obj['standard_lang'] = standard_lang
        obj.pop('lang', 'standard_lang')
    else:
        standard_lang = obj.pop('standard_lang', '')
        if not standard_lang:
            standard_lang = lookup_lang_from_code(code)

        new_obj['standard_lang'] = standard_lang
        obj.pop('lang', 'standard_lang')
    

    senses = obj.pop('senses', [])
    if senses:
        senses = sorted(senses)
    new_obj['senses'] = senses

    translations = obj.pop('translations', [])
    if translations:
        translations = sort_translations(translations)

    new_items = sort_dict(obj, exclude=new_obj.keys() + ['translations', 'senses'])
    
    new_obj['translations'] = translations

    return new_obj



def sort_filter_sense(obj: dict, pop_examples=True) -> dict:
    new_sense = OrderedDict()
    glosses = obj.pop('glosses', '')
    translations = obj.pop('translations', '')
    translations = sort_translations(translations)
    form_of = obj.pop('form_of', '')
    if not form_of:
        form_of = obj.get('forms')
    
    obj.pop('senseid', '')
    obj.pop('wikidata', '')
    obj.pop('wikipedia', '')
    obj.pop('attestations', '')
    obj.pop('head_nr', '')

    if pop_examples:
        obj.pop('examples','')
    if glosses:
        if isinstance(glosses[0], list):
            print('list', glosses)
    new_sense['glosses'] = glosses
    new_sense['form_of'] = form_of
    synonyms = obj.get('synonyms')
    synonyms = sort_dict_list(synonyms, 'word', True)
    new_sense['synonyms'] = synonyms
    sorted_obj=sort_dict(obj, list(new_sense.keys()) + ['translations'])
    for k,v in sorted_obj.items():
        if k not in new_sense:
            new_sense[k] = v
    new_sense['translations'] = translations
    return new_sense
    

def sort_standardize_entry(obj: dict, pop_examples=True) -> dict:
    new_obj = {}
    word = obj.get('word')
    if not word:
        return None
    pos = obj.get('pos')
    if not pos:
        return None
    if pos == 'name' or pos == 'abbrevation' or pos == 'proverb':
        return None
    
    new_obj['word'] = word
    new_obj['pos'] = pos
    code = obj.get('lang_code')
    lang = obj.get('lang', '').lower()
    if not code:
        code = obj.get('code')
        if code:
            standard_lang = lookup_lang_from_code(code)
            if standard_lang:
                obj['lang_code'] = code
                
                obj.pop('code')
            else:
                return None
        else:
            code = lookup_lang_code(lang)
            if not code:
                return None
    
    standard_lang = obj.get('standard_lang')
    if not standard_lang:
        standard_lang = lookup_lang_from_code(code)
    
    if not standard_lang:
        return None
    
    if lang == '':
        lang = standard_lang
    new_obj['lang_code'] = code
    new_obj['lang'] = lang
    new_obj['standard_lang'] = standard_lang

    ## Filter Categories
    categories = obj.get('categories')
    if categories:
        categories = filter_categories(categories)
        if categories:
            new_obj['categories'] = sorted(categories)
        else: new_obj['categories'] = []
    else:
        new_obj['categories'] = []

    ## Filter Translations
    new_translations = []
    translations = obj.get('translations')
    
    if translations:
        for t in translations:
            translation = standardize_translation(t)
            if translation:
                new_translations.append(translation)
        if new_translations:
            new_translations = sort_translations(new_translations)
    new_obj['translations'] = new_translations
    
    ## Filter Senses
    new_senses = []
    senses = obj.get('senses')
    if not senses:
        return None
    if senses:
        for sense in senses:
            new_sense = sort_filter_sense(sense)
            if new_sense and sense not in new_senses:
                new_senses.append(new_sense)
        if not new_senses:
            new_senses = []
    new_obj['senses'] = new_senses

    obj_keys = sorted(list(obj.keys()))
    for key in obj_keys:
        if key not in new_obj:
            new_obj[key] = obj[key]

    
    if new_obj:
        return new_obj
    return None

def make_key_tuples(obj, out_set=set(), prev_level_tuple=()):
    if not obj:
        return out_set
    if isinstance(obj, (str, int, float)):
        level_tuple = prev_level_tuple + (type(obj))
        out_set.insert(level_tuple)
    elif isinstance(obj, dict):
        obj_items = obj.items()
        for k, v in obj_items:
            level_tuple = prev_level_tuple + (k)
            out_set.insert(level_tuple)
            out_set = make_key_tuples(v, out_set, level_tuple)
    elif isinstance(obj, list):
        level_tuple = prev_level_tuple + (list)
        out_set.insert(level_tuple)
        for i, v in enumerate(obj):
            out_set = make_key_tuples(v, out_set, level_tuple)
    return out_set