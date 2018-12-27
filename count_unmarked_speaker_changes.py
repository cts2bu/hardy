# -*- coding: utf-8 -*-

"""
Christopher Smith
King's College London 2017
"""

# This short file is used in Chapter 4 of my dissertation to help discuss the role of 'I' dialogue SVOs.
# It finds parts of the text where Hardy has two people talking but does not indicate a clear speaker change.
# These changes are important because the main parser does not know how to capture this shift and change speakers.

import re
import os
from svo_parser import ingest_text


# The target here are moments like the following:
# Jude said, 'I don't know.'
#
# 'What do you know?'
# The speaker changes but the text has no direct indicator. The parser will still think Jude says the second quote.
def count_unmarked_speaker_changes():
    doc_root = 'corpus/unicode'  # Change this to whatever folder holds your texts
    for item in os.listdir(doc_root):
        num_quotation_changes = 0  # Used to count the number of times a speaker changes without a textual indicator
        novel_text = ingest_text(doc_root + '/' + item)
        if item != 'Far from the Madding Crowd.txt':
            pattern = r"\"\n\n\".+?(?=\")"  # For MoC, TotD, JtO
        else:
            pattern = r"\"\n\".+?(?=\")"  # For FftMC
        res = re.findall(pattern, novel_text)
        for found in res:
            if 'I' in found:
                num_quotation_changes += 1
        print(item, num_quotation_changes)
