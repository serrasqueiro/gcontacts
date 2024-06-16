# -*- coding: utf-8 -*-
#
# (c)2024  Henrique Moreira

""" Dump MCards() to text-based output

Author: Henrique Moreira
"""

# pylint: disable=missing-function-docstring

import os.path
import gcontacts.mcard
from gcontacts.mcharacter import MainCard
from gcontacts.dprint import dprint


def process_outtext(cards, indir, outdir="", debug=1):
    """ Dump text-based output from MCards() """
    outdir = outdir if outdir else indir
    assert isinstance(outdir, str), "outdir string?"
    dprint(
        f"process_outtext(): {cards}, indir={indir}, outdir={outdir}",
        debug=debug,
    )
    outs = {
        "phone": os.path.join(outdir, "txt-phone.csv"),
    }
    cards = gcontacts.mcard.MCards(fromdir=indir)
    lst = [MainCard(crd) for crd in cards.data]
    mlist = []
    for mcard in lst:
        if mcard.name != "f8c4d7d9": continue
        dprint(
            mcard.name, mcard.nicks["Phone"],
            debug=debug,
        )
        mlist.append(mcard)
    code, msg = 0, ""
    return code, msg, mlist
