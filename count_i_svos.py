# -*- coding: utf-8 -*-

"""
Christopher Smith
King's College London 2017
"""

# This short file helps with Chapter 4 of my dissertation.
# It is structurally very similar to main, except it merely counts the number of SVOs with "I" as the subject.

import spacy
import os
from svo_parser import ingest_text, find_svos
from collections import OrderedDict

# Three lists to handle part of speech tagging and SVO association.
# As with the find_svos method, help with these lists came from the following project:
# http://github.com/NSchrading/intro-spacy-nlp/blob/master/subject_object_extraction.py  [Accessed 4 June 2017].
SUBJECTS = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
ADJECTIVES_AND_ADVERBS = ["acomp", "advcl", "advmod", "amod", "appos", "nn", "nmod", "ccomp", "complm", "hmod",
                          "infmod", "xcomp", "rcmod", "poss", "possessive", "aux", "neg", "auxpass"]
POTENTIAL_TARGET_DEPS = ["dobj", "pobj", "iobj", "poss", "attr", "oprd"]


# The driver of the program.
# Reads in the Hardy texts, finds the SVOs, and checks to see if the subject is 'I.'
def process_files():
    doc_root = 'corpus/unicode'  # Change this to whatever folder holds your texts

    # Load the spaCy dictionary
    print "Loading spaCy dictionary (this will take a while)..."
    en_nlp = spacy.load('en')
    print "Dictionary loaded."

    svo_counts = OrderedDict()  # Used to track total number of SVOs across all documents
    # Now, iterate through your document folder and pull the source files one by one
    for item in os.listdir(doc_root):
        # The script assumes that your doc_root folder only contains the text files to parse, but I check isfile anyway
        if os.path.isfile(doc_root + '/' + item):
            print "Loading \'" + item + "\' into spaCy..."
            doc = en_nlp(ingest_text(doc_root + '/' + item))
        else:
            print "Skipping \'" + item + "\'..."
            continue

        book_title = item.split('.')[0]  # This assumes the files you'repobj reading are saved like <title>.txt

        # Prepare the file for parsing
        print 'Parsing ' + book_title + '...'
        # Create a running tracker of the number of SVOs found with 'I' as the subject.
        i_svo_count = 0
        # So, SVO == subject, verb, and object phrase + adjectival context
        # This block of code parses every sentence of the text for these SVOs, and then:
        # -> Pulls out the subject
        # -> Checks to see if it is 'I' or not before incrementing a counter
        for sentence in doc.sents:
            sentence_svos = find_svos(sentence)  # Get the SVOs for the current sentence
            for svo in sentence_svos:
                svo_subject = svo[1].text  # Get the subject
                if svo_subject == 'I':  # If it is 'I', increment the counter
                    i_svo_count += 1

        svo_counts['"I" SVOs in ' + book_title] = i_svo_count

    # Print the total number of SVOs per gender per text
    for filename in svo_counts.keys():
        print filename + ': ' + str(svo_counts[filename])


# Run the program!
def main():
    process_files()

if __name__ == '__main__':
    main()
