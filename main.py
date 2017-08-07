# -*- coding: utf-8 -*-

"""
Christopher Smith
King's College London 2017
"""

import spacy
import os
from collections import OrderedDict

# Three lists to handle part of speech tagging.
# As with the find_svos method, help with these lists came from the following project:
# http://github.com/NSchrading/intro-spacy-nlp/blob/master/subject_object_extraction.py  [Accessed 4 June 2017].
SUBJECTS = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
ADJECTIVES_AND_ADVERBS = ["acomp", "advcl", "advmod", "amod", "appos", "nn", "nmod", "ccomp", "complm", "hmod",
                          "infmod", "xcomp", "rcmod", "poss", "possessive", "aux", "neg", "auxpass"]
POTENTIAL_TARGET_DEPS = ["dobj", "pobj", "poss", "attr", "oprd"]

# Two other lists to handle gender of male and female subjects and objects.
# Probably missing some characters and specifics, but for the scale of this project is mostly fine.
MALE_TARGETS = ['he', 'him', 'his', 'man', 'men', 'himself', 'boy', 'boys', 'husband', 'father', 'uncle', 'mister',
                'mr.', 'sir', 'gabriel', 'oak', 'francis', 'frank', 'troy', 'william', 'boldwood', 'jan', 'coggan',
                'joseph', 'poorgrass', 'cain', 'cainy', 'ball', 'pennyways', 'billy', 'jacob', 'jude', 'fawley',
                'richard', 'phillotson', 'angel', 'clare', 'alec', "d'urberville", 'john', 'durbeyfield', 'felix',
                'cuthbert', 'michael', 'henchard', 'donald', 'farfrae', 'newson', 'joshua', 'jopp', 'abel', 'whittle',
                'benjamin', 'grower', 'christopher', 'coney', 'nance', 'mockridge', 'solomon', 'longways', 'male']
FEMALE_TARGETS = ['she', 'her', 'woman', 'women', 'herself', 'girl', 'girls', 'wife', 'mother', 'aunt', 'miss', 'ms.',
                  'mrs.', 'maid', 'maiden', 'bathsheba', 'everdene', 'fanny', 'robin', 'liddy', 'sue', 'susanna',
                  'bridehead', 'arabella', 'donn', 'drusilla', 'tess', 'joan', 'marian', 'izz', 'huett', 'retty',
                  'priddle', 'eliza', 'elizabeth', 'elizabeth-jane', 'lucetta', 'templeton', 'susan', 'female']


# A helper method - read in a file at the specified filesystem location and return it as a text block for spaCy ingest.
# I also have a sanity check at the end to encode the text in unicode - spaCy is picky that way.
def ingest_text(file_url):
    f = open(file_url, 'r')
    text = f.read()
    return unicode(text, 'utf8')


# A helper method - take a sentence and a gender tag and write it to the appropriate destination file.
# The writing process normalizes the spacing of the spaCy tokens to match that of a normal sentence.
def write_to_file(sentence_tokens, outfile):
    joined_sentence = ''
    for i in range(0, len(sentence_tokens)):  # Loop through every token
        curr_token = sentence_tokens[i]
        try:
            next_token = sentence_tokens[i + 1]  # Check next token up until the end
        except IndexError:
            joined_sentence += curr_token.orth_
            break
        if next_token.orth_[0].isalpha():  # If the next token is a normal word, add a space so it looks normal
            joined_sentence += curr_token.orth_
            joined_sentence += ' '
        else:  # Otherwise, the next token starts with punctuation of some sort, so don't add the extra space
            joined_sentence += curr_token.orth_
    print >> outfile, joined_sentence.encode('utf8')
    print >> outfile, '---'


# A helper method - splits out the task of adding a token to a dependency list since it's repeated so much.
# Used in adding adjectival/descriptive context to subjects, verbs, and objects in find_svos.
def add_token_and_dependencies(token, dependency_list):
    subtree = list(token.subtree)  # Get all sub-dependencies of the current token
    if subtree:  # If we have descendants, include them too, unless they've already been added
        for element in subtree:
            if element not in dependency_list:
                dependency_list.append(element)
    else:  # Otherwise, just add the token, unless it's already in there
        if token not in dependency_list:
            dependency_list.append(token)


# A helper method - take a full tokenized sentence and parses it for svos: (s)ubject, (v)erb, (o)bject.
# This works by finding each verb in a sentence first, then:
# -> Determining the verb's subject and that subject's descriptors.
# -> Determining the verb's descriptive content, such as adverbs.
# -> Determining the verb's object and any other associated parts of the sentence.
# This essentially re-builds the sentence from the svo up, but by collecting the subject in this way, we can gender it.
# Note that the order doesn't really matter; for comprehension, I later sort the words by original appearance order.
# The code is unique, but I consulted the following spaCy projects for some ideas about SVOs:
# http://github.com/NSchrading/intro-spacy-nlp/blob/master/subject_object_extraction.py (concept of SVO extraction)
# http://stackoverflow.com/a/40014532 (attempt at SVO extraction with adjectives) [Accessed 4 June 2017]
def find_svos(tokens):
    svos = []
    verbs = [token for token in tokens if token.pos_ == "VERB"]  # Get the verbs
    # For each verb, determine subject, object, and adjectival parts
    for verb in verbs:
        # Subject is any part to the left of the verb that is a nsubj/nsubjpass/etc.
        try:
            subject = [token for token in verb.lefts if token.dep_ in SUBJECTS][0]
        except IndexError:
            try:
                subject = [token for token in verb.rights if token.dep_ in SUBJECTS][0]
            except IndexError:
                continue  # If we can't find a subject, move to the next verb
        # Get descriptors of that subject (before or after subject)
        subject_descriptors = []
        for token in tokens:
            if subject in list(token.ancestors):  # Find modifiers
                add_token_and_dependencies(token, subject_descriptors)
        # Get descriptors of that verb (before or after verb)
        verb_descriptors = []
        for token in verb.lefts:
            if verb in list(token.ancestors) and token.dep_ in ADJECTIVES_AND_ADVERBS:  # Find modifiers
                add_token_and_dependencies(token, verb_descriptors)
        # Get object parts (right subtree of the verb)
        object_words = []
        for token in verb.rights:
            if token.pos_ != 'VERB':  # Don't include verbs, which would cut off later SVOs
                add_token_and_dependencies(token, object_words)
        svos.append([subject_descriptors, subject, verb_descriptors, verb, object_words])
    return svos


# Now, we're into the main part of the program.
doc_root = 'corpus/unicode'  # Change this to whatever folder holds your texts
out_dir = 'output'  # Change this to whatever folder will hold your outputted files

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

    book_title = item.split('.')[0]  # This assumes the files you're reading are saved like <title>.txt

    # Prepare the output file for writing
    print 'Parsing ' + book_title + '...'
    # Create one output file for men, one for women, and one for non-specified genders for the current text
    male_outfile = open('output' + '/' + item.split('.')[0] + ' - Dependencies (Male).txt', 'w')
    female_outfile = open('output' + '/' + item.split('.')[0] + ' - Dependencies (Female).txt', 'w')
    rest_outfile = open('output' + '/' + item.split('.')[0] + ' - Dependencies (Other).txt', 'w')
    # Finally, create a running tracker of the number of SVOs found for each gender.
    male_svo_count = 0
    female_svo_count = 0

    # So, SVO == subject, verb, and object phrase + adjectival context
    # This block of code parses every sentence of the text for these SVOs, and then:
    # -> Determines the gender of the subject
    # -> If it can't do that, determines the gender of the object
    # -> Puts each SVO in its appropriate file
    for sentence in doc.sents:
        sentence_svos = find_svos(sentence)
        all_tokens = []  # Will hold a running list of tokens to stop repeats in appending
        for svo in sentence_svos:
            target_words = []  # The tokens we want to write to a file
            # Get each variable from each svo
            svo_subject_descriptors = svo[0]
            svo_subject = svo[1]
            svo_verb_descriptors = svo[2]
            svo_verb = svo[3]
            svo_object_words = svo[4]
            # Now, keep a running list of all words things to add
            for subject_descriptor in svo_subject_descriptors:  # Run through each subject descriptor
                if subject_descriptor not in all_tokens:
                    target_words.append(subject_descriptor)
                all_tokens.append(subject_descriptor)
            if svo_subject not in all_tokens:  # Run through the subject
                target_words.append(svo_subject)
            all_tokens.append(svo_subject)
            for verb_descriptor in svo_verb_descriptors:  # Run through each verb descriptor
                if verb_descriptor not in all_tokens:
                    target_words.append(verb_descriptor)
                all_tokens.append(verb_descriptor)
            if svo_verb not in all_tokens:  # Run through the verb
                target_words.append(svo_verb)
            all_tokens.append(svo_verb)
            for obj_word in svo_object_words:  # Run through each object word
                if obj_word not in all_tokens:
                    target_words.append(obj_word)
                all_tokens.append(obj_word)
            # Now, assuming we have something to add, figure out the gender of the SVO
            if target_words:
                target_words = sorted(target_words, key=lambda target_word: target_word.i)  # Re-create sentence order
                svo_subject = svo_subject.text.lower()  # Make the subject lowercase for easier comparisons
                # Easy part: if the subject of the sentence is 'male' or 'female', tag and move on
                if svo_subject in MALE_TARGETS:
                    write_to_file(target_words, male_outfile)
                    male_svo_count += 1
                elif svo_subject in FEMALE_TARGETS:
                    write_to_file(target_words, female_outfile)
                    female_svo_count += 1
                # Hard part: need to check for the multifarious other situations.
                # Check pobjs (passive objects), then dobjs (dative objects), poss (possessives), then subjects again
                # The second subject check is necessary, otherwise a particularly large svo may go in the wrong file
                elif any(word.text.lower() in MALE_TARGETS and word.dep_ in POTENTIAL_TARGET_DEPS
                         for word in target_words):
                    write_to_file(target_words, male_outfile)
                    male_svo_count += 1
                elif any(word.text.lower() in FEMALE_TARGETS and word.dep_ in POTENTIAL_TARGET_DEPS
                         for word in target_words):
                    write_to_file(target_words, female_outfile)
                    female_svo_count += 1
                elif any(word.text.lower() in MALE_TARGETS and word.dep_ in SUBJECTS
                         for word in target_words):
                    write_to_file(target_words, male_outfile)
                    male_svo_count += 1
                elif any(word.text.lower() in FEMALE_TARGETS and word.dep_ in SUBJECTS
                         for word in target_words):
                    write_to_file(target_words, female_outfile)
                    female_svo_count += 1
                # If we can't place it anywhere, throw the SVO in the file of shame
                else:
                    write_to_file(target_words, rest_outfile)
    male_outfile.close()
    female_outfile.close()
    rest_outfile.close()

    svo_counts['Male SVOs in ' + book_title] = male_svo_count
    svo_counts['Female SVOs in ' + book_title] = female_svo_count

# Print the total number of SVOs per gender per text
for filename in svo_counts.keys():
    print filename + ': ' + str(svo_counts[filename])
