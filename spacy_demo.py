import spacy
from spacy import displacy

text = """London is the capital and most populous city of England and 
    the United Kingdom.  Standing on the River Thames in the south east 
    of the island of Great Britain, London has been a major settlement 
    for two millennia. It was founded by the Romans, who named it Londinium.
    """

text = """spaCy excels at large-scale information extraction tasks. It's written from the ground up in carefully memory-managed Cython. Independent research has confirmed that spaCy is the fastest in the world. If your application needs to process entire web dumps, spaCy is the library you want to be using.
"""

if __name__ == "__main__":
    print("Welcome to demo of spacy")
    print("We've got a text: \n\'{0}\'\n".format(text))

    nlp = spacy.load('en_core_web_lg')
    doc = nlp(text)

    for entity in doc.ents:
        print(f"{entity.text} ({entity.label_})")

    displacy.serve(doc, style='dep')
