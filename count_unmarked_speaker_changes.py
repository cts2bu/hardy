# -*- coding: utf-8 -*-

"""
Christopher Smith
King's College London 2017
"""

# This short file helps with Chapter 4 of my dissertation.
# It finds parts of the text where Hardy has two people talking but does not indicate a clear speaker change.
# These changes are important because the main parser does not know how to capture this shift!

import re, os

# A helper method, copied from main.
def ingest_text(file_url):
    f = open(file_url, 'r')
    text = f.read()
    return unicode(text, 'utf8')


doc_root = 'corpus/unicode'  # Change this to whatever folder holds your texts
for item in os.listdir(doc_root):
    num_quotation_changes = 0  # Used to count the number of times a speaker changes without a clear textual indicator
    text = ingest_text(doc_root + '/' + item)
    if item != 'Far from the Madding Crowd.txt':
        pattern = r"\"\n\n\".+?(?=\")" # For MoC, TotD, JtO
    else:
        pattern = r"\"\n\".+?(?=\")" # For FftMC
    res = re.findall(pattern, text)
    for found in res:
        if 'I' in found:
            num_quotation_changes += 1
    print item, num_quotation_changes