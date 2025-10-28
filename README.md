# Dutch Analyzer 2.0
DutchAnalyzers goal is to create a set of replacement rules and make easily available the most common rules to turn every word in the Dutch language into English and vice versa. (e.g replacing a zo at the beginning of a dutch word with su to make an English one zommer -> summer, zon -> sun) It is meant to be of intellectual interest and help to language learners and morphological enthusiasts. 

DutchAnalyzer 2.0 is meant to be the public version of DutchAnalyzer using exclusively free to use, open source datasets. It is licensed under Creative Commons Attribution–NonCommercial–ShareAlike 4.0 International (CC BY-NC-SA 4.0). 

## Project Structure 
├── README.md
├── LICENSE.md
├── pyproject.toml 
├── requirements.txt
├── data
│   └── external 
|       ├── opentaal
|       ├── leipzig   
│   └── interim
│       ├── preproccessing
│       ├── exploration
│       ├── cleaning
│       └── analysis
│   ├── processed 
│   └── raw         
|       └── kaikki
|            ├── en
|            └── nl
├── models 
├── notebooks 
│       ├── preproccessing

├── references
|
├── reports
|
└── dutchanalyzer
    │
    ├── __init__.py             
    │
    ├── config.py               
    │
    ├── dataset.py              
    │
    ├── features.py 
    │                
    └── utilities.py


## Licensing

© 2025 Elise Grizzell.
This repository is licensed under the Creative Commons Attribution–NonCommercial–ShareAlike 4.0 International License (CC BY-NC-SA 4.0).

Code and dirived data: Licensed under CC BY-NC-SA 4.0 (see LICENSE).

## Data Sources

The following sources are what currently are expected to be used over the course of this project: 
- Kaikki.org English and Dutch data (from Wiktionary) — CC BY-SA 4.0, Specifically (25-10-2025 versions of the following datasets): https://kaikki.org/dictionary/Dutch/, https://kaikki.org/dictionary/English/, https://kaikki.org/dictionary/rawdata.html


- English & Dutch Wiktionary — CC BY-SA 4.0, Both en.wiktionary.org and nl.wiktionary.org


- OpenTaal — CC BY-SA 3.0 https://www.opentaal.org/


- Leipzig Corpora Collection — used for analysis only under their non-commercial research license; no corpus text redistributed. https://wortschatz.uni-leipzig.de/en/download/Dutch

You may freely use and adapt this project for non-commercial research and educational purposes, provided you give attribution and share any derivatives under the same license.

## Contributing
If you are interested in contributing please send me a message on github 