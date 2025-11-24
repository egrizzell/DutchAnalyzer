# Wiktextract Data Structure Documentation

This document contains two parts:
1. **Human‑readable Markdown description** of the full visual tree (Option B format) including datatypes and tag descriptions.
2. **Complete JSON Schema** (as a code block) representing the same structure.

---

## 1. Visual Tree of Wiktextract Entry Structure

```
entry (object)
├── word: string — the lemma being defined
├── lang: string — full language name
├── lang_code: string — language code (ISO)
├── pos: string — part of speech
├── etymology_text: string — plain etymology text
├── original_title: string — original page title
├── etymology_number: integer — nth etymology section
├── categories: string[] — semantic or topical categorization
├── wikipedia: string[] — associated Wikipedia titles
├── head_templates: template[]
│   └── { name: string, args: object, expansion: string }
├── etymology_templates: template[]
│   └── { name: string, args: object, expansion: string }
├── inflection_templates: template[]
│   └── { name: string, args: object }
├── hyphenations: hyphenation[]
│   └── { parts: string[] }
├── sounds: sound[]
│   └── {
│        ipa: string,
│        audio: string,
│        ogg_url: string,
│        mp3_url: string,
│        rhymes: string,
│        homophone: string,
│        tags: string[],
│        note: string,
│        text: string,
│        other: string
│      }
├── forms: form[]
│   └── {
│        form: string,
│        tags: string[],
│        source: string,
│        raw_tags: string[],
│        head_nr: integer
│      }
├── senses: sense[]
│   └── sense (object)
│        ├── glosses: string[] — human‑readable definitions
│        ├── raw_glosses: string[] — unprocessed definitions
│        ├── tags: string[] — grammatical or semantic flags
│        ├── raw_tags: string[]
│        ├── categories: string[]
│        ├── topics: string[] — subject areas
│        ├── wikipedia: string[]
│        ├── senseid: string[] — unique sense identifiers
│        ├── head_nr: integer — headword index
│        ├── qualifier: string — qualifier text
│        ├── links: string[]
│        ├── wikidata: string[]
│        ├── form_of: { word: string, extra: string }[]
│        ├── alt_of:  { word: string, extra: string }[]
│        ├── antonyms: { word: string }[]
│        ├── hypernyms:  { word: string }[]
│        ├── hyponyms:   { word: string }[]
│        ├── holonyms:   { word: string }[]
│        ├── meronyms:   { word: string }[]
│        ├── coordinate_terms: {
│        │        word: string,
│        │        english: string,
│        │        translation: string
│        │      }[]
│        ├── related: { word: string, tags: string[] }[]
│        ├── examples: example[]
│        │      └── {
│        │           text: string,
│        │           translation: string,
│        │           english: string,
│        │           type: string,
│        │           tags: string[],
│        │           ref: string,
│        │           literal_meaning: string,
│        │           roman: string,
│        │           bold_text_offsets: number[],
│        │           bold_translation_offsets: number[],
│        │           bold_literal_offsets: number[],
│        │           raw_tags: string[]
│        │         }
│        ├── attestations: { date: string, references: array }[]
│        ├── info_templates: {
│        │        name: string,
│        │        args: object,
│        │        extra_data: object,
│        │        expansion: string
│        │      }[]
├── derived: relation_entry[]
├── descendants: relation_entry[]
├── related: relation_entry[]
├── synonyms: synonym_entry[]
├── antonyms: antonym_entry[]
├── hypernyms: relation_entry[]
├── hyponyms: relation_entry[]
├── holonyms: relation_entry[]
├── meronyms: relation_entry[]
├── abbreviations: { word: string }[]
├── coordinate_terms: coordinate_entry[]
└── (relation_entry definitions)

relation_entry {
  word: string,
  lang: string,
  lang_code: string,
  tags: string[],
  ipa: string,
  audio: string,
  ogg_url: string,
  mp3_url: string,
  parts: string[],
  name: string,
  args: object,
  expansion: string,
  raw_tags: string[],
  roman: string,
  rhymes: string,
  homophone: string,
  sense: string,
  descendants: string[],
  english: string,
  translation: string,
  note: string,
  text: string,
  other: string,
  topics: string[],
  alt: string,
  taxonomic: string,
  ruby: string[]
}
```

---

## 2. JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Wiktextract Entry",
  "type": "object",
  "properties": {
    "word": { "type": "string" },
    "lang": { "type": "string" },
    "lang_code": { "type": "string" },
    "pos": { "type": "string" },
    "etymology_text": { "type": "string" },
    "original_title": { "type": "string" },
    "etymology_number": { "type": "integer" },
    "categories": { "type": "array", "items": { "type": "string" } },
    "wikipedia": { "type": "array", "items": { "type": "string" } },

    "head_templates": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "args": { "type": "object" },
          "expansion": { "type": "string" }
        }
      }
    },

    "etymology_templates": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "args": { "type": "object" },
          "expansion": { "type": "string" }
        }
      }
    },

    "inflection_templates": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "args": { "type": "object" }
        }
      }
    },

    "hyphenations": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "parts": {
            "type": "array",
            "items": { "type": "string" }
          }
        }
      }
    },

    "sounds": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "ipa": { "type": "string" },
          "audio": { "type": "string" },
          "ogg_url": { "type": "string" },
          "mp3_url": { "type": "string" },
          "rhymes": { "type": "string" },
          "homophone": { "type": "string" },
          "tags": { "type": "array", "items": { "type": "string" } },
          "note": { "type": "string" },
          "text": { "type": "string" },
          "other": { "type": "string" }
        }
      }
    },

    "forms": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "form": { "type": "string" },
          "tags": { "type": "array", "items": { "type": "string" } },
          "source": { "type": "string" },
          "raw_tags": { "type": "array", "items": { "type": "string" } },
          "head_nr": { "type": "integer" }
        }
      }
    },

    "senses": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "glosses": { "type": "array", "items": { "type": "string" } },
          "raw_glosses": { "type": "array", "items": { "type": "string" } },
          "tags": { "type": "array", "items": { "type": "string" } },
          "raw_tags": { "type": "array", "items": { "type": "string" } },
          "categories": { "type": "array", "items": { "type": "string" } },
          "topics": { "type": "array", "items": { "type": "string" } },
          "wikipedia": { "type": "array", "items": { "type": "string" } },
          "senseid": { "type": "array", "items": { "type": "string" } },
          "head_nr": { "type": "integer" },
          "qualifier": { "type": "string" },
          "links": { "type": "array", "items": { "type": "string" } },
          "wikidata": { "type": "array", "items": { "type": "string" } },

          "form_of": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "word": { "type": "string" },
                "extra": { "type": "string" }
              }
            }
          },

          "alt_of": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "word": { "type": "string" },
                "extra": { "type": "string" }
              }
            }
          },

          "examples": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "text": { "type": "string" },
                "translation": { "type": "string" },
                "english": { "type": "string" },
                "type": { "type": "string" },
                "tags": { "type": "array", "items": { "type": "string" } },
                "ref": { "type": "string" },
                "literal_meaning": { "type": "string" },
                "roman": { "type": "string" },
                "bold_text_offsets": {
                  "type": "array",
                  "items": { "type": "number" }
                },
                "bold_translation_offsets": {
                  "type": "array",
                  "items": { "type": "number" }
                },
                "bold_literal_offsets": {
                  "type": "array",
                  "items": { "type": "number" }
                },
                "raw_tags": {
                  "type": "array",
                  "items": { "type": "string" }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

---

