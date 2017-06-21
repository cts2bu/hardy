# -*- coding: utf-8 -*-
"""
Christopher Smith
King's College London 2017
"""

import spacy
import os
from collections import OrderedDict

# Three lists to handle part of speech tagging.

SUBJECTS = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
ADJECTIVES = ["acomp", "advcl", "advmod", "amod", "appos", "nn", "nmod", "ccomp", "complm",
              "hmod", "infmod", "xcomp", "rcmod", "poss", "possessive", "aux"]
POTENTIAL_TARGET_DEPS = ["dobj", "pobj", "poss"]

# Two other lists to handle gendering referees in a sentence.
# Probably missing some stuff, so still needs some refinement.
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

"""
Helper methods I wrote.
"""


# A helper method - read in a file at the specified filesystem location and return it as a text block for tokenization.
# I also have a sanity check at the end to encode the text in unicode - spaCy is picky that way.
def ingest_text(file_url):
    f = open(file_url, 'r')
    text = f.read()
    return unicode(text, 'utf8')


# A helper method - takes a sentence and a gender tag and writes it to the appropriate destination file.
# The writing process normalizes the spacing of the tokens to match that of a normal sentence.
def write_to_file(sentence_tokens, outfile):
    joined_sentence = ''
    for i in range(0, len(sentence_tokens)):  # Loop through every token
        curr_token = sentence_tokens[i]
        try:
            next_token = sentence_tokens[i + 1]  # Check next token up until the end
        except IndexError:
            joined_sentence += curr_token.orth_
            break
        if next_token.orth_[0].isalpha():  # If the next token is a normal word, add a space to this one and move on
            joined_sentence += curr_token.orth_
            joined_sentence += ' '
        else:  # Otherwise, the next token starts with punctuation of some sort, so don't add the extra space
            joined_sentence += curr_token.orth_
    print >> outfile, joined_sentence.encode('utf8')
    print >> outfile, '---'


"""
I wrote the following method as well, although it owes some ideas to the following two files:
http://github.com/NSchrading/intro-spacy-nlp/blob/master/subject_object_extraction.py
https://stackoverflow.com/a/40014532 [Accessed 4 June 2017].
"""


# A helper method - take a full tokenized sentence and parses it for svos: (s)ubject, (v)erb, (o)bject.
# This works by finding each verb in a sentence first, then:
# -> Determining the verb's subject and that subject's descriptors.
# -> Determining the verb's object and any other associated parts of the sentence.
# This essentially re-builds the sentence from the svo up, but by collecting the subject in this way, we can gender it.
# Note that the order doesn't really matter; for comprehension, we later sort the words by original appearance order.
def find_svos(tokens):
    svos = []
    # Get the verbs
    verbs = [token for token in tokens if token.pos_ == "VERB" and token.dep_ != "aux"]
    # Sort by sentence index maybe?
    # For each verb, determine subject, object, and adjectives
    for verb in verbs:
        # Saying subject is any part of left that is a nsubj/nsubjpass/etc., which for spaCy is pretty accurate
        try:
            subject = [token for token in verb.lefts if token.dep_ in SUBJECTS][0]
        except IndexError:
            try:
                subject = [token for token in verb.rights if token.dep_ in SUBJECTS][0]
            except IndexError:
                continue
        subject_descriptors_l = [token for token in tokens if subject in list(token.ancestors)
                                 and token not in list(subject.rights)]
        subject_descriptors_r = [token for token in tokens if subject in list(token.ancestors)
                                 and token not in list(subject.lefts)]
        verb_descriptors = [token for token in verb.lefts if verb in list(token.ancestors)
                            and token.dep_ in ADJECTIVES]
        object_words = list(verb.rights)  # Finally, include all right (objectival) parts of the verb subtree
        svos.append([subject_descriptors_l, subject, subject_descriptors_r, verb_descriptors, verb, object_words])
    return svos

# Now, we're into the main part of the program.

doc_root = 'corpus/unicode'  # Change this to whatever folder holds your texts
out_dir = 'output'  # Change this to whatever folder will hold your outputted files

print "Loading spaCy dictionary (this will take a while)..."
en_nlp = spacy.load('en')  # Load the spaCy dictionary
print "Dictionary loaded."

svo_counts = OrderedDict()  # Used to track total number of SVOs across all documents
# OK, now iterate through your document folder and pull the source files one by one
for item in os.listdir(doc_root):
    # The script assumes that your doc_root folder only contains the text files to parse, but I check isfile anyway
    if os.path.isfile(doc_root + '/' + item):
        print "Loading \'" + item + "\' into spaCy..."
        doc = en_nlp(ingest_text(doc_root + '/' + item))
    else:
        print "Skipping \'" + item + "\'..."
        continue

    book_title = item.split('.')[0]

    # Prepare the output file for writing
    print 'Parsing ' + book_title + '...'
    # Use this for a one file-per-novel pass
    male_outfile = open('output' + '/' + item.split('.')[0] + ' - Dependencies (Male).txt', 'w')
    female_outfile = open('output' + '/' + item.split('.')[0] + ' - Dependencies (Female).txt', 'w')
    # TODO - Maybe have an 'I' file and a 'they' file?
    rest_outfile = open('output' + '/' + item.split('.')[0] + ' - Dependencies (Other).txt', 'w')
    """
    # Use this for a a one ile-per-gender pass
    male_outfile = open('output/All Dependencies (Male).txt', 'w')
    female_outfile = open('output/All Dependencies (Female).txt', 'w')
    rest_outfile = open('output/All Dependencies (Other).txt', 'w')
    """
    # Use for tracking total number of SVOs per object
    male_svo_count = 0
    female_svo_count = 0

    # OK, so, SVO == subject, verb, and object phrase + adjectival context or the goal object of the program
    # This block of code parses every sentence of the text for these SVOs, and then:
    # -> Determines what words are connected with the subject
    # -> Determines the gender of the subject
    # -> Puts each SVO in its appropriate file
    for sentence in doc.sents:
        sentence_svos = find_svos(sentence)
        all_tokens = []  # Will hold a running list of tokens to stop repeats in appending
        for svo in sentence_svos:
            target_words = []  # The tokens we want to write to a file
            # Get each variable from each svo
            svo_subject_descriptors_l = svo[0]
            svo_subject = svo[1]
            svo_subject_descriptors_r = svo[2]
            svo_verb_descriptors = svo[3]
            svo_verb = svo[4]
            svo_object_words = svo[5]
            # Now, add the parts into a target list, assuming they haven't already been added to another SVO
            for subject_descriptor_l in svo_subject_descriptors_l:  # Run through each left descriptor
                if subject_descriptor_l not in all_tokens:
                    target_words.append(subject_descriptor_l)
                all_tokens.append(subject_descriptor_l)
            if svo_subject not in all_tokens:  # Run through the subject
                target_words.append(svo_subject)
            all_tokens.append(svo_subject)
            for subject_descriptor_r in svo_subject_descriptors_r:  # Run through each right descriptor
                if subject_descriptor_r not in all_tokens:
                    target_words.append(subject_descriptor_r)
                all_tokens.append(subject_descriptor_r)
            for verb_descriptor in svo_verb_descriptors:  # Run through each verb descriptor
                if verb_descriptor not in all_tokens:
                    target_words.append(verb_descriptor)
                all_tokens.append(verb_descriptor)
            if svo_verb not in all_tokens:  # Run through the verb
                target_words.append(svo_verb)
            all_tokens.append(svo_verb)
            # For the object parts, we want to determine the full descendant subtree to capture adjectives, etc.
            for obj_word in svo_object_words:
                descendants = [desc for desc in obj_word.subtree]  # Check all parts of subtree (gets adjectives, etc.)
                if descendants:  # If we have descendants, include them (again, as long as they aren't already included)
                    for desc_tok in descendants:
                        if desc_tok.dep_ != 'SPACE' and desc_tok not in all_tokens:
                            target_words.append(desc_tok)
                        all_tokens.append(desc_tok)
            # Now, assuming we have something to add, figure out the gender of the SVO
            # We don't want to write the same SVO to the same file twice, but the same SVO *can* go in both files
            if target_words:
                target_words = sorted(target_words, key=lambda target_word: target_word.i)  # Sorts by sentence order
                written_to_male_file = False  # Tracks whether we've written to a male file
                written_to_female_file = False  # Tracks whether we've written to the female file
                svo_subject = svo_subject.text.lower()  # Make the subject lowercase for easier comparisons
                tokens_as_strings = [word.text.lower() for word in target_words]  # For string comparisons, etc.
                # Easy part: if the subject of the sentence is 'male' or 'female', tag and move on
                if svo_subject in MALE_TARGETS:
                    write_to_file(target_words, male_outfile)
                    male_svo_count += 1
                    written_to_male_file = True
                if svo_subject in FEMALE_TARGETS:
                    write_to_file(target_words, female_outfile)
                    female_svo_count += 1
                    written_to_female_file = True
                # Hard part: need to check for the multifarious other situations.
                # Check pobjs (passive objects), then dobjs (dative objects), poss (possessives), then subjects again
                # The second subject check is necessary, otherwise a particularly large svo may go in the wrong file
                if any(word.text.lower() in MALE_TARGETS and word.dep_ in POTENTIAL_TARGET_DEPS
                       for word in target_words) and not written_to_male_file:
                    write_to_file(target_words, male_outfile)
                    male_svo_count += 1
                    written_to_male_file = True
                if any(word.text.lower() in FEMALE_TARGETS and word.dep_ in POTENTIAL_TARGET_DEPS
                       for word in target_words) and not written_to_female_file:
                    write_to_file(target_words, female_outfile)
                    female_svo_count += 1
                    written_to_female_file = True
                if any(word.text.lower() in MALE_TARGETS and word.dep_ in SUBJECTS
                       for word in target_words) and not written_to_male_file:
                    write_to_file(target_words, male_outfile)
                    male_svo_count += 1
                    written_to_male_file = True
                if any(word.text.lower() in FEMALE_TARGETS and word.dep_ in SUBJECTS
                       for word in target_words) and not written_to_female_file:
                    write_to_file(target_words, female_outfile)
                    female_svo_count += 1
                    written_to_female_file = True
                # If we can't place it anywhere, throw the SVO in the file of shame
                if not written_to_male_file and not written_to_female_file:
                    write_to_file(target_words, rest_outfile)
    male_outfile.close()
    female_outfile.close()
    rest_outfile.close()

    svo_counts['Male SVOs in ' + book_title] = male_svo_count
    svo_counts['Female SVOs in ' + book_title] = female_svo_count

for filename in svo_counts.keys():
    print filename + ': ' + str(svo_counts[filename])
