# -*- coding: utf-8 -*-
"""
Christopher Smith
King's College London 2017
"""

import spacy

# A helper method - read in a file at the specified filesystem location and return it as a text block for tokenization.
# Makes the text unicode because Spacy needs it to be unicode.
def ingest_text(file_url):
    f = open(file_url, 'r')
    text = f.read()
    return unicode(text, 'utf8')

male_char_names = []
female_char_names = []
# Read in the text and tokenize it into sentences
doc_root = 'corpus' # Change this to whatever folder holds your texts
text = ingest_text('corpus/unicode/Far from the Madding Crowd.txt')
en_nlp = spacy.load('en')
doc = en_nlp(ingest_text('corpus/unicode/Far from the Madding Crowd.txt'))
outfile = open('output/Far from the Madding Crowd  - Dependencies.txt', 'w')
# Parse the text
# For each sentence, tokenize the words and determine their dependencies (part of speech)
for sentence in doc.sents:
    print >> outfile, sentence
    for word in sentence:
        if word.dep_ != 'punct' and not word.is_space:
            print >> outfile, word, " : ", word.dep_
    print >> outfile, '---'
outfile.close()
