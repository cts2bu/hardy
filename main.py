# -*- coding: utf-8 -*-
"""
Christopher Smith
King's College London 2017
"""

import spacy
import os

# Three lists to handle part of speech tagging.

SUBJECTS = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
ADJECTIVES = ["acomp", "advcl", "advmod", "amod", "appos", "nn", "nmod", "ccomp", "complm",
              "hmod", "infmod", "xcomp", "rcmod", "poss", "possessive"]
POTENTIAL_TARGET_DEPS = ["dobj", "pobj", "poss"]

# Two other lists to handle gendering referees in a sentence.
# Probably missing some stuff, so still needs some refinement.
MALE_TARGETS = ['he', 'him', 'his', 'man', 'himself', 'men', 'boy', 'boys', 'husband', 'father', 'uncle', 'mister',
                'mr.', 'sir', 'gabriel', 'oak', 'francis', 'frank', 'troy', 'william', 'boldwood', 'jan', 'coggan',
                'joseph', 'poorgrass', 'cain', 'cainy', 'ball', 'pennyways', 'billy', 'jude', 'fawley', 'richard',
                'phillotson', 'angel', 'clare', 'alec', "d'urberville", 'john', 'durbeyfield', 'felix', 'cuthbert',
                'michael', 'henchard', 'donald', 'farfrae', 'newson', 'joshua', 'jopp', 'abel', 'whittle', 'benjamin',
                'grower', 'christopher', 'coney', 'nance', 'mockridge', 'solomon', 'longways']
FEMALE_TARGETS = ['she', 'her', 'woman', 'herself', 'women', 'girl', 'girls', 'wife', 'mother', 'aunt', 'miss', 'ms.',
                  'mrs.', 'maid', 'maiden', 'bathsheba', 'everdene', 'fanny', 'robin', 'liddy', 'sue', 'susanna',
                  'bridehead', 'arabella', 'donn', 'drusilla', 'tess', 'joan', 'marian', 'izz', 'huett', 'retty',
                  'priddle', 'eliza', 'elizabeth', 'elizabeth-jane', 'lucetta', 'templeton', 'susan']

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
def write_to_file(sentence_tokens, outfile):
    joined_sentence = ' '.join([sentence_token.orth_ for sentence_token in sentence_tokens])
    print >> outfile, joined_sentence.encode('utf8')
    print >> outfile, '---'

"""
I wrote the following method as well, although it owes some ideas to the following two files:
http://github.com/NSchrading/intro-spacy-nlp/blob/master/subject_object_extraction.py
https://stackoverflow.com/a/40014532 [Accessed 4 June 2017].
"""


# A helper method - take a full tokenized sentence and parses it for svaos: (s)ubject, (v)erb, (a)djective, (o)bject.
# This works by finding each verb in a sentence first, then:
# -> Determining the verb's subject and its descriptors (left subtree).
# -> Determining the verb's object and any other associated parts of the sentence (right subtree).
# This essentially re-builds the sentence from the svao up, but by collecting the subject in this way, we can gender it.
def find_svos(tokens):
        svos = []
        # Get the verbs
        verbs = [token for token in tokens if token.pos_ == "VERB" and token.dep_ != "aux"]
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
            subject_descriptors = [token for token in tokens if token.head == subject and token.dep_ != 'prep']  # Include associated words
            object_words = list(verb.rights)  # Finally, include all right (objectival) parts of the verb subtree
            svos.append([subject_descriptors, subject, verb, object_words])
        return svos


# Now, we're into the main part of the program.

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
    # Use this for a one file-per-novel pass
    male_outfile = open('output' + '/' + item.split('.')[0] + ' - Dependencies (Male).txt', 'w')
    female_outfile = open('output' + '/' + item.split('.')[0] + ' - Dependencies (Female).txt', 'w')
    # TODO - Maybe have an 'I' file and a 'they' file?
    rest_outfile = open('output' + '/' + item.split('.')[0] + ' - Dependencies (Other).txt', 'w')
    """
    # Use this for a a one file-per-gender pass
    male_outfile = open('output/All Dependencies (Male).txt', 'w')
    female_outfile = open('output/All Dependencies (Female).txt', 'w')
    rest_outfile = open('output/All Dependencies (Other).txt', 'w')
    """
    # Use for tracking total number of SVOs per object
    male_svo_count = 0
    female_svo_count = 0

    # OK, so, SVO == subject, verb, and object phrase + adjectival context or the goal object of the program.
    # This block of code parses every sentence of the text for these SVOs, and then:
    # -> Determines what words are connected with the subject.
    # -> Determines the gender of the subject.
    # -> Puts each SVO in its appropriate file.
    for sentence in doc.sents:
        sentence_svos = find_svos(sentence)
        all_tokens = []  # Will hold a running list of tokens to stop repeats in appending
        for svo in sentence_svos:
            target_words = []  # The tokens we want to write to a file
            svo_subject_descriptors = svo[0]
            svo_subject = svo[1]
            svo_verb = svo[2]
            svo_object_words = svo[3]
            for subject_descriptor in svo_subject_descriptors:  # Run through each descriptor, add if not present
                if subject_descriptor not in all_tokens:
                    target_words.append(subject_descriptor)
                all_tokens.append(subject_descriptor)
            if svo_subject not in all_tokens:  # Run through the subject, add if not present
                target_words.append(svo_subject)
            all_tokens.append(svo_subject)
            if svo_verb not in all_tokens:  # Run through the verb, add if not present
                target_words.append(svo_verb)
            all_tokens.append(svo_verb)
            # A choice here - full sentences associated with genders, OR adjectives only?
            # For an adjectival focus, comment out line 142 and replace with line 141.
            for obj_word in svo_object_words:
                descendants = [desc for desc in obj_word.subtree] # Check all parts of subtree (gets adjectives, etc.)
                if descendants:  # If we have right descendants, include
                    for desc_tok in descendants:
                        if desc_tok.dep_ != 'SPACE' and desc_tok not in all_tokens:
                            target_words.append(desc_tok)
                        all_tokens.append(desc_tok)
            if target_words:  # Now, figure out the gender of the SVO
                svo_subject = svo_subject.text.lower()  # Make the subject lowercase for easier comparisons
                tokens_as_strings = [word.text.lower() for word in target_words]  # For string comparisons, etc.
                # Easy part: if the subject of the sentence is 'male' or 'female', tag and move on
                if svo_subject in MALE_TARGETS:
                    write_to_file(target_words, male_outfile)
                    male_svo_count += 1
                elif svo_subject in FEMALE_TARGETS:
                    write_to_file(target_words, female_outfile)
                    female_svo_count += 1
                # Hard part: need to check for the multifarious other situations.
                # Check pobjs (passive objects), then dobjs (dative objects), poss (possessives), then subjects again
                # The second subject check is necessary, otherwise a particularly large svao may go in the wrong file
                elif any(word.text.lower() in MALE_TARGETS and word.dep_ in POTENTIAL_TARGET_DEPS
                         for word in target_words):
                    write_to_file(target_words, male_outfile)
                    male_svo_count += 1
                elif any(word.text.lower() in FEMALE_TARGETS and word.dep_ in POTENTIAL_TARGET_DEPS
                         for word in target_words):
                    write_to_file(target_words, female_outfile)
                    female_svo_count += 1
                elif any(word.text.lower() in MALE_TARGETS and word.dep_ in SUBJECTS for word in target_words):
                    write_to_file(target_words, male_outfile)
                    male_svo_count += 1
                elif any(word.text.lower() in FEMALE_TARGETS and word.dep_ in SUBJECTS for word in target_words):
                    write_to_file(target_words, female_outfile)
                    female_svo_count += 1
                # If we can't place it anywhere, throw the SVO in the file of shame
                else:
                    write_to_file(target_words, rest_outfile)
    male_outfile.close()
    female_outfile.close()
    rest_outfile.close()

    print "Number of male SVOs in \'" + item + "\'", male_svo_count
    print "Number of female SVOs in \'" + item + "\'", female_svo_count
