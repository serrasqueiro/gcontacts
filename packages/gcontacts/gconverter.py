# -*- coding: utf-8 -*-
#
# (c)2024  Henrique Moreira

""" gconverter -- converts e.g. 42 fields into 79 standard google contacts csv listing

Author: Henrique Moreira
"""

# pylint: disable=missing-function-docstring

import gcontacts.csvpayload
from gcontacts.simplifier import simpler_words
from gcontacts.csvpayload import CPayload
from gcontacts.fields import CFields
from gcontacts.dprint import dprint

class GCards(gcontacts.csvpayload.CContent):
    """ Google card contacts """
    def __init__(self, path:str, name=""):
        super().__init__(path, name)
        self._new = []

    def adapt(self, debug=0):
        """ Adapt ourselves to the 79-list cards """
        self.msgs = []
        if self.cards:
            return False
        self.parse()
        self.items, self._new = [], []
        exp_n = len(self.fields_list)
        if exp_n == CFields().num_fields():
            for card in self.cards:
                self.items.append(CPayload().line_wrap(card))
            return True
        msg = self._adapt(self.fields_list, CFields(), debug)
        if msg:
            self.msgs.append(msg)
            return False
        # Refurbish now cards:
        self.items = self._new
        return True

    def _adapt(self, flist, to_fields, debug=0):
        exp_n = len(flist)
        lens = []
        dprint(
            "Adapting from", exp_n, flist, "; to:", to_fields.num_fields(),
            debug=debug,
        )
        dct = {}
        for idx, card in enumerate(self.cards, 1):
            shown = CPayload().line_wrap(card)
            alen = len(shown)
            dprint(
                idx, f"(len={alen})", simpler_words(shown),
                debug=(int(debug > 0 and idx in (1, len(self.cards)))),
            )
            if alen != exp_n:
                lens.append(("index", idx, "num-fields", alen))
            dct[idx] = shown
        if lens:
            return f"Mixed lens: {lens}"
        self._new = self._run_adapt(flist, to_fields, dct, debug)
        return ""

    def _run_adapt(self, flist, to_fields, dct, debug=0):
        """ Iterate on every card and appending newly, with 79 fields. """
        res = []
        for idx, _ in enumerate(self.cards, 1):
            shown = dct[idx]
            mine = [None] * to_fields.num_fields()
            for k_fld, field in enumerate(shown):
                k_idx, fld_name = flist[k_fld]
                dprint(
                    f"idx={idx}, converting {k_fld+1}={fld_name} as {k_idx}: {simpler_words(field)}",
                    debug=(int(debug > 0 and idx >= len(self.cards))),
                )
                mine[k_idx - 1] = field
            res.append(mine)
        return res
