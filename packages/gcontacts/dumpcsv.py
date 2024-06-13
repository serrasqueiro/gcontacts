#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c)2024  Henrique Moreira
""" Dump google contacts csv

Author: Henrique Moreira
"""

# pylint: disable=missing-function-docstring

import sys
import os.path
import gcontacts.csvpayload
import gcontacts.goutprocess
from gcontacts.simplifier import simpler_words
from gcontacts.csvpayload import CContent, CPayload
from gcontacts.dprint import dprint

def main():
    """ Main (non-interactive) script """
    code = process(sys.stdout, sys.stderr, sys.argv[1:])
    if code is None:
        print(f"""Usage:

{__file__} [options] [path.csv]

Options are:
  -v                Verbose (twice: -v -v, more verbose)

Verbose:
	0	Basic dump
	1	More verbose
	2	Too verbose
	3	Debug
""")
    sys.exit(code if code else 0)


def process(out, err, args):
    opts = {
        "verbose": 0,
    }
    param = args
    while param and param[0].startswith("-"):
        this = param[0]
        if this.startswith("-v"):
            assert len(this) == this.count("v") + 1, this
            opts["verbose"] += this.count("v")
            del param[0]
            continue
        return None
    if not param:
        param = ["contacts.csv"]
    if len(param) > 1:
        return None
    apath = param[0]
    if opts["verbose"] > 3:
        print("Too much verbose!", end="\n\n")
        return None
    code = do_it(out, err, apath, opts)
    return code


def do_it(out, err, path, opts) -> int:
    """ Main script
    """
    assert path, "do_it()"
    verbose = opts["verbose"]
    debug = int(verbose >= 3)
    if os.path.isdir(path):
        code, msg = process_out(["contacts.csv"], (path,), verbose, debug)
        if code:
            print("Error:", msg)
        return code
    code, msg, dct = process_csv(path, err, verbose, debug)
    if code:
        print("Error:", msg, end="\n\n")
        return code
    cards = dct["cards"]
    dump_cards(cards)
    return 0

def dump_cards(cards):
    for idx, card in enumerate(cards, 1):
        pay = CPayload()
        lst = simpler_words(pay.line_wrap(card))
        print(
            f"{idx}: (len={len(lst)})\n",
            lst,
            end="\n\n"
        )

def process_csv(path:str, err, verbose, debug=0):
    """ Open csv """
    code = 0
    dprint("### process_csv():", path, "; debug:", debug, debug=debug)
    ccc = CContent(path, "contacts")
    ccc.parse()
    dprint("### process_csv() ends:", code)
    dct = {
        "ccc": ccc,
        "cards": ccc.cards,	# a plain list of cards, comma separated
    }
    if verbose > 0:
        print("# Header:", ccc.head, end="\n<<<\n\n")
    if verbose >= 3:
        for idx, field in ccc.fields_list:
            print("# Field idx:", idx, field)
    return 0, "", dct

def process_out(c_list, c_opts, verbose=0, debug=0):
    assert debug >= 0, "Debug!"
    if not c_list:
        return 1, "No contacts (list)"
    if len(c_list) > 1:
        return 3, "Too many inputs"
    outdir = c_opts[0]
    path = c_list[0]
    ccc = CContent(path)
    ccc.parse()
    code, msg = gcontacts.goutprocess.process_outs(path, outdir, ccc, debug)
    return code, msg

if __name__ == "__main__":
    main()
