# Replacement Rules
def replace_suffix_tie(word):
    if len(word) < 3 or not word.endswith('tie'):
        return word
    return word[0:-3] + 'tion'
    
def replace_z_begin(word):
    if word.startswith('z'):
        return 's' + word[1:]
    return word
    
def remove_end_n(word):
    if word.endswith('n'):
        return word[0:-1]
    return word
    
def remove_end_en(word):
    if len(word) > 2 and word.endswith('en'):
        return word[0:-2]
    return word

def replace_oe_to_oo(word):
    index = word.find('oe')
    if index != -1:
        word.replace('oe', 'oo')
        return word
    else:
        return word

def English_to_Dutch_Replacements(word):
    pass

def Dutch_to_English_Replacements(word):
    #apply_test(recorder_df, EEF_df, 3, 'replace oe with oo', 'oe', 'oo', replace_function='middle', na_val='word')
    pass

replacements = [
    {'description': 'replace oe with oo', 'original_letters': 'oe', 'replace_with': 'oo', 'replace_function': 'middle', 'na_val': 'word'
     }
]