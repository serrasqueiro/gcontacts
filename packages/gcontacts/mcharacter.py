# -*- coding: utf-8 -*-
#
# (c)2024  Henrique Moreira

""" mcharacter -- MCard helper for main characteristics

Author: Henrique Moreira
"""

# pylint: disable=missing-function-docstring

import re
import os.path
import gcontacts.mcard
from gcontacts.fields import FieldsIndex
from gcontacts.dprint import dprint

singleton_fi = FieldsIndex()


class CardSeq(gcontacts.mcard.MCard):
    """ Sequence of cards. """
    def __init__(self, cards=None, outdir="", name=""):
        """ Initializer """
        assert isinstance(outdir, str)
        super().__init__(name=name)
        self._outdir = outdir
        lst = cards.data if cards else []
        self.data = [
            MainCard(crd) for crd in lst
        ]
        self.mlist = []
        self.nick2index = {}
        self._init_rest()
        self.outs = self._my_outs(outdir)

    def get_bynick(self, astr):
        if isinstance(astr, str):
            nick = '+'.join(astr.split(" "))
        else:
            nick = '+'.join(astr)
        hit = self.nick2index.get(nick)
        return [] if hit is None else hit

    def write_outs(self):
        for key in sorted(self.outs):
            outname, head = self.outs[key]
            seq = self._what_output(key, outname, head)
            with open(outname, "wb") as fdout:
                fdout.write(bytes(head + "\n", "ascii"))
                for line in seq:
                    fdout.write(bytes(line + "\n", "ascii"))
        return True

    def _what_output(self, key, outname, head):
        """ Calculate and write output """
        res = []
        if key != "phone":
            return []
        dphone_who, dphone_eql = {}, {}
        dphone_sqz = {}
        for mcard in self.mlist:
            nick = mcard.nick.replace("+", " ")
            for phone in mcard.phones:
                if phone in dphone_who:
                    dphone_who[phone].append(nick)
                else:
                    dphone_who[phone] = [nick]
                eqs = mcard.d_phones["original"][phone]
                if phone in dphone_eql:
                    dphone_eql[phone] = sorted(
                        list(set(dphone_eql[phone] + eqs))
                    )
                else:
                    dphone_eql[phone] = eqs
                    if phone not in dphone_sqz:
                        dphone_sqz[phone] = mcard.d_phones["squeezed"][phone][0]
        for phone in sorted(dphone_eql):
            nick = dphone_who[phone][0]	# only the first
            eqs = dphone_eql[phone]
            rphone = dphone_sqz[phone]
            for one in eqs:
                lst = [phone, one, rphone, nick]
                #print("##", lst)
                astr = '\t'.join(lst)
                res.append(astr)
        return res

    def _init_rest(self, debug=0):
        dct = {}
        self.mlist = []
        for idx, mcard in enumerate(self.data):
            grp = mcard.groups()
            dprint(
                mcard.name, mcard.nicks["Phone"],
                grp,
                debug=debug,
            )
            self.mlist.append(mcard)
            if mcard.nick in dct:
                dct[mcard.nick].append(idx)
            else:
                dct[mcard.nick] = [idx]
        self.nick2index = dct

    def _my_outs(self, outdir):
        outs = {
            "phone": (
                os.path.join(outdir, "txt-phone.csv"),
                '\t'.join(
                    ("#p-phone", "phone", "r-phone", "nick")
                ),
            ),
        }
        return outs


class MainCard(gcontacts.mcard.MCard):
    """ MCard main characteristicst """
    def __init__(self, obj=None, name=""):
        """ Init. card """
        super().__init__(name=name)
        initialize_regexp(singleton_fi)
        self.names = []
        self.nick, self.nicks = "", {}
        self.phones, self.phones_pri = [], []
        self.d_phones = {
            "original": {},
            "squeezed": {},	# No blanks
        }
        self._groups = []
        if obj is None:
            self.data = []
        else:
            self._init_from_obj(obj)

    def groups(self):
        """ Return GroupMembership list """
        return self._groups

    def _init_from_obj(self, obj, fix=None):
        if fix is None:
            fix = singleton_fi	# Fixed fields singleton
        if self.name == "?":
            self.name = obj.name
        self.names = obj.data[:4]
        self.data = obj.data
        self.nick = obj.nick
        for key in fix.bynick:
            vals = [idx - 1 for idx in fix.bynick[key] if idx > 0]
            nlist = []
            for fld in vals:
                astr = heal(self.data[fld], key)
                if astr:
                    nlist.append(astr)
            # A phone contact can have ':::' to separate multiple ones
            self.nicks[key] = nlist
        # Phones, specifically, ordered by importance
        for fld in fix.bynick["Phone"]:
            s_value = self.data[fld - 1]
            astr = heal(s_value)
            for single in astr.split(":::"):
                new = heal(single)
                if not new:
                    continue
                self.phones.append(new)
                self.phones_pri.append(fld - fix.byname["Phone1Value"] + 1)
            for single in s_value.split(":::"):
                new = heal(single, "R")
                self._update_phones(heal(single), single.strip(), new)
        self._groups = self._get_groups(
            self.data[fix.byname["GroupMembership"] - 1]
        )
        return True

    def _update_phones(self, new, single, sqz):
        """ Fill in 'd_phones' dictionaries """
        if not new:
            return False
        if new not in self.d_phones["original"]:
            self.d_phones["original"][new] = []
        if new not in self.d_phones["squeezed"]:
            self.d_phones["squeezed"][new] = []
        self.d_phones["original"][new].append(single)
        self.d_phones["squeezed"][new].append(sqz)
        return True

    def _get_groups(self, astr):
        """ Returns paired list of group membership """
        if not astr:
            astr = singleton_fi.members["* myContacts"][1]
        paired1, paired2 = [], []
        for words in astr.split(":::"):
            this = heal(words, "G")
            if not this:
                continue
            if this in singleton_fi.members:
                grp = singleton_fi.members[this]
                paired1.append(list(grp))
            else:
                paired2.append([0, this])
        soma = sorted(paired1, key=lambda x: x[0]) + paired2
        return soma

def initialize_regexp(fix):
    """ Entered and updated singleton ('fix') """
    s_reg = fix.my_phone_regexp
    if not s_reg:
        return False
    rexp = re.compile(s_reg)	# compiled regexp
    fix.my_phone_regcomp = rexp
    return True

def heal(astr, kind="P", use_rmatch=True):
    """ P: Phone,
	Q: Phone, do not ignore blanks
	R: Phone, maybe with prefix (but stripped blanks)
	G: Group,
    """
    kind = kind[0]
    assert isinstance(kind, str)
    res = astr.strip()
    if kind == "Q":
        return res
    if kind == "G":
        new = res
    else:
        new = ''.join(res.split(" "))
    if kind in "P":
        if not new:
            return new
        if new[0] == "*":
            return new
        ign = singleton_fi.ignore_pre[0] if singleton_fi.ignore_pre else ""
        if ign and new.startswith(ign):
            new = new[len(ign):]
            return new
        if not use_rmatch:
            return new
        rxr = re.match(singleton_fi.my_phone_regcomp, new)
        if rxr:
            new = ''.join(
                [ala.strip().replace("-", "") for ala in rxr.groups() if ala]
            )
    return new
