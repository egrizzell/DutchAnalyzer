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
import json


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

def filter_translations_regex(obj_str: str):
    translations_pattern = r'"translations"\s*:\s*\[({.*?})\]'
    translations_block = re.compile(translations_pattern, re.DOTALL)
    gen_lang_block_pattern = r'(\{[^{}]*?"lang"\s*:\s*"(English|Engels|Dutch|Nederlands|Old English|Oudengels|Old Saxon|Oudnederlands|Dutch Low Saxon|Middle Dutch|Middelnederlands|Old Dutch|Middle English|Limburgish|Oudnederlands|Middenengels|Middelengels|Simple English|Eenvoudig Engels)"[^{}]*?\})'
    rarer_lang_block_patterns = r'\{[^{}]*?"lang"\s*:\s*"(Old English|Oudengels|Old Saxon|OudenNederlands|Dutch Low Saxon|Middle Dutch|Old Dutch|Middle English|Limburgish)"[^{}]*?\}'
    gen_lang_block = re.compile(gen_lang_block_pattern, re.DOTALL)
    en_translation_pattern = r'\{[^{}]*?"lang_code"\s*:\s*"(en|eng)"[^{}]*?\}'
    nl_translation_pattern = r'\{[^{}]*?"lang_code"\s*:\s*"nl"[^{}]*?\}'
    engels_translation_pattern = r'\{[^{}]*?"lang"\s*:\s*"Engels"[^{}]*?\}'
    english_translation_pattern = r'\{[^{}]*?"lang"\s*:\s*"English"[^{}]*?\}'
    dutch_translation_pattern = r'\{[^{}]*?"lang"\s*:\s*"Dutch"[^{}]*?\}'
    nederlands_translation_pattern = r'\{[^{}]*?"lang"\s*:\s*"Nederlands"[^{}]*?\}'
    match = translations_block.search(obj_str)
    
    while match is not None:
        if match:
            new_translations_str = '"translations": ['
            start, end = match.span()
            m = match.group(0)
            dn = gen_lang_block.findall(m)
        if dn:
            
            dn = [safe_dict(x[0]) for x in dn]
            str_dn = '[' + ', '.join(json.dumps(x) for x in dn) + ']'
            
            obj_str = obj_str[:start]+ '"translations": ' + str_dn + obj_str[end:]
            match = translations_block.search(obj_str, start + len(str_dn))
        else:
            to_remove_end = end
            if end < len(obj_str) and obj_str[end] == ',':
                to_remove_end += 1
            obj_str = obj_str[:start] + obj_str[to_remove_end:]
            match = translations_block.search(obj_str, start)

    return obj_str

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
    new_translation = {'word': word,
                        'lang_code': lang_code,
                        'lang': lang,
                        'standard_lang': standard_lang}
    
    obj_items = sorted(obj.items())
    for key, val in obj_items:
        if key not in new_translation:
            new_translation[key] = val
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
    
def filter_categories(obj: list):
    new_categories = []

    if not obj or not isinstance(obj, list):
        return None
    
    for i, category in enumerate(obj):
        if isinstance(category, str):
            cut_cat = ''
            if category.startswith('Terms with') and category.endswith('translations') and 'incorrect' not in category:
                cut_cat = category.removeprefix('Terms with')
                cut_cat = cut_cat.removesuffix('translations')
                cut_cat = cut_cat.strip()
                lang_code2 = lookup_lang_code(cut_cat)
                if lang_code2:
                    new_categories.append(category)
            elif category.startswith('Requests for'):
                cut_cat = category.removeprefix('Requests for review of ')
                cut_cat = category.removeprefix('Requests for attention concerning ')
                cut_cat = category.removeprefix('Requests for translations into ')

                cut_cat = category.removesuffix(' translations')
                cut_cat = category.removesuffix(' entries')

                cut_cat = cut_cat.strip()
                lang_code2 = lookup_lang_code(cut_cat)
                if lang_code2:
                    new_categories.append(category)
                

            elif category.startswith('Woorden in het'):
                cut_cat = category.removeprefix('Woorden in het ')
                lang_code2 = lookup_lang_code(cut_cat.strip())
                if lang_code2:
                    new_categories.append(category)  
            
            elif 'transliterations' in category:
                cut_cat = category.removeprefix('Automatic ')
                cut_cat = cut_cat.removesuffix(' terms with redundant transliterations')
                cut_cat = cut_cat.removesuffix(' terms with non-redundant manual transliterations')
                cut_cat = cut_cat.removesuffix(' transliterations containing ambiguous characters')
                lang_code2 = lookup_lang_code(cut_cat.strip())
                if lang_code2:
                    new_categories.append(category)
            elif category.endswith('terms in nonstandard scripts'):
                cut_cat = category.removesuffix(' terms in nonstandard scripts')
                lang_code2 = lookup_lang_code(cut_cat.strip())
                if lang_code2:
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

def get_file_wl_code(file):
    if isinstance(file, Path):
        file = file.stem

    elif '\\' in file and '.' in file:
        file = file.split('\\')[-1]
        file = file.split('.')[0]
        
    if 'EEF' in file:
        return 'EEF'
    if 'ENF' in file:
        return 'ENF'
    if 'NNF' in file:
        return 'NNF'
    if 'NEF' in file:
        return 'NEF'
    if 'ENR' in file:
        return 'ENR'
    if 'EER' in file:
        return 'EER'
    if 'NNR' in file:
        return 'NNR'
    if 'NER' in file:
        return 'NER'
    return ''

def filter_pos(obj, banned_pos = ['num', 'symbol', 'phrase', 'character', 'punct', 'abbrev', 'proverb']):
    if obj.get('pos', '') in banned_pos:
        return None
    return obj

def overwrite_file(file, new_file):
    file_path = Path(file)
    new_file_path = Path(new_file)
    if file_path.exists() and new_file_path.exists():
        os.remove(file)
        Path.rename(new_file_path, file)
    print(f'{file} was overwritten with {new_file}')

def current_filter_obj(obj): 
    if obj:
        obj = sort_standardize_entry(obj)
    return obj

def overwrite_file_with_filter_operations(file, filter_ops=['standardize_entries'], batch_size=10000):
    batch = []
    if isinstance(file, Path):
        file = file.__str__()
    
    total_lines = count_lines_with_progress(file)
    file_list = file.split('\\')
    out_name = file_list[-1].split('.')[0] + '_temp.jsonl'
    out_file = '\\'.join(file_list[0:-1]) + '\\' +out_name
    if 'add_wl_code' in filter_ops:
        wl_code = get_file_wl_code(file)
        
    with open(file, 'r', encoding='utf-8') as f:
        with open(out_file, 'w+', encoding='utf-8') as out:
            for i, line in tqdm(enumerate(f), total=total_lines):
                obj = json.loads(line)
                if obj:
                    if 'current_filter' in filter_ops:
                        obj = current_filter_obj(obj)
                        if not obj:
                            continue
                    if 'pos' in filter_ops:
                        obj = filter_pos(obj)
                        if not obj:
                            continue
                    if 'standardize_entries' in filter_ops:
                        obj = sort_standardize_entry(obj)
                        if not obj:
                            continue
                    if 'add_wl_code' in filter_ops:
                        if wl_code and obj:
                            obj['wl_code'] = wl_code
                    if obj:
                        batch.append(obj)
                    if len(batch) > batch_size:
                        for item in batch:
                            json.dump(item, out, ensure_ascii=False)
                            out.write('\n')
                        batch = []
            if batch:
                for item in batch:
                    json.dump(item, out, ensure_ascii=False)
                    out.write('\n')
    response = input(f'are you sure you want to overwrite {file} with {out_file}? y/n')
    if response == 'y':
        overwrite_file(file, out_file)
    else:
        print('aborted temp file saved as: ', out_file)


def sort_filter_sense(obj: dict, pop_examples=True) -> dict:
    new_sense = {}
  
    glosses = obj.pop('glosses', '')
    translations = obj.pop('translations', '')
    translations = sort_translations(translations)
    form_of = obj.pop('form_of', '')
    if not form_of:
        form_of = obj.get('forms', '')
    
    obj.pop('senseid', '')
    obj.pop('wikidata', '')
    obj.pop('wikipedia', '')
    obj.pop('attestations', '')
    obj.pop('head_nr', '')

    if pop_examples:
        obj.pop('examples','')
    new_sense['glosses'] = glosses
    if form_of:
        new_sense['form_of'] = form_of
    synonyms = obj.get('synonyms')
    if synonyms:
        synonyms = sort_dict_list(synonyms, 'word', True)
        new_sense['synonyms'] = synonyms
    
    
    sorted_keys = sorted(list(obj.keys()))
    for key in sorted_keys:
        if key not in new_sense and key != 'translations':
            new_sense[key] = obj[key]
    if translations:
        new_sense['translations'] = translations

    return new_sense
    

def sort_standardize_entry(obj: dict, pop_examples=True) -> dict:
    new_obj = {}
    word = obj.get('word')
    if not word:
        return None
    if has_cjk_or_arabic_fast(word):
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

    try:
        ## Filter Categories
        categories = obj.get('categories')
        if categories:
            categories = filter_categories(categories)
            if categories:
                
                new_obj['categories'] = sorted(categories)
            
            else: new_obj['categories'] = []
        else:
            new_obj['categories'] = []
        
    except:
        print('categories failed ', categories)
        raise
    
    
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

    if 'forms' in obj:
        new_obj['forms'] = obj['forms']
    ## Filter Etymologies
    new_etymology_templates = []
    if 'etymology_templates' in obj:
        for ety_template in obj['etymology_templates']:
            if 'args' in ety_template:
                if '1' in ety_template['args']:
                    lc = ety_template['args']['1']
                    if lookup_lang_from_code(lc):
                        new_etymology_templates.append(ety_template)
            elif 'name' in ety_template:
                name = ety_template['name']
                name = name.split()
                for n in name:
                    if lookup_lang_from_code(n):
                       new_etymology_templates.append(ety_template)          
        if new_etymology_templates:
            new_obj['etymology_templates'] = new_etymology_templates

    ## Filter Sounds 
    new_sounds = []
    if 'sounds' in obj:
        for sound in obj['sounds']:
            if isinstance(sound, dict):
                sound.pop('ogg_url', '')
                sound.pop('mp3_url', '')
                sound.pop('audio', '')
                if sound:
                    new_sounds.append(sound)
    ## Add Remaining Keys
    obj_keys = sorted(list(obj.keys()))
    for key in obj_keys:
        if key not in new_obj and key != 'translations':
            if key == 'sounds' and new_sounds:
                new_obj['sounds'] = new_sounds
            else:
                new_obj[key] = obj[key]

    ## Filter Translations
    new_translations = []
    translations = obj.get('translations')
    try:
        if translations:
            for t in translations:
                
                translation = standardize_translation(t)
                if translation:
                    new_translations.append(translation)
            if new_translations:

                new_translations = sort_translations(new_translations)
            
            new_obj['translations'] = new_translations
    except:
        print('translations failed', new_translations)
        raise

    if new_obj:
        return new_obj
    return None

def extract_words_senses(raw_entry: dict):
    word = raw_entry.get("word")
    pos = raw_entry.get("pos", 'unknown')
    senses = raw_entry.get("senses")
    translations = raw_entry.get("translations")
    lang_code = raw_entry.get("lang_code")
    forms = raw_entry.get('forms')
    synonyms = raw_entry.get('synonyms')
    if not forms:
        forms = raw_entry.get('form_of')
    glosses = []
    sense_translations = []
    word_entry = {'word': word,
                  'pos': pos, 
                  'lang_code': lang_code}
    if senses:
        word_entry['senses'] = {}
        for i, sense in enumerate(senses):
            new_sense = {}
            if 'glosses' in sense:
                glosses = sense['glosses']
                new_sense['glosses'] = glosses
            if 'translations' in sense or 'translation' in sense:
                sense_translations = sense['translations']
                if not sense_translations:
                    sense_translations = sense_translations['translation']
                new_sense['translations'] = sense_translations
            if 'form_of' in sense or 'forms' in sense:
                forms = sense.get('form_of')
                if not forms: forms = sense['forms']
                new_sense['forms'] = forms
            if 'alt_of' in sense:
                new_sense['alt_of'] = sense.get('alt_of')
            if 'synonyms' in sense:
                new_sense['synonyms'] = sense.get('synonyms')
            word_entry['senses'][i] = new_sense

    if translations:
        word_entry['translations'] = translations
    if forms:
        word_entry['forms'] = forms
    if synonyms:
        word_entry['synonyms'] = synonyms
    if 'etymology_templates' in raw_entry:
        word_entry['etymology_templates'] = raw_entry['etymology_templates']
    if 'wl_code' in raw_entry:
        word_entry['wl_code'] = raw_entry['wl_code']
    return word_entry


def en_keep_before_load(line):
    line = line.strip()
    line_len = len(line)
    brack_index = line.rfind(']')
    if brack_index == line_len - 2:
      left_bracket = line.rfind('[')
      line = line[:left_bracket].strip()
      brack_index = line.rfind(']')
      left_bracket = line.rfind('[')
      line_len = len(line)

    word_index = line.rfind(', "word": "')
    lcr_index = line.rfind(', "lang_code": "')

    if lcr_index > 0:
      lang_code = line[lcr_index + len(', "lang_code": "') - 1: lcr_index + len('"lang_code": "') + 4]
      lang_code = lang_code.strip('"')
      lang_code = lang_code.strip()
      if lang_code:
        if not lookup_lang_from_code(lang_code):
          
          return False
     
    if word_index:
        end = line[word_index + len(', "word": "') - 1:]
        end = end.find(',')
        word = line[word_index + len(', "word": '):end]
        word = word.strip('"')
        if word:
          if has_cjk_or_arabic_fast(word):
            return False
          if not check_has_valid_chars(word):
            return False
    pos_index = line.rfind('], "pos": "')
    
    if pos_index > 0:
        end_i = line.find(',', pos_index+4)
        pos = line[pos_index+len('], "pos": "'):end_i]
        pos = pos.strip('"')
        pos = pos.strip()
        banned_pos = ['num', 'symbol', 'phrase', 'character', 'punct', 'abbrev', 'proverb']
        if pos in banned_pos:
           return False
    return True

def nl_keep_before_load(line: str) -> bool:
    
    if has_cjk_or_arabic_fast(line, 30):
        return False
    
    lc_loc = line.find('"lang_code": "', 0, 70)

    if lc_loc > 0:
        start = lc_loc+len('"lang_code": "')
        lc_end = line.find('"', start)
        lc = line[start:lc_end]
        
        lc = lc.strip()
        if not lookup_lang_from_code(lc) and lc != 'unknown':
            return False
        
    word_loc = line.find('"word": "')
    if word_loc == 1:
        end = line.find('"', word_loc + len('"word": "'))
        word = line[word_loc + len('"word": "'):end].strip()
        if not check_has_valid_chars(word):
            return False
    
    banned_pos = ['num', 'symbol', 'phrase', 'character', 'punct', 'abbrev', 'proverb']
    pos_loc = line.find('"pos": "')
    if pos_loc == -1:
        return False
    cut_line = line[pos_loc + len('"pos": "'):]
    end = cut_line.find('"')
    pos = cut_line[:end].strip()
    if pos in banned_pos:
        return False
    return True

def process_file(in_file, entries_out_file, wl_code, definitions_out_file=None, batch_size=1000, break_point=-1):
    batch = []
    entries_batch = []
    lang_2_lines = []
    other_lines = []
    error_lines = []
    with open(in_file, 'r', encoding='utf-8') as f:
        with open(entries_out_file, 'w+', encoding='utf-8') as out:
            
            for i, line in tqdm(enumerate(f), total=count_lines_with_progress(f)):
                if break_point > 0:
                    if i > break_point:
                        print(entries_batch)
                        break
                if line:
                    curr_wl_code = ''
                    if wl_code == 'ERAW' or wl_code == 'NRAW':
                        
                        line = filter_translations_regex(line)
                        if wl_code == 'ERAW':
                            curr_wl_code = 'E'
                            if not en_keep_before_load(line):
                                continue
                        if wl_code == 'NRAW':
                            curr_wl_code = 'N'
                            if not nl_keep_before_load:
                                continue      

                    try:
                        obj = json.loads(line)
                        obj = sort_standardize_entry(obj)
                        if obj:
                            if curr_wl_code:
                                curr_wl_code = curr_wl_code + obj.get('lang_code') + 'R'
                            else:
                                curr_wl_code = wl_code

                            obj['wl_code'] = curr_wl_code
                            lang_code = obj.get('lang_code')
                            

                            entries_batch.append(obj)

                            if len(entries_batch) > batch_size:
                                for entry in entries_batch:
                                    json.dump(entry, out, ensure_ascii=False)
                                    out.write('\n')
                                entries_batch = []
                            if definitions_out_file:
                                word_entry = extract_words_senses(obj)
                                batch.append(word_entry)
                                if len(batch) > batch_size:
                                    with open(definitions_out_file, 'a+', encoding='utf-8') as def_out: 
                                        for entry in batch:
                                            json.dump(entry, def_out, ensure_ascii=False)
                                            def_out.write('\n')
                                        batch = []
                    except Exception as e:
                        error_lines.append((i, obj))
                        print(line)
                        print("Error on line: ", i, " Error: ", e)
                        break
            if entries_batch:
                for entry in entries_batch:
                    json.dump(entry, out, ensure_ascii=False)
                    out.write('\n')  
            if batch and definitions_out_file:
                with open(definitions_out_file, 'a+', encoding='utf-8') as def_out: 
                    for entry in batch:
                        json.dump(entry, def_out, ensure_ascii=False)
                        def_out.write('\n')
    return entries_batch, batch, error_lines

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

def reformat_sounds(obj: dict):
    ipas = []
    rhymes = []
    other = []
    tags = []

    sounds = obj.get('sounds')
    if sounds:
        for sound in sounds:
            ipa = sound.get('ipa')
            rhyme = sound.get('rhymes')
            tag = sound.get('tags')
            if ipa:
                if ipa not in ipas:
                    ipas.append(ipa)
            if rhyme:
                if rhyme not in rhymes:
                    rhymes.append(rhyme)
            if tag:
                if tag not in tags:
                    tags.append(tag)
        if ipas:
            obj['ipa'] = ipas
        if rhymes:
            obj['rhymes'] = rhymes
        if tags:
            obj['sound_tags'] = tags
        obj.pop('sounds')
