"""
Christopher Smith
King's College London 2017
"""

from nltk import sent_tokenize, word_tokenize, pos_tag
import os


# A helper method - read in a file at the specified filesystem location and return it as a text block for tokenization.
def ingest_text(file_url):
    f = open(file_url, 'r')
    text = f.read()
    return text

# Read in the text and tokenize it into sentences.
madding_crowd_text = ingest_text('corpus/Far from the Madding Crowd.txt')
sentences = sent_tokenize(madding_crowd_text)

male_char_names = []
fem_char_names = []

# Begin to parse the text - break it into words.
for sentence in sentences:
    tokens = word_tokenize(sentence)
    # If the sentence contains our target search item (Bathsheba), mark it.
    # Try for pronouns?
    if 'Bathsheba' in tokens:
        tagged_tokens = pos_tag(tokens)
        print tagged_tokens
        print '---'
