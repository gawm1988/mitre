# https://spacy.io/usage/linguistic-features#pos-tagging
import spacy

nlp = spacy.load("en_core_web_sm")

text = "Abuse Elevation Control Mechanism: Adversaries may circumvent mechanisms designed to control elevate privileges to gain higher-level permissions. Most modern systems contain native elevation control mechanisms that are intended to limit privileges that a user can perform on a machine. Authorization has to be granted to specific users in order to perform tasks that can be considered of higher risk.(Citation: TechNet How UAC Works)(Citation: sudo man page 2018) An adversary can perform several methods to take advantage of built-in control mechanisms in order to escalate privileges on a system.(Citation: OSX Keydnap malware)(Citation: Fortinet Fareit)"

doc =  nlp(text)

#for token in doc:
 #   print(token, token.pos_, token.lemma_)

verbs = []
for token in doc:
    if token.pos_ == "VERB":
        verbs.append(token.lemma_)

nouns = []

print(verbs)