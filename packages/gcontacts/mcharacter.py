# -*- coding: utf-8 -*-
#
# (c)2024  Henrique Moreira

""" mcharacter -- MCard helper for main characteristics

Author: Henrique Moreira
"""

# pylint: disable=missing-function-docstring

import gcontacts.mcard
from gcontacts.fields import FieldsIndex

singleton_fi = FieldsIndex()


class MainCard(gcontacts.mcard.MCard):
    """ MCard main characteristicst """
    def __init__(self, obj=None, name=""):
        """ Init. card """
        super().__init__(name=name)
        self.names = []
        self.nicks = {}
        self.phones, self.phones_pri = [], []
        if obj is None:
            self.data = []
        else:
            self._init_from_obj(obj)

    def _init_from_obj(self, obj):
        if self.name == "?":
            self.name = obj.name
        self.names = obj.data[:4]
        self.data = obj.data
        for key in singleton_fi.bynick:
            vals = [idx - 1 for idx in singleton_fi.bynick[key] if idx > 0]
            nlist = []
            for fld in vals:
                astr = heal(self.data[fld], key)
                if astr:
                    nlist.append(astr)
            # A phone contact can have ':::' to separate multiple ones
            self.nicks[key] = nlist
        # Phones, specifically, ordered by importance
        for fld in singleton_fi.bynick["Phone"]:
            astr = heal(self.data[fld - 1])
            for single in astr.split(":::"):
                new = heal(single)
                if new:
                    self.phones.append(new)
                    self.phones_pri.append(fld - fix.byname["Phone1Value"] + 1)
        return True

def heal(astr, kind="P"):
    kind = kind[0]
    assert isinstance(kind, str)
    res = astr.strip()
    new = ''.join(res.split(" "))
    if kind in "P":
        ign = singleton_fi.ignore_pre[0] if singleton_fi.ignore_pre else ""
        if ign and new.startswith(ign):
            new = new[len(ign):]
    return new
