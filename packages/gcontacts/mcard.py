# -*- coding: utf-8 -*-
#
# (c)2024  Henrique Moreira

""" mcard -- generated from google contacts

Format: 79 lines, see fields.py DEF_FIELDS;

Non-empty line:
	NUM: value
Empty line (ends with a dot)
	NUM.

Author: Henrique Moreira
"""

# pylint: disable=missing-function-docstring

import os
import gcontacts.fields
import gcontacts.simplex
from gcontacts.simplifier import simpler_words
from gcontacts.csvpayload import CPayload


class MLine():
    def __init__(self, astr=None, name=""):
        """ Init. MCard line """
        self.name = name if name else "?"
        self._line = "" if astr is None else self._from_string(astr)
        assert isinstance(self._line, str), "String"

    def ascii(self) -> str:
        """ Return un-accented words. """
        astr = simpler_words(self._line)
        return astr

    def _from_string(self, astr):
        res = CPayload().unquoted(astr)
        return res

    def __str__(self):
        """ Returns the string """
        return self._line

    def __repr__(self):
        """ Returns the string representation """
        return repr(self._line)

class MCards(MLine):
    def __init__(self, mkeys=None, fromdir=None, name=""):
        """ Init. cards (contacts) """
        super().__init__(name=name)
        self._adir = ""
        self.mkeys = [] if mkeys is None else mkeys
        self._raw, self.data = [], []
        self.byname = {}
        if fromdir is None:
            assert isinstance(self.mkeys, list)
        else:
            self._adir = fromdir
            assert not mkeys, self.name
            self._from_dir(fromdir)
        self._update()

    def _update(self):
        """ Several updates, as needed. """
        dct = {}
        for mcard in self.mkeys:
            if mcard.name in dct:
                dct[mcard.name].append(mcard)
            else:
                dct[mcard.name] = [mcard]
        self.byname = dct

    def _from_dir(self, fromdir:str):
        lst = [
            entry.path for entry in os.scandir(fromdir) if entry.path.endswith(".txt")
        ]
        for fname in sorted(lst):
            mkey = os.path.basename(fname)[:8]
            this = MCard(name = mkey)
            this.from_file(fname)
            print("from_file():", mkey, this.data[:4])
            hexs, first = gcontacts.simplex.primary_fields(this.data)
            this.nick = gcontacts.simplex.my_nick(first)
            assert this.name == hexs, f"{this.name} vs {hexs}, {this.data[:4]}: {this}"
            self.mkeys.append(this)
        return True

class MCard(MLine):
    """ A single MCard contact """
    def __init__(self, alist=None, name=""):
        """ Init. contact. """
        super().__init__(name=name)
        self.nick = ""
        self.data = [None] * MCard.n_fields() if alist is None else alist
        self._cont = {}

    def listed(self) -> str:
        """ Return un-accented words list. """
        res = [simpler_words(line) for line in self.data]
        return res

    def get_content(self):
        """ Return content as (numeric) dictionary. """
        assert isinstance(self._cont, dict), "Dict!"
        assert len(self._cont) == MCard.n_fields(), self.name
        return self._cont

    def from_file(self, fname) -> bool:
        with open(fname, "r", encoding="utf-8") as fdin:
            msg = self._read_from_list(fdin.readlines())
        if self.name == "?":
            self.name = os.path.basename(fname)
        return msg == ""

    def _read_from_list(self, alist, prefix=True):
        """ Returns an empty string if all ok. """
        ins = [ala.rstrip("\n") for ala in alist]
        dct = {}
        for idx, line in enumerate(ins, 1):
            msg = f"Fail parsing line {idx}: '{line}'"
            dct[idx] = ""
            if prefix:
                s_pre = f"{idx}."
                if line == s_pre:
                    continue
                s_pre = f"{idx}: "
                if line.startswith(s_pre):
                    value = MLine(line[len(s_pre):])
                else:
                    return msg
            else:
                value = MLine(line)
            dct[idx] = value
        self.data, self._raw = self._from_dict(dct)
        self._cont = dct
        return ""

    def _from_dict(self, dct):
        res, raw = [], []
        for idx in sorted(dct):
            value = str(dct[idx])
            res.append(value)
            raw.append(compatible_comma(value))
        return res, raw

    def __str__(self):
        return self.nick

    def __repr__(self):
        return repr(self.nick)

    @staticmethod
    def n_fields():
        return len(gcontacts.fields.DEF_FIELDS)

    @staticmethod
    def m_fields():
        return gcontacts.fields.DEF_FIELDS

def compatible_comma(astr):
    if isinstance(astr, MLine):
        return compatible_comma(str(astr))
    if "," not in astr:
        return astr
    if '"' not in astr:
        return '"' + astr + '"'
    new = ""
    for achr in astr:
        if achr == '"':
            new += '\\'
        new += achr
    return new
