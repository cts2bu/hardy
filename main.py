# -*- coding: utf-8 -*-
"""
Christopher Smith
King's College London 2017
"""
import spacy
import os


# A helper method - read in a file at the specified filesystem location and return it as a text block for tokenization
# I also have a sanity check at the end to encode the text in unicode - spaCy is picky that way
def ingest_text(file_url):
    f = open(file_url, 'r')
    text = f.read()
    return unicode(text, 'utf8')

# TODO - make a targeted list of names in the novels; currently the script only does very rudimentary pronoun search
male_char_names = []
female_char_names = []

# First, set the document roots for input texts and the output text files.
doc_root = 'corpus/unicode'  # Change this to whatever folder holds your texts
out_dir = 'output'  # Change this to whatever folder will hold your outputted files

print "Loading spaCy dictionary (this will take a while)..."
en_nlp = spacy.load('en')  # Load the spaCy dictionary
print "Dictionary loaded."

# OK, now iterate through your document folder and pull the source files one by one
for item in os.listdir(doc_root):
    # This makes the assumption that you only have text files in your document folder and no sub-folders
    if os.path.isfile(doc_root + '/' + item):
        print "Loading \'" + item + "\' into spaCy..."
        doc = en_nlp(ingest_text(doc_root + '/' + item))
    else:
        print "Skipping \'" + item + "\'..."
        continue

    # Prepare the output file for writing
    print "Parsing \'" + item + "\'..."
    men_outfile = open('output' + '/' + item.split('.')[0] + ' - Dependencies (Men).txt', 'w')
    women_outfile = open('output' + '/' + item.split('.')[0] + ' - Dependencies (Women).txt', 'w')

    # Now we can parse the text!
    # For each sentence, tokenize the words and determine their dependency structure
    # End files will be anywhere from 500 KB to 3 MB each
    for sentence in doc.sents:
        # print >> outfile, sentence
        for word in sentence:
            # Skip punctuation and blank word tokens
                # TODO - revise parse mechanism; more robust, handle span lefts/rights of root, more pronouns, and names
                # Very rudimentary and limited - pull any appearance with a male subject into the text file
                if word.dep_ == 'nsubj' and word.text == 'he':
                    # If this case is 'true,' we've found a relevant sentence, so pull it and tag word dependencies
                    print >> men_outfile, sentence
                    for tagged_word in sentence:
                        if tagged_word.dep_ != 'punct' and not tagged_word.is_space:
                            print >> men_outfile, tagged_word, " : ", tagged_word.dep_
                    print >> men_outfile, '---'
                    break
                # Do likewise for female subjects
                elif word.dep_ == 'nsubj' and word.text == 'she':
                    print >> women_outfile, sentence
                    for tagged_word in sentence:
                        if tagged_word.dep_ != 'punct' and not tagged_word.is_space:
                            print >> women_outfile, tagged_word, " : ", tagged_word.dep_
                    print >> women_outfile, '---'
                    break
    men_outfile.close()
    women_outfile.close()
