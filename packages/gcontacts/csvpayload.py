# -*- coding: utf-8 -*-
#
# (c)2024  Henrique Moreira

""" csv payload -- from google contacts

Author: Henrique Moreira
"""

# pylint: disable=missing-function-docstring

from gcontacts.simplifier import simpler_words
from gcontacts.simplex import simpler_field
from gcontacts.fields import CFields

class CContent():
    """ Contacts content """
    def __init__(self, path:str, name=""):
        self.name = name if name else "?"
        self.msgs = []
        with open(path, "r", encoding="utf-8") as fdin:
            self._data = fdin.readlines()
        first = self._data[0]
        self.has_header = first.startswith("Name,")
        if self.has_header:
            self.head, self.cont = first.rstrip(), self._data[1:]
        else:
            self.head, self.cont = CFields().splash(), self._data
        self.fields_list = []
        self.cards = []
        self.items = []	# same as cards, but as a list
        self.tidy_header()

    def tidy_header(self):
        lst = [simpler_field(one) for one in self.head.split(",")]
        self.head = lst
        fields = CFields().byname
        self.fields_list = []
        for one in lst:
            self.fields_list.append((fields[one], one))
        return lst

    def parse(self):
        """ Process contacts content """
        astr = ''.join(self.cont)
        pay = CPayload(astr, "c1")
        self.cards = pay.seq
        return True

    def build_items(self):
        """ Updates 'items' based on 'cards' """
        self.items = []
        for card in self.cards:
            s_list = CPayload().line_wrap(card)
            self.items.append(s_list)

class CPayload():
    """ Contacts Payload """
    def __init__(self, astr="", name=""):
        self.name = name if name else "?"
        self.texts = []
        self._method = "Q"	# double-quoted
        self.seq = self.wording_wrap(astr, self._method == "Q")

    def wording_wrap(self, astr, quoted=True):
        seq = self._my_wording_wrap(astr, quoted, False)
        return seq

    def line_wrap(self, astr):
        seq = self._my_wording_wrap(astr, False, True)
        return seq

    def unquoted(self, astr):
        if len(astr) > 1 and astr.startswith('"') and astr[-1] == '"':
            return astr[1:-1]
        return astr

    def _my_wording_wrap(self, astr, quoted, repl):
        """ Streams multiple lines when double-quotes are there.
        quoted: keeps double-quotes;
        repl: used with quoted=False; replaces comma by special char.
        """
        seq = []
        state, last = 0, ""
        oldchr = ""
        idx = 0
        for achr in astr:
            if achr == '"':
                if oldchr == '\\':
                    seq.append(achr)
                    oldchr = achr
                    continue
                state = int(state == 0)
                if state:
                    last = '"'
                else:
                    assert last[0] == '"', last
                    if repl:
                        last = last.replace(",", "~!")
                    seq.append((last + '"') if quoted else last[1:])
                    last = ""
                continue
            if state:
                if achr == '\n':
                    idx += 1
                    achr = "\\n"
                last += achr
                continue
            seq.append(achr)
        assert not last, f"Dangling: '{last}'"
        if repl:
            seq = ''.join(seq).split(",")
            return [ala.replace("~!", ",") for ala in seq]
        seq = ''.join(seq).splitlines()
        self.texts.append(simpler_words(seq))
        return seq
