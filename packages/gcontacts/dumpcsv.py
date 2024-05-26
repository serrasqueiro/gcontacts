#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c)2024  Henrique Moreira
""" Dump google contacts csv

Author: Henrique Moreira
"""

# pylint: disable=missing-function-docstring, consider-using-with

import sys
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
    assert path
    verbose = opts["verbose"]
    debug = int(verbose >= 3)
    code, msg, dct = process_csv(path, err, verbose, debug)
    if code:
        print("Error:", msg, end="\n\n")
        return code
    return 0

def process_csv(path:str, err, verbose, debug=0):
    """ Open csv """
    code, dct = 0, {}
    dprint("### process_csv():", path, "; debug:", debug, debug=debug)
    dprint("### process_csv() ends:", code)
    return 0, "", dct

if __name__ == "__main__":
    main()
