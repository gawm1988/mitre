import pandas as pd
import requests

class Synonym:
    def __init__(self, data):
        self.word = data[0]['word']
        self.meanings = data[0]['meanings']

    def get_synonyms(self):
        definitions = []
        synonyms = []
        for meaning in self.meanings:
            partOfSpeech = meaning["partOfSpeech"]
            if partOfSpeech != "verb":
                continue
            for definition in meaning["definitions"]:
                definitions.append(definition['definition'])
                synonyms.append(definition['synonyms'])
        return definitions, synonyms

    def __str__(self):
        definitions, synonyms = self.get_synonyms()
        return f"word: {self.word}\ndefinitions: {definitions}\nsynonyms: {synonyms}"

base_url = "https://api.dictionaryapi.dev/api/v2/entries/en/"

def get_synonyms(word:str):
    word = word.lower()
    response = requests.get(base_url + word)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"No data retrieved for {word} - {response.status_code}")
        return None

verbs = ['circumvent', 'design', 'control', 'gain', 'contain', 'intend', 'limit', 'perform', 'have', 'grant', 'perform', 'consider', 'page', 'perform', 'take', 'build', 'escalate']

for verb in verbs:
    verb_info = get_synonyms(verb)
    if verb_info:
        synonym = Synonym(verb_info)
        definitions, synonyms = synonym.get_synonyms()
        print(f"verb: {verb}\ndefintions: {definitions}\nsynonyms: {synonyms}\n")