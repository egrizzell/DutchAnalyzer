import re
import dutchanalyzer.utilities.json_utils as json_utils

def has_valid_chars(text, num_to_check=2) -> bool:
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

def is_lang(translation, lang_codes=['en', 'nl']) -> bool:
    lang_code = translation.get('lang_code', '')
    if lang_code in lang_codes:
        return True
    return False

def is_en_nl(translation: dict) -> bool:
    return is_lang(translation, lang_codes=['en', 'nl'])

def is_sense_only(obj: dict) -> bool:
    if obj.get('word'):
        return False
    if obj.get('sense'):
        return True
    return False

def has_word(obj: dict) -> bool:
    if obj.get('word'):
        return True
    return False

def is_standard_banned_pos(pos: str):
    banned_pos=['name','num', 'symbol', 'phrase', 'character', 'punct', 'abbrev', 'proverb', '', None]
    return pos in banned_pos

def has_banned_pos(obj: dict, banned_pos=[]):
    if banned_pos:
        return obj.get('pos') in banned_pos
    return is_standard_banned_pos(obj.get('pos'))
    

def filter_langs(obj: list, langs_to_keep=['en', 'nl']) -> list:
    if langs_to_keep == ['en', 'nl']:
        return filter(is_en_nl, obj)
    return [x for x in obj if x.get('lang_code', '') in langs_to_keep]

def any_in(obj, terms: list):
    if not obj:
        return False
    elif isinstance(obj, str):
        if any(el in obj for el in terms):
            return True
    elif isinstance(obj, list):
        if isinstance(obj[0], str):
            for o in obj:
                if any(o in terms for o in obj):
                    return True
        elif isinstance(obj[0], list):
            for o in obj:
                if any_in(o, terms):
                    return True  
        else:
            print('not implemented')
    return False
                



def split_langs(obj: list) -> dict:
    split_langs = {}
    for i in obj:
        lang_code = i.get('lang_code') 
        if not lang_code in split_langs:
            split_langs[lang_code] = [i]
        else:
            split_langs[lang_code].append(i)
    return split_langs

def split_list(obj: list, split_by = ['has_word', 'sense_only']):
    split_by.append('unmet')
    list_of_lists = [[]]*len(split_by)
    split_conditions = dict(zip(split_by, list_of_lists))
    
    if split_by == ['has_word', 'sense_only', 'unmet']:
        
        for i in list:
            if has_word(i):
                split_conditions['has_word'].append(i)
            elif is_sense_only(i):
                split_conditions['sense_only'].append(i)
            else:
                split_conditions['unmet'].append(i)
        
    else:
        print('not implemented')
    return split_conditions

def is_inflection(obj: dict):
    inflection_keywords = ['form of', 'inflection of', 'alt of', 'plural of', 'alternative of', 'abbrivation of', 'initialism of', 'diminutive of', 'declension of', 'participle of']
    inflection_categories = ["Dutch adjective case forms" ,"Dutch non-lemma forms", "Dutch obsolete forms", "Dutch past participles"]
    inflection_sense_tags = ["alt-of", 'form-of', "alternative", 'plural', 'subjunctive', 'second-person', 'indicative', 'first-person', 'third-person', 'singular', 'present', 'participle']
    categories = obj.get('categories')
    if any_in(categories, inflection_categories):
        return True
    senses = obj.get('senses')
    forms = json_utils.get_forms(obj)
    
    if senses:
        for sense in senses:
            glosses = sense.get('glosses')
            if any_in(glosses, inflection_keywords):
                return True
            tags = sense.get('tags')
            if any_in(tags, inflection_sense_tags):
                return True
            

            


if __name__ == '__main__':
    print(is_standard_banned_pos('num'))
    print(is_standard_banned_pos('noun'))



    




