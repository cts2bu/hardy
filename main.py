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


# A helper method - takes a sentence and a gender tag and writes it to the appropriate destination file
def write_to_file(sentence, outfile):
        print >> outfile, sentence
        for tagged_word in sentence:
            if tagged_word.dep_ != 'punct' and not tagged_word.is_space:
                print >> outfile, tagged_word, " : ", tagged_word.dep_
        print >> outfile, '---'

# TODO - make a targeted list of names in the novels; currently the script only does very rudimentary pronoun search
male_char_names = ['oak', 'gabriel', 'troy', 'boldwood']
female_char_names = ['bathsheba']

# First, set the document roots for input texts and the output text files.
doc_root = 'corpus/unicode'  # Change this to whatever folder holds your texts
out_dir = 'output'  # Change this to whatever folder will hold your outputted files

print "Loading spaCy dictionary (this will take a while)..."
en_nlp = spacy.load('en')  # Load the spaCy dictionary
print "Dictionary loaded."

# OK, now iterate through your document folder and pull the source files one by one
for item in os.listdir(doc_root):
    # The script assumes that your doc_root folder only contains the text files to parse, but I check isfile anyway
    if os.path.isfile(doc_root + '/' + item):
        print "Loading \'" + item + "\' into spaCy..."
        doc = en_nlp(ingest_text(doc_root + '/' + item))
    else:
        print "Skipping \'" + item + "\'..."
        continue

    # Prepare the output file for writing
    print "Parsing \'" + item + "\'..."
    male_outfile = open('output' + '/' + item.split('.')[0] + ' - Dependencies (Male).txt', 'w')
    female_outfile = open('output' + '/' + item.split('.')[0] + ' - Dependencies (Female).txt', 'w')
    rest_outfile = open('output' + '/' + item.split('.')[0] + ' - Dependencies (Other).txt', 'w')

    # Now we can parse the text!
    # For each sentence, tokenize the words and determine their dependency structure
    # End files will be anywhere from 500 KB to 3 MB each
    for sentence in doc.sents:
        tagged = False
        for word in sentence:
            # TODO - nsubj v pobj.
            # Check each word's part of speech. Do different things based on that part of speech.
            if word.dep_ == 'nsubj':
                subj = word.text.lower()
                if subj == 'he' or subj in male_char_names:
                    write_to_file(sentence, male_outfile)
                    tagged = True
                    break
                elif subj == 'she' or subj in female_char_names:
                    write_to_file(sentence, female_outfile)
                    tagged = True
                    break
            elif word.dep_ == 'poss':
                poss = word.text.lower()
                if poss == 'his':
                    write_to_file(sentence, male_outfile)
                    tagged = True
                    break
                elif poss == 'her':
                    write_to_file(sentence, female_outfile)
                    tagged = True
                    break
            elif word.dep_ == 'pobj':
                pobj = word.text.lower()
        # If it's not specifically gendered, put it in the 'general' catch-all file.
        if not tagged:
            write_to_file(sentence, rest_outfile)
    male_outfile.close()
    female_outfile.close()
    rest_outfile.close()
