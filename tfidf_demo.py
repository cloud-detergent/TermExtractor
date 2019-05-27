from sklearn.feature_extraction.text import TfidfVectorizer
from main import open_tag_data, get_documents, open_raw_terms
import os
from ITermExtractor.Structures.WordStructures import TaggedWord, Separator

if __name__ == "__main__":
    print("123")
    tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0, stop_words=None)

    # tf

    document_types = ['Указания', 'Инструкция', 'Инструктивные', 'Выводы', 'Приказ']

    tagged_sentence_list = open_tag_data(os.path.join('result', 'tags'))
    tagged_documents = get_documents(tagged_sentence_list, document_types)
    reconstructed = [
        '.'.join([
        ' '.join([
            word.word if type(word) is TaggedWord else word.symbol for word in sentence
        ])
        for sentence in doc
        ])
        for doc in tagged_documents]
    print(len(tagged_documents))
