# -*- coding: utf-8 -*-
#
# (c)2024  Henrique Moreira

""" Dump MCards() to text-based output

Author: Henrique Moreira
"""

# pylint: disable=missing-function-docstring

import gcontacts.mcard
from gcontacts.mcharacter import CardSeq
from gcontacts.dprint import dprint


def process_outtext(indir, outdir="", debug=0):
    """ Dump text-based output from MCards() """
    outdir = outdir if outdir else indir
    assert isinstance(outdir, str), "outdir string?"
    dprint(
        f"process_outtext(): indir={indir}, outdir={outdir}",
        debug=debug,
    )
    cards = gcontacts.mcard.MCards(fromdir=indir)
    cseq = CardSeq(cards, outdir)
    code, msg = 0, ""
    cseq.write_outs()
    return code, msg, cseq
