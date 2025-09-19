import requests

class Synonym:
    def __init__(self, data):
        self.word = data[0]['word']
        self.definitions = data[0]['meanings'][1]['definitions']

    def get_synonyms(self):
        synonyms = []
        for i in self.definitions:
            synonyms.append(f"definition: \'{i['definition']}\', synonyms: {i['synonyms']}")
        return synonyms

    def __str__(self):
        return f"word: {self.word}\n{self.get_synonyms()}"

base_url = "https://api.dictionaryapi.dev/api/v2/entries/en/"

def get_synonyms(word:str):
    word = word.lower()
    response = requests.get(base_url + word)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"No data retrieved for {word} - {response.status_code}")
        return None

verb = "exploit"
verb_info = get_synonyms(verb)
if verb_info:
    synonym = Synonym(verb_info)
    print(synonym)