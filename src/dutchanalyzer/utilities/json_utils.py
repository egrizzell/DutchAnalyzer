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
import string
from dutchanalyzer.config import PROJ_ROOT
from dutchanalyzer.utilities.bool_filters import *
from dutchanalyzer.utilities.utils import make_temp_file_path


# Checking File Info
def count_lines_with_progress(file_path, chunk_size=1024 * 1024, quiet=False):
    if isinstance(file_path, Path):
        file_path = file_path.__str__()
    total_size = os.path.getsize(file_path)
    lines = 0
    if quiet == False:
        with open(file_path, 'rb') as f, tqdm(total=total_size, unit='B', unit_scale=True, desc="Counting Lines") as pbar:
            while chunk := f.read(chunk_size):
                chunk_count = chunk.count(b'\n')
                lines += chunk_count
                pbar.update(len(chunk))
        print(f'Lines in file: {lines}')
    else:
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                chunk_count = chunk.count(b'\n')
                lines += chunk_count
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
                
def save_batch_to_file(batch, out_file, mode):
    with open(out_file, mode, encoding='utf-8') as out:
        for obj in batch:
            json.dump(obj, out, ensure_ascii=False)
            out.write('\n')

# Safe Json Utils    
def safe_dict(obj_str: str):
    if isinstance(obj_str, str):
        try:
            return ast.literal_eval(obj_str)
        except Exception:
            return ""       


# Filtering Languages and Translations
def filter_translations_regex(obj_str: str):
    translations_pattern = r'"translations"\s*:\s*\[({.*?})\]'
    translations_block = re.compile(translations_pattern, re.DOTALL)
    gen_lang_block_pattern = r'(\{[^{}]*?"lang"\s*:\s*"(English|Engels|Dutch|Nederlands|Old English|Oudengels|Old Saxon|Oudnederlands|Dutch Low Saxon|Middle Dutch|Middelnederlands|Old Dutch|Middle English|Limburgish|Oudnederlands|Middenengels|Middelengels|Simple English|Eenvoudig Engels)"[^{}]*?\})'
    gen_lang_block = re.compile(gen_lang_block_pattern, re.DOTALL)
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
                
                obj_str = obj_str[:start] + '"translations": ' + str_dn + obj_str[end:]
                match = translations_block.search(obj_str, start + len(str_dn))
            else:
                to_remove_end = end
                if obj_str[end] == ',':
                    to_remove_end += 1
                if obj_str[end + 1] == ']' or obj_str[end + 1] == '}':
                    if obj_str[start - 1] == ',':
                        start = start - 1
                    elif obj_str[start - 2] == ',':
                        start = start - 2
                obj_str = obj_str[:start] + obj_str[to_remove_end:]
                match = translations_block.search(obj_str, start)
    obj_str = obj_str.replace(', ]', ']')
    obj_str = obj_str.replace(', }', '}')
    return obj_str

def lookup_lang_code(lang):
    if not lang:
        return None
    lang = lang.lower()
    lang = lang.strip()
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
    if not lang_code:
        return None
    lang_code = lang_code.lower()
    lang_code = lang_code.strip()
    name = codes_to_names.get(lang_code)
    if name:
        return name['standard']
    return None

# Sorting 
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


def sort_translations(translations: list, sort_by='lang_code', sort_words=True) -> list:
    if not translations:
        return []
    if sort_words:
        sorted_translations = sorted(translations, key=lambda translations: translations['word'])
        split_dict = split_langs(sorted_translations)
        split_dict_keys = list(split_dict.keys())
        split_dict_keys.sort()
        sorted_translations = []
        if 'en' in split_dict_keys:
            sorted_translations.extend(split_dict['en'])
            split_dict_keys.remove('en')
        if 'nl' in split_dict_keys:
            sorted_translations.extend(split_dict['nl'])
            split_dict_keys.remove('nl')
        for k in split_dict_keys:
            sorted_translations.extend(split_dict[k])
    else:
        sorted_translations = sorted(translations, key=lambda translations: translations[sort_by])
    return sorted_translations

# Standardization of Entries
def standardize_translation(obj: dict) -> dict | None:
    word = obj.get('word', '')
    sense = obj.get('sense', '')

    if word == '' and sense == '':
        return None
    
    lang_code = obj.get('lang_code', '')
    lang = obj.get('lang', '').lower()
    
    if lang_code == '':
        lang_code = obj.get('code', '')
        
    new_translation = {}
    
    if lang_code == '' and lang == '':
        return None

    elif lang == '':
        lang = lookup_lang_from_code(lang_code)
        if not lang:
            return None

    elif lang_code == '':
        lang_code = lookup_lang_code(lang)
        if not lang_code:
            return None
        
    lang = lookup_lang_from_code(lang_code)
    if not lang:
        return None    
    new_translation = {'word': word,
                        'lang_code': lang_code,
                        'lang': lang}
    
    sorted_keys = sorted(list(obj.keys()))

    for key in sorted_keys:
        if key not in new_translation:
            new_translation[key] = obj[key]

    return new_translation


def filter_categories(obj: list) -> None|list:
    new_categories = []

    if not obj or not isinstance(obj, list):
        return None
    
    for i, category in enumerate(obj):
        if isinstance(category, str):
            category = category.strip()
            cut_cat = ''
            if category.startswith('Terms with') and category.endswith('translations') and 'incorrect' not in category:
                cut_cat = category.removeprefix('Terms with')
                cut_cat = cut_cat.removesuffix('translations')
                cut_cat = cut_cat.strip()
                lang_code2 = lookup_lang_code(cut_cat.lower())
                if lang_code2:
                    new_categories.append(category)
            elif category.startswith('Requests for'):
                cut_cat = category.removeprefix('Requests for review of ')
                cut_cat = category.removeprefix('Requests for attention concerning ')
                cut_cat = category.removeprefix('Requests for translations into ')
                
                cut_cat = cut_cat.removesuffix(' translations')
                cut_cat = cut_cat.removesuffix(' entries')

                cut_cat = cut_cat.strip()
                lang_code2 = lookup_lang_code(cut_cat.lower())
                if lang_code2:
                    new_categories.append(category)
                

            elif category.startswith('Woorden in het'):
                cut_cat = category.removeprefix('Woorden in het ')
                if 'met' in cut_cat:
                    cut_cat = cut_cat.split('met')[0]
                    
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
            elif category == 'Woorden in het Nederlands met audioweergave':
                continue
            elif 'examples' in category:
                continue
            else:
                new_categories.append(category)
    new_categories.sort()
    return new_categories


def sort_entry_keys(obj, start_keys=['word', 'pos', 'lang_code', 'lang', 'senses'], end_keys=['translations', 'wl_code'], groups=['forms', 'etymology', 'nyms', 'categories']):
    obj_keys = obj.keys()
    start = [c for c in start_keys if c in obj_keys]
    end = [c for c in end_keys if c in obj_keys]
    protected_keys = start 
    etymology_grouping = ['etymology_templates', 'etymology_text', 'etymology_tree', 'etymology_number']
    forms_grouping = ['form_of','forms', 'alt_of', 'inflection_templates', 'derived']
    nyms_grouping = ['synonyms', 'antonyms', 'hypernyms','hyponyms', 'troponyms', 'holonyms', 'meronyms']
    categories_grouping = ['categories', 'instances', 'links', 'related', 'topics']
    
    if groups:
        for group in groups:
            if 'forms' == group:
                forms_grouping = [c for c in forms_grouping if c in obj_keys]
                protected_keys += forms_grouping
            if 'etymology' == group:
                etymology_grouping = [c for c in etymology_grouping if c in obj_keys]
                protected_keys += etymology_grouping

            if 'nyms' == group:
                nyms_grouping = [c for c in nyms_grouping if c in obj_keys]
                protected_keys += nyms_grouping

            if 'categories' == group:
                categories_grouping = [c for c in categories_grouping if c in obj_keys]
                protected_keys += categories_grouping
    protected_keys = [c for c in protected_keys if c in obj_keys]
    unprotected_keys = [c for c in obj_keys if c not in protected_keys and c not in end]

    unprotected_keys.sort()
    return protected_keys + unprotected_keys + end

def get_file_wl_code(file):
    
    if isinstance(file, Path):
        file = file.__str__()
    else:
        file = str(file)
    # elif '\\' in file and '.' in file:
    #     file = file.split('\\')[-1]
    #     file = file.split('.')[0]
        
    if 'EEF' in file or 'eef' in file:
        return 'EEF'
    if 'ENF' in file or 'enf' in file:
        return 'ENF'
    if 'NNF' in file or 'nnf' in file:
        return 'NNF'
    if 'EOF' in file or 'eof' in file:
        return 'EOF'
    if 'NOF' in file or 'nof' in file:
        return 'NOF'
    if 'NEF' in file or 'nef' in file:
        return 'NEF'
    if 'ENR' in file or 'enr' in file:
        return 'ENR'
    if 'EER' in file or 'eer' in file:
        return 'EER'
    if 'NNR' in file or 'nnr' in file:
        return 'NNR'
    if 'NER' in file or 'ner':
        return 'NER'
    
    return ''



def overwrite_file(file, new_file, quiet=False):
    file_path = Path(file)
    new_file_path = Path(new_file)
    rel_file_path = file.relative_to(PROJ_ROOT)
    new_rel_file_path = new_file.relative_to(PROJ_ROOT)
    if file_path.exists() and new_file_path.exists():
        os.remove(file)
        Path.rename(new_file_path, file)
    
    if quiet == False:
        print(f'{rel_file_path} was overwritten with {new_rel_file_path}')

def sort_filter_sense(obj: dict, pop_examples=True) -> dict:
    new_sense = {}
  
    glosses = obj.get('glosses', '')
    translations = obj.get('translations', '')
    if not translations:
        translations = obj.get('translation', '')
    translations = sort_translations(translations)
   
    form_of = obj.get('form_of', '')
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
    
    if 'categories' in obj:
        categories = filter_categories(obj.get('categories'))
        if categories:
            new_sense['categories'] = categories
        else:
            obj.pop('categories', '')

    synonyms = obj.get('synonyms')
    if synonyms:
        synonyms = sort_dict_list(synonyms, 'word', True)
        new_sense['synonyms'] = synonyms
        
    if form_of:
        new_sense['form_of'] = form_of
    
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
    if not has_valid_chars(word):
        return None
    pos = obj.get('pos')
    if is_standard_banned_pos(pos):
        return None
    
    code = obj.get('lang_code')
    if code:
        if not lookup_lang_from_code(code):
            return None
    else:
        code = obj.get('code')
        if code:
            if lookup_lang_from_code(code):
                obj['lang_code'] = code
                obj.pop('code')
            else:
                return None
        else:
            lang = obj.get('lang', '').lower()
            code = lookup_lang_code(lang)
            if not code:
                return None
    
    lang = lookup_lang_from_code(code)
    if not lang:
        return None
    
    new_keys = sort_entry_keys(obj)
    categories = obj.get('categories')
    if categories:
        new_categories = filter_categories(categories)
        if not new_categories:
            if categories == ['Woorden in het Sallands'] or categories == ['Woorden in het Achterhoeks'] or categories == ['Woorden in het Veluws']:
                new_categories = []
            elif categories == ['Woorden in het Drents'] or categories == ['Woorden in het Gronings'] or categories == ['Woorden in het Stellingwerfs']:
                new_categories = []
            else:
                print(categories)
                new_categories = categories
    
    ## Filter Senses
    new_senses = []
    senses = obj.get('senses')
    if not senses:
        return None
    for sense in senses:
        new_sense = sort_filter_sense(sense)
        if new_sense and sense not in new_senses:
            new_senses.append(new_sense)
        
    
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
        

    ## Filter Sounds 
    new_sounds = []
    sounds = obj.get('sounds')
    if 'sounds' in obj:
        for sound in sounds:
            if isinstance(sound, dict):
                sound.pop('ogg_url', '')
                sound.pop('mp3_url', '')
                sound.pop('audio', '')
                if sound and sound != {}:
                    new_sounds.append(sound)

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
    except:
        print('translations failed', new_translations)
        raise
    
    for k in new_keys:
        if k == 'translations':
            if new_translations:
                new_obj['translations'] = new_translations
        elif k == 'sounds':
            if new_sounds:
                new_obj['sounds'] = new_sounds
        elif k == 'categories':
            if new_categories:
                new_obj['categories'] = new_categories
        elif k == 'etymology_templates':
            if new_etymology_templates:
                new_obj['etymology_templates'] = new_etymology_templates
        elif k == 'senses':
            if new_senses:
                new_obj['senses'] = new_senses
        elif k == 'lang':
            new_obj['lang'] = lang
        else:
            val = obj[k]
            if isinstance(val, str):
                val = val.strip()
            new_obj[k] = val
    
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
          if not has_valid_chars(word):
            return False
    pos_index = line.rfind('], "pos": "')
    
    if pos_index > 0:
        end_i = line.find(',', pos_index+4)
        pos = line[pos_index+len('], "pos": "'):end_i]
        pos = pos.strip('"')
        if is_standard_banned_pos(pos):
            return False
    return True


def nl_keep_before_load(line: str) -> bool:
    
    if has_cjk_or_arabic_fast(line, 30):
        return False
    
    lc_loc = line.find(', "lang_code": "', 0, 70)

    if lc_loc > 0:
        start = lc_loc+len(', "lang_code": "')
        lc_end = line.find('"', start)
        lc = line[start:lc_end]
        
        lc = lc.strip()
        if not lookup_lang_from_code(lc) and lc != 'unknown':
            return False
        
    word_loc = line.find('"word": "')
    if word_loc == 1:
        end = line.find('"', word_loc + len('"word": "'))
        word = line[word_loc + len('"word": "'):end].strip()
        if not has_valid_chars(word):
            return False
    
    banned_pos = ['num', 'symbol', 'phrase', 'character', 'punct', 'abbrev', 'proverb', 'name', 'number']
    pos_loc = line.find(', "pos": "')
    if pos_loc == -1:
        return False
    cut_line = line[pos_loc + len(', "pos": "'):]
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
    mode = 'w+'
    def_mode = 'w+'
    with open(in_file, 'r', encoding='utf-8') as f:
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
                            save_batch_to_file(entries_batch, entries_out_file, mode)
                            if mode == 'w+':
                                mode = 'a'
                            entries_batch = []
                        if definitions_out_file:
                            word_entry = extract_words_senses(obj)
                            batch.append(word_entry)
                            if len(batch) > batch_size:
                                save_batch_to_file(batch, definitions_out_file, def_mode)
                                if def_mode == 'w+':
                                    def_mode = 'a'
                                    
                                batch = []
                except Exception as e:
                    error_lines.append((i, obj))
                    print(line)
                    print("Error on line: ", i, " Error: ", e)
                    break
        if entries_batch:
            save_batch_to_file(entries_batch, entries_out_file, mode)
            if mode == 'w+':
                mode = 'a'   
        if batch and definitions_out_file:
            save_batch_to_file(batch, definitions_out_file, def_mode)
            if def_mode == 'w+':
                def_mode = 'a'
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

def filter_sense_categories(obj: dict):
    if obj:
        senses = obj.get('senses')
        if senses:
            for i, sense in enumerate(senses):
                categories = filter_categories(sense.get('categories', []))
                if categories:
                    obj['senses'][i]['categories'] = categories
                else:
                    deleted_categories = obj['senses'][i].pop('categories', '')

def current_filter_obj(obj): 
    if obj:
        obj = sort_standardize_entry(obj)
    return obj

def overwrite_file_with_filter_operations(file, filter_ops=['standardize_entries'], batch_size=10000):
    batch = []
    if not isinstance(file, Path):
        file = Path(file)
    
    out_file = make_temp_file_path(file)

    total_lines = count_lines_with_progress(file)
    mode = 'w+'
    if 'add_wl_code' in filter_ops:
        wl_code = get_file_wl_code(file)
        
    with open(file, 'r', encoding='utf-8') as f:
        
        for i, line in tqdm(enumerate(f), total=total_lines):
            if line:
                try:
                    obj = json.loads(line)
                    if obj:
                        if 'current_filter' in filter_ops:
                            obj = current_filter_obj(obj)
                            if not obj:
                                continue
                        if 'pos' in filter_ops:
                            if has_banned_pos(obj):
                                continue
                        if 'standardize_entries' in filter_ops:
                            obj = sort_standardize_entry(obj)
                            if not obj:
                                continue
                        if 'filter_sense_categories' in filter_ops:
                            filter_sense_categories(obj)
                        if 'add_wl_code' in filter_ops:
                            if wl_code and obj:
                                obj['wl_code'] = wl_code
                        if obj:
                            batch.append(obj)
                        if len(batch) > batch_size:
                            save_batch_to_file(batch, file, mode)
                            if mode == 'w+':
                                mode='a'
                            batch = []
                    
                    if batch:
                        save_batch_to_file(batch, file, mode)
                        if mode == 'w+':
                            mode='a'
                except:
                    print(line)
        file_name = file.relative_to(PROJ_ROOT)
        out_file_name = out_file.relative_to(PROJ_ROOT)
        response = input(f'are you sure you want to overwrite {file_name} with {out_file_name}? y/n')
        if response == 'y':
            overwrite_file(file, out_file)
        else:
            print('aborted temp file saved as: ', out_file_name)
    return out_file


def saveletterlist(letter_list, save_folder, letter):
    letter_file = Path(save_folder, 'letter_files', f'{letter}.jsonl')
    with open(letter_file, 'a+', encoding='utf-8') as sf: 
        for obj in letter_list:
            json.dump(obj, sf, ensure_ascii=False)
            sf.write('\n')

def alpha_sort_large_file(file, save_folder, start_a=True, total_lines=None, batch_size=1000):
    error_lines = []
    if start_a:
        letter_lines_dict = {ch: [] for ch in "abcdefghijklmnopqrstuvwxyz"}
        letter_lines_dict["non_ascii"] = []
        letter_lines_dict["non_a_z"] = []

    else:
        letter_lines_dict["non_a_z"] = []
        for ch in string.ascii_lowercase():
           letter_lines_dict[ch] = []
        letter_lines_dict["non_ascii"] = []

    sorted_file = Path(save_folder, f'{file.stem}_sorted.jsonl')
    
    if not Path(save_folder, 'letter_files').exists():
        Path(save_folder, 'letter_files').mkdir(parents=True, exist_ok=True)
    
    if not total_lines:
        total_lines = count_lines_with_progress(file, quiet=True)
    with open(file, 'r', encoding='utf-8') as f:
        for i, line in tqdm(enumerate(f), total=total_lines, desc='Splitting and reading lines'):
            if line:
                try:
                    loaded = json.loads(line)
                    if loaded:
                        word = loaded.get('word')
                        if word:
                            word = word.strip()
                            if word:
                                letter = word[0].lower()
                            else:
                                continue
                            if letter.isnumeric():
                                continue
                            if not letter.isascii():
                                letter = 'non_ascii'
                            elif not letter.isalnum():
                                letter = 'non_a_z'
                            letter_lines_dict[letter].append(loaded)
                            
                            if len(letter_lines_dict[letter]) >= batch_size:
                                saveletterlist(letter_lines_dict[letter], save_folder, letter)
                                letter_lines_dict[letter] = []
                except Exception as e:
                    print('Error on line ', i, ': ', e)
                    print(line)
                    error_lines.append((i, line))
        for k, v in letter_lines_dict.items():
            if v:
                saveletterlist(v, save_folder, k)

    sorted_mode = 'w+'
    for key in tqdm(letter_lines_dict.keys(), total=28, desc='sorting letters and writing to out file'):
        print(f'Now processing: {key}')
        letter_file = Path(save_folder, 'letter_files', f'{key}.jsonl')
        if letter_file.exists():
            with open(letter_file, 'r', encoding='utf-8') as lf:
                lines = lf.readlines()
                loaded_lines = [json.loads(x) for x in lines if x]
                loaded_lines = sort_dict_list(loaded_lines)
                save_batch_to_file(loaded_lines, sorted_file, sorted_mode)
                if sorted_mode == 'w+':
                    sorted_mode = 'a'
            os.remove(letter_file.__str__())
    os.rmdir(Path(save_folder, 'letter_files').__str__())    
    return sorted_file

def add_entry_ids(file, overwrite=False):
    batch = []
    batch_size = 100000
    wl_code = get_file_wl_code(file)
    if wl_code.endswith('R'):
        wl_code = f'{wl_code[0:2]}F'
    out_file = make_temp_file_path(file)
    mode = 'w+'
    with open(file, 'r', encoding='utf-8') as f:
        
        for i, line in tqdm(enumerate(f)):
            if line:
                loaded = json.loads(line)
                if loaded:
                    if 'entry_id' not in loaded:
                        loaded['entry_id'] = f'{wl_code}_{i}'
                        sorted_keys = sort_entry_keys(loaded, start_keys=['entry_id', 'word', 'pos', 'lang_code', 'lang', 'senses'])
                        obj = {}
                        for k in sorted_keys:
                            obj[k] = loaded[k]
                    batch.append(obj)
                
            if len(batch) > batch_size:
                save_batch_to_file(batch, out_file, mode)
                if mode == 'w+':
                    mode='a'
                batch = []
            
        if batch:
            save_batch_to_file(batch, out_file, mode)
    if overwrite:
        overwrite_file(file, out_file)
    return batch, out_file

# Getters
def get_eid_word_pos(obj):
    id = obj.get('entry_id')
    word = obj.get('word')
    pos = obj.get('pos')
    return id, word, pos

def get_eid_word_pos_senses(obj):
    id = obj.get('entry_id')
    word = obj.get('word')
    pos = obj.get('pos')
    senses = obj.get('senses')
    return id, word, pos, senses


def get_forms(obj):
    if 'forms' in obj:
        return obj.get('forms')
    elif 'form_of' in obj:
        return obj.get('form_of')
    else:
        return None

def get_all_glosses(obj):
    if not obj:
        return None
    elif isinstance(obj, dict):
        senses = obj.get('senses')
        if not senses:
            return None
    elif isinstance(obj, list):
        senses = obj
    return [x.get('glosses') for x in senses if 'glosses' in x]
        
def make_eid_word_dict(obj: dict, extra_args=[]):
    word_dict = {'entry_id': obj.get('entry_id'), 'word':obj.get('word')}
    if extra_args:
        for earg in extra_args:
            if earg == 'forms':
                forms = get_forms(obj)
                if forms:
                    word_dict['forms'] = forms
            elif earg in obj:
                word_dict[earg] = obj.get(f'{earg}')
    return word_dict

if __name__ == '__main__':
    # {"word": "free", "pos": "verb", "lang_code": "en", "lang": "english", "senses": [{"glosses": ["To make free; set at liberty; release."], "categories": ["English terms with quotations", "English transitive verbs"], "links": [["liberty", "liberty"], ["release", "release"]], "raw_glosses": ["(transitive) To make free; set at liberty; release."], "tags": ["transitive"]}, {"glosses": ["To rid of something that confines or oppresses."], "categories": ["English terms with quotations", "English transitive verbs", "Quotation templates to be cleaned"], "info_templates": [{"args": {"1": "en", "2": ":from"}, "name": "+obj", "extra_data": {"words": ["from"]}, "expansion": "[with from]"}], "links": [["rid", "rid"]], "raw_glosses": ["(transitive) To rid of something that confines or oppresses. [with from]"], "tags": ["transitive"]}, {"glosses": ["To relinquish (previously allocated memory) to the system."], "categories": ["English terms with quotations", "English transitive verbs", "Quotation templates to be cleaned", "en:Programming"], "links": [["programming", "programming#Noun"], ["relinquish", "relinquish"], ["allocate", "allocate"], ["memory", "memory"], ["system", "system"]], "raw_glosses": ["(transitive, programming) To relinquish (previously allocated memory) to the system."], "tags": ["transitive"], "topics": ["computing", "engineering", "mathematics", "natural-sciences", "physical-sciences", "programming", "sciences"]}], "forms": [{"form": "frees", "tags": ["present", "singular", "third-person"]}, {"form": "freeing", "tags": ["participle", "present"]}, {"form": "freed", "tags": ["participle", "past"]}, {"form": "freed", "tags": ["past"]}], "derived": [{"word": "befree"}, {"word": "free up"}], "etymology_templates": [{"name": "inh", "args": {"1": "en", "2": "enm", "3": "freen"}, "expansion": "Middle English freen"}, {"name": "inh", "args": {"1": "en", "2": "ang", "3": "frēon"}, "expansion": "Old English frēon"}, {"name": "inh", "args": {"1": "en", "2": "gmw-pro", "3": "*frijōn"}, "expansion": "Proto-West Germanic *frijōn"}, {"name": "inh", "args": {"1": "en", "2": "gem-pro", "3": "*frijōną"}, "expansion": "Proto-Germanic *frijōną"}, {"name": "der", "args": {"1": "en", "2": "ine-pro", "3": "*preyH-"}, "expansion": "Proto-Indo-European *preyH-"}, {"name": "cog", "args": {"1": "nl", "2": "vrijen"}, "expansion": "Dutch vrijen"}], "etymology_text": "From Middle English freen, freoȝen, from Old English frēon, frēoġan (“to free; make free”), from Proto-West Germanic *frijōn, from Proto-Germanic *frijōną, from Proto-Indo-European *preyH-, and is cognate with German freien, Dutch vrijen, Czech přát, Serbo-Croatian prijati, Polish sprzyjać.", "etymology_number": 2, "synonyms": [{"word": "befree"}, {"word": "emancipate"}, {"word": "let loose"}, {"word": "liberate"}, {"word": "manumit"}, {"word": "release"}, {"word": "unchain"}, {"word": "unfetter"}, {"word": "unshackle"}], "categories": ["English countable nouns", "English entries with incorrect language header", "English lemmas", "English nouns", "English terms derived from Middle English", "English terms derived from Old English", "English terms derived from Proto-Germanic", "English terms derived from Proto-Indo-European", "English terms derived from Proto-West Germanic", "English terms inherited from Middle English", "English terms inherited from Old English", "English terms inherited from Proto-Germanic", "English terms inherited from Proto-West Germanic", "English terms with homophones", "English verbs", "Entries with translation boxes", "Pages with 3 entries", "Pages with entries", "Rhymes:English/iː", "Rhymes:English/iː/1 syllable", "Terms with Dutch translations", "Terms with Old English translations", "en:Money"], "head_templates": [{"name": "en-verb", "args": {}, "expansion": "free (third-person singular simple present frees, present participle freeing, simple past and past participle freed)"}], "sounds": [{"enpr": "frē"}, {"ipa": "/fɹiː/"}, {"ipa": "[fɹɪi̯]"}, {"rhymes": "-iː"}, {"homophone": "three (th-fronting)"}], "translations": [{"word": "frēoġan", "lang_code": "ang", "lang": "old_english", "code": "ang", "sense": "to make free, set at liberty"}, {"word": "bevrijden", "lang_code": "nl", "lang": "dutch", "code": "nl", "sense": "to make free, set at liberty"}, {"word": "loslaten", "lang_code": "nl", "lang": "dutch", "code": "nl", "sense": "to make free, set at liberty"}, {"word": "laten gaan", "lang_code": "nl", "lang": "dutch", "code": "nl", "sense": "to make free, set at liberty"}], "wl_code": "EER"}
    translations = [{"word": "frēoġan", "lang_code": "ang", "lang": "old_english", "code": "ang", "sense": "to make free, set at liberty"}, {"word": "bevrijden", "lang_code": "nl", "lang": "dutch", "code": "nl", "sense": "to make free, set at liberty"}, {"word": "loslaten", "lang_code": "nl", "lang": "dutch", "code": "nl", "sense": "to make free, set at liberty"}, {"word": "laten gaan", "lang_code": "nl", "lang": "dutch", "code": "nl", "sense": "to make free, set at liberty"}]
    print(sort_translations(translations))