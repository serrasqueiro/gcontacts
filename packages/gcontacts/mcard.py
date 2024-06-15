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

import gcontacts.fields
from gcontacts.simplifier import simpler_words


class MLine():
    def __init__(self, astr=None, name=""):
        """ Init. MCard line """
        self.name = name if name else "?"
        self._line = "" if astr is None else astr
        assert isinstance(self._line, str), "String"

    def ascii(self) -> str:
        """ Return un-accented words. """
        astr = simpler_words(self._line)
        return astr

    def __str__(self):
        """ Returns the string """
        return self._line

    def __repr__(self):
        """ Returns the string representation """
        return repr(self._line)

class MCard(MLine):
    """ A single MCard contact """
    # pylint: disable=line-too-long, anomalous-backslash-in-string
    def __init__(self, alist=None, name=""):
        """ Init. contact. """
        super().__init__(name=name)
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
        self.data, self._cont = self._from_dict(dct)
        return ""

    def _from_dict(self, dct):
        res = []
        for idx in sorted(dct):
            res.append(compatible_comma(dct[idx]))
        return res, dct

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
