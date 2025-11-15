# The Structure of Kiakki Wiktionary Json Data and Common Morphological Meanings

## Wiktionary Jsonl 
├── word (str) 
├── pos (str)
├── lang (str) name lang word is in
├── lang_code (str) 2-3 letter code of the language the word belongs to. 
├── senses (list[dict]):
│   └── sense
|       ├── glosses 
|       ├── raw_glosses 
│       ├── alt_of
│       ├── tags
│       ├── categories (list[str])
│       ├── topics
|       ├── translations
|       ├── form_of (list[dict])
|       |    ├── word
|       |    └── extra
|       ├── senseid 
|       ├── antonyms (list[dict]): words that mean the opposite 
|       ├── holonyms (list[dict]): the word for the group/category of stuff this word belongs to: e.g. utensil is holonym for spoon, chopsticks, prongs (on a fork)
|       ├── hypernyms (list[dict]): More specific terms (vehicle → car, truck).
|       ├── meronyms (list[dict]): Parts of this item (car → wheel, engine). (meronym = “part of a whole”)
|       ├── synonyms (list[dict])
|       ├── related (list[dict])
|       ├── wikidata 
|       ├── wiktionary
|       ├── english
│       └── examples

├── abbrevations (list[dict])
├── categories (list[str])
├── coordinate_terms (list[dict]): Items with the same hypernym (cat, dog, horse → mammals). (coordinate terms = “sibling categories”)
├── descendants (list[dict]),
├── derived (list[dict]), 
├── etymology_number (int): for words with multiple numbered etymologies, this contains the number of the etymology under which this entry appeared
├── etymology_text (list[str])
├── etymology_templates (list[dict]): list of inflected or alternative forms specified for the word (e.g., plural, comparative, superlative, roman script version)
├── forms (list[dict])
    ├── form string
│   ├── tags list[string]
│   ├── ipa : string (optional)
│   ├── roman : string (optional)
│   └── source : string (optional)
├── head_templates (list[dict])
├── inflection templates (list[dict])
├── original_title list[str]
├── proverbs (NL Only)
├── sounds (list[dict])
│       ├── preproccessing
|       └── nl
├── topics (list[str])
├── translations 
|
├── antonyms (list[dict]): words that mean the opposite 
├── holonyms (list[dict]): the word for the group/category of stuff this word belongs to: e.g. utensil is holonym for spoon, chopsticks, prongs (on a fork)
├── hypernyms (list[dict]): More general terms (car → vehicle). (hypernym = “is-a broader category of”)
├── meronyms (list[dict]): Parts of this item (car → wheel, engine). (meronym = “part of a whole”)
├── synonyms (list[dict]) 
├── related (list[dict])
├── wikidata 
├── wiktionary





Word Entry (dictionary)
│   Represents a single extracted dictionary entry from Wiktionary.
│
├── word : string
│     The lemma (canonical written form).
│
├── pos : string
│     Part of speech (e.g., noun, verb, adjective).
│
├── lang : string
│     Full language name (e.g., "English").
│
├── lang_code : string
│     Language code (ISO-like, e.g., "en").
│
├── senses : list[Sense]
│     List of senses (meanings) for this word.
│
│   Sense (dictionary)
│   │
│   ├── glosses : list[string]
│   │     Short explanations of the meaning.
│   │
│   ├── raw_glosses : list[string]
│   │     Unprocessed glosses extracted directly.
│   │
│   ├── tags : list[string]
│   │     Labels like "archaic", "slang", "transitive".
│   │
│   ├── categories : list[string]
│   │     Wiktionary categories the sense belongs to.
│   │
│   ├── topics : list[string]
│   │     Topical categories (e.g., "Medicine", "Astronomy").
│   │
│   ├── alt_of : list[dict]
│   │     Alternative form of another word.
│   │
│   ├── form_of : list[dict]
│   │     Inflected form of another lemma.
│   │
│   ├── translations : list[Translation]
│   │     Translations grouped by sense.
│   │
│   ├── synonyms : list[string]
│   │     Words with the same or very similar meaning.
│   │
│   ├── antonyms : list[string]
│   │     Words with opposite meaning.
│   │
│   ├── hypernyms : list[string]
│   │     More general terms (car → vehicle).
│   │     (hypernym = “is-a broader category of”)
│   │
│   ├── hyponyms : list[string]   (sometimes present)
│   │     More specific terms (vehicle → car, truck).
│   │
│   ├── holonyms : list[string]
│   │     Whole items of which this is a part (wheel → car).
│   │     (holonym = “whole that contains this part”)
│   │
│   ├── meronyms : list[string]
│   │     Parts of this item (car → wheel, engine).
│   │     (meronym = “part of a whole”)
│   │
│   ├── coordinate_terms : list[string]
│   │     Items with the same hypernym (cat, dog, horse → mammals).
│   │     (coordinate terms = “sibling categories”)
│   │
│   ├── derived : list[string]
│   │     Words derived from this form.
│   │
│   ├── related : list[string]
│   │     Words with related concepts or origins.
│   │
│   ├── senseid : string
│   │     Unique identifier linking senses across entries.
│   │
│   ├── wikidata : string | null
│   │     Q-ID of the corresponding Wikidata entity.
│   │
│   ├── wikipedia : string | null
│   │     Title of linked Wikipedia article.
│   │
│   └── examples : list[string]
│         Usage examples.
│
├── forms : list[Form]
│     Inflected forms or alternative spellings.
│
│   Form (dictionary)
│   ├── form : string
│   ├── tags : list[string]
│   ├── ipa : string (optional)
│   ├── roman : string (optional)
│   └── source : string (optional)
│
├── sounds : list[Sound]
│     Pronunciation and phonological data.
│
│   Sound (dictionary)
│   ├── ipa : string
│   │     IPA transcription.
│   ├── enpr : string
│   │     English pronunciation respelling.
│   ├── audio : string (filename)
│   ├── ogg_url : string
│   ├── mp3_url : string
│   ├── audio-ipa : string (optional)
│   ├── homophones : list[string]
│   │     Words pronounced the same (e.g., “sea”/“see”).
│   ├── hyphenation : list[string]
│   │     Syllable splits.
│   └── tags : list[string]
│
├── categories : list[string]
│     Word-level categories.
│
├── topics : list[string]
│     Non-grammatical thematic categories.
│
├── translations : list[Translation]
│     Translations not tied to a specific sense.
│
│   Translation (dictionary)
│   ├── alt : string (alternative spelling)
│   ├── code : string (language code)
│   ├── english : string (gloss)
│   ├── lang : string (language name)
│   ├── note : string | null
│   ├── roman : string | null
│   ├── sense : string | int
│   ├── tags : list[string]
│   └── taxonomic : bool
│         True if the translation describes biological taxonomy.
│         (taxonomic = “pertaining to biological classification”)
│
├── etymology_text : string
│     Human-readable textual etymology.
│
├── etymology_templates : list[Template]
│     Template-expanded structured etymology.
│
├── etymology_number : int | null
│     For entries with multiple etymologies.
│
├── descendants : list[Descendant]
│     Words in other languages derived from this one.
│
│   Descendant (dictionary)
│   ├── depth : int
│   ├── templates : list[Template]
│   └── text : string
│
├── synonyms / antonyms / hypernyms / holonyms / meronyms /
│   derived / related / coordinate_terms
│   (same meaning & data types as the sense-level versions)
│
├── wikidata : string | null
├── wikipedia : string | null
│
├── head_templates : list[Template]
└── inflection_templates : list[Template]

    Template (dictionary)
    │   name : string
    │   args : dict[string, string]
    └── expansion : string



## ENR
### Level 0 Keys/Value Types (and subkey values if list)
level_0_keys = {
'senses': [list][dict],
 'pos': [str],
 'head_templates': [list][dict],
 'forms': [list][dict],
 'derived': [list][dict],
 'descendants': [list][dict],
 'sounds': [list][dict],
 'hyphenations': [list][dict],
 'etymology_text': [str],
 'etymology_templates': [list][dict],
 'word': [str],
 'lang': [str],
 'lang_code': [str],
 'inflection_templates': [list][dict],
 'categories': [list][str],
 'related': [list][dict],
 'etymology_number': [int],
 'synonyms': [list][dict],
 'antonyms': [list][dict],
 'wikipedia': [list][str],
 'hypernyms': [list][dict],
 'hyponyms': [list][dict],
 'holonyms': [list][dict],
 'coordinate_terms': [list][dict],
 'meronyms': [list][dict],
 'abbreviations': [list][dict],
 'original_title': [str]}

 ## Level 1 Keys
 senses = [{'links': [str],
 'synonyms': [
    {'word': str,
    'tags': list['str],
    'extra': str,
    'source': str,
    'alt': str,
    'english': str,
    'translation': str,
    'topics': list['str]}],
 'glosses': [str],
 'tags': [str],
 'categories': [str],
 'wikipedia': [str],
 'form_of': [{'word': str, 
             'extra': str}],
 'raw_glosses': [str],
 'raw_tags': [str],
 'examples': [{'text': str,
   'bold_text_offsets': list,
   'translation': str,
   'english': str,
   'bold_translation_offsets': list,
   'type': str,
   'tags': list['str],
   'ref': str,
   'literal_meaning': str,
   'bold_literal_offsets': list,
   'roman': str,
   'raw_tags': list}],
 'alt_of': [{'word': str, 
             'extra': str}],
 'topics': [str],
 'attestations': [{'date': str, 'references': list}],
 'antonyms': [{'word': str}],
 'wikidata': [str],
 'qualifier': str,
 'senseid': [str],
 'head_nr': int,
 'hypernyms': [{'word': str}],
 'coordinate_terms': [{'word': str, 'english': str, 'translation': str}],
 'meronyms': [{'word': str}],
 'info_templates': [{'args': dict,
   'name': str,
   'extra_data': dict,
   'expansion': str}],
 'holonyms': [{'word': str}],
 'related': [{'word': str, 'tags': list}],
 'hyponyms': [{'word': str}]}

forms =  {'form': str, 'tags': list[str], 'source': str, 'raw_tags': list[str], 'head_nr': int} 
 
derived = {'word': str,
 'lang': str,
 'lang_code': str,
 'tags': list[str],
 'ipa': str,
 'audio': str,
 'ogg_url': str,
 'mp3_url': str,
 'parts': list[str],
 'name': str,
 'args': dict,
 'expansion': str,
 'raw_tags': list[str],
 'roman': str,
 'rhymes': str,
 'homophone': str,
 'sense': str,
 'descendants': list[str],
 'english': str,
 'translation': str,
 'note': str,
 'text': str,
 'other': str,
 'topics':  list[str],
 'alt': str,
 'taxonomic': str,
 'ruby': list[str]}
descendants = {'word': str,
 'lang': str,
 'lang_code': str,
 'tags': list[str],
 'ipa': str,
 'audio': str,
 'ogg_url': str,
 'mp3_url': str,
 'parts': list[str],
 'name': str,
 'args': dict,
 'expansion': str,
 'raw_tags': list[str],
 'roman': str,
 'rhymes': str,
 'homophone': str,
 'sense': str,
 'descendants': list[str],
 'english': str,
 'translation': str,
 'note': str,
 'text': str,
 'other': str,
 'topics':  list[str],
 'alt': str,
 'taxonomic': str,
 'ruby': list[str]}

sounds = {'ipa': str,
 'audio': str,
 'ogg_url': str,
 'mp3_url': str,
 'rhymes': str,
 'homophone': str,
 'tags': list[str],
 'note': str,
 'text': str,
 'other': str}
hyphenations = {'parts': list[str]}
etymology_templates = {'name': str, 'args': dict, 'expansion': str}
inflection_templates = {'name': str, 'args': dict}

related = {'tags': list['str],
 'word': str,
 'sense': str,
 'english': str,
 'translation': str,
 'roman': str,
 'topics': list['str], 
 'alt': str,
 'raw_tags': list['str]}
coordinate_terms= {'word': str,
 'tags': list['str],
 'sense': str,
 'topics': list,
 'english': str,
 'translation': str,
 'alt': str}
abbreviations= {'word': str}
synonyms= {'word': str,
 'sense': str,
 'tags': list['str],
 'raw_tags': list['str],
 'topics': list['str],
 'source': str,
 'alt': str,
 'english': str,
 'translation': str,
 'taxonomic': str,
 'roman': str}
antonyms= {'word': str,
 'sense': str,
 'english': str,
 'translation': str,
 'tags': list['str],
 'topics': list['str],
 'alt': str}

hypernyms= {'word': str,
 'sense': str,
 'topics': list['str],
 'alt': str,
 'tags':list['str],
 'english': str,
 'translation': str}
hyponyms= {'word': str,
 'sense': str,
 'english': str,
 'translation': str,
 'topics': list['str],
 'taxonomic': str,
 'alt': str}
holonyms= {'word': str, 'tags': list['str],}

meronyms= {'word': str, 'alt': str}

# Basic Morphology Terms
