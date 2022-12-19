from pyrogram import Client, filters
import configparser
import os
import re
import numpy as np
import pickle

import nltk
from nltk.tokenize import word_tokenize

from sklearn.feature_extraction.text import TfidfVectorizer
from tensorflow.keras.models import load_model


conf = configparser.ConfigParser()
conf.read('conf.ini')
app = Client(**conf['TELEGRAM'])

model = load_model('models/my_model.h5')
my_vectorizer = pickle.load(open('models/vectorizer_features.pickle', 'rb'))

class UkrainianStemmer():
    def __init__(self, word):
        self.word = word
        self.vowel = r'аеиоуюяіїє'
        self.perfectiveground = r'(ив|ивши|ившись|ыв|ывши|ывшись((?<=[ая])(в|вши|вшись)))$'
        self.reflexive = r'(с[яьи])$'
        self.adjective = r'(ими|ій|ий|а|е|ова|ове|ів|є|їй|єє|еє|я|ім|ем|им|ім|их|іх|ою|йми|іми|у|ю|ого|ому|ої)$'
        self.participle = r'(ий|ого|ому|им|ім|а|ій|у|ою|ій|і|их|йми|их)$'
        self.verb = r'(сь|ся|ив|ать|ять|у|ю|ав|али|учи|ячи|вши|ши|е|ме|ати|яти|є)$'
        self.noun = r'(а|ев|ов|е|ями|ами|еи|и|ей|ой|ий|й|иям|ям|ием|ем|ам|ом|о|у|ах|иях|ях|ы|ь|ию|ью|ю|ия|ья|я|і|ові|ї|ею|єю|ою|є|еві|ем|єм|ів|їв|ю)$'
        self.rvre = r'[аеиоуюяіїє]'
        self.derivational = r'[^аеиоуюяіїє][аеиоуюяіїє]+[^аеиоуюяіїє]+[аеиоуюяіїє].*(?<=о)сть?$'
        self.RV = ''

    def ukstemmer_search_preprocess(self, word):
        word = word.lower()
        word = word.replace("'", "")
        word = word.replace("ё", "е")
        word = word.replace("ъ", "ї")
        return word

    def s(self, st, reg, to):
        orig = st
        self.RV = re.sub(reg, to, st)
        return (orig != self.RV)

    def stem_word(self):
        word = self.ukstemmer_search_preprocess(self.word)
        if not re.search('[аеиоуюяіїє]', word):
            stem = word
        else:
            p = re.search(self.rvre, word)
            start = word[0:p.span()[1]]
            self.RV = word[p.span()[1]:]

            # Step 1
            if not self.s(self.RV, self.perfectiveground, ''):

                self.s(self.RV, self.reflexive, '')
                if self.s(self.RV, self.adjective, ''):
                    self.s(self.RV, self.participle, '')
                else:
                    if not self.s(self.RV, self.verb, ''):
                        self.s(self.RV, self.noun, '')
            # Step 2
            self.s(self.RV, 'и$', '')

            # Step 3
            if re.search(self.derivational, self.RV):
                self.s(self.RV, 'ость$', '')

            # Step 4
            if self.s(self.RV, 'ь$', ''):
                self.s(self.RV, 'ейше?$', '')
                self.s(self.RV, 'нн$', u'н')

            stem = start + self.RV
        return stem

def stemming(parsed_text):
  stem_parsed_text = []
  for word in parsed_text:
    ukrainian_stemmer = UkrainianStemmer(word)
    stem_parsed_text.append(ukrainian_stemmer.stem_word())

  return stem_parsed_text

@app.on_message(filters.text)
async def main(client, msg):
    text = word_tokenize(msg.text)
    text = stemming(text)
    text = my_vectorizer.transform([' '.join(text)]).toarray()
    pred = model.predict(text[:, np.newaxis, :])
    temp_f = lambda x: f'нормальне повідомлення {np.round(1 - sum(x), 2)*100}%'\
        if sum(x) < 0.6 else f'пропаганда {np.round(sum(x), 2)*100}%'

    reply_text = temp_f(pred[0])
    await msg.reply(reply_text)





if __name__ == '__main__':
    app.run()