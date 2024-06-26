# -*- coding: utf-8 -*-
#
# (c)2024  Henrique Moreira

""" fields -- from google contacts

Author: Henrique Moreira
"""

# pylint: disable=missing-function-docstring

F_IDX_VERSION = "1.00"

DEF_FIELDS = {
    1 : "Name",
    2 : "GivenName",
    3 : "AdditionalName",
    4 : "FamilyName",
    5 : "YomiName",
    6 : "GivenNameYomi",
    7 : "AdditionalNameYomi",
    8 : "FamilyNameYomi",
    9 : "NamePrefix",
    10 : "NameSuffix",
    11 : "Initials",
    12 : "Nickname",
    13 : "ShortName",
    14 : "MaidenName",
    15 : "FileAs",
    16 : "Birthday",
    17 : "Gender",
    18 : "Location",
    19 : "BillingInformation",
    20 : "DirectoryServer",
    21 : "Mileage",
    22 : "Occupation",
    23 : "Hobby",
    24 : "Sensitivity",
    25 : "Priority",
    26 : "Subject",
    27 : "Notes",
    28 : "Language",
    29 : "Photo",
    30 : "GroupMembership",
    31 : "Email1Type",
    32 : "Email1Value",
    33 : "Email2Type",
    34 : "Email2Value",
    35 : "IM1Type",
    36 : "IM1Service",
    37 : "IM1Value",
    38 : "Phone1Type",
    39 : "Phone1Value",
    40 : "Phone2Type",
    41 : "Phone2Value",
    42 : "Phone3Type",
    43 : "Phone3Value",
    44 : "Phone4Type",
    45 : "Phone4Value",
    46 : "Phone5Type",
    47 : "Phone5Value",
    48 : "Address1Type",
    49 : "Address1Formatted",
    50 : "Address1Street",
    51 : "Address1City",
    52 : "Address1POBox",
    53 : "Address1Region",
    54 : "Address1PostalCode",
    55 : "Address1Country",
    56 : "Address1ExtendedAddress",
    57 : "Address2Type",
    58 : "Address2Formatted",
    59 : "Address2Street",
    60 : "Address2City",
    61 : "Address2POBox",
    62 : "Address2Region",
    63 : "Address2PostalCode",
    64 : "Address2Country",
    65 : "Address2ExtendedAddress",
    66 : "Organization1Type",
    67 : "Organization1Name",
    68 : "Organization1YomiName",
    69 : "Organization1Title",
    70 : "Organization1Department",
    71 : "Organization1Symbol",
    72 : "Organization1Location",
    73 : "Organization1JobDescription",
    74 : "Relation1Type",
    75 : "Relation1Value",
    76 : "Website1Type",
    77 : "Website1Value",
    78 : "CustomField1Type",
    79 : "CustomField1Value",
}

DEF_GRP_MEMBERSHIP = {
    "* starred": (1, "star"),
    "* myContacts": (2, "contacts"),
    "* friends": (3, "friends"),
}

COUNTRY_PREFIXES = {
    "+1": "US",
    "+351": "Portugal",
    "+44": "UK",
    "+49": "Germany",
}

COUNTRY_IGNORE = (
    "+351",
)

PHONE_REGEXP_US = '^(\+\d{1,3}\s?)?\(?(\d{2,3})\)?[\s.-]?(\d{3}[\s.-]?\d{4})$'

PHONE_REGEXP_WW = '^(\+\d{1,3}\s?)?\(?(\d{2,3})\)?\s?(\d{3}\s?\d{4})$'


class CGeneric():
    """ Generic class """
    def __init__(self, name=""):
        """ Generic initializer """
        self.name = name if name else "?"

    def __str__(self):
        return self.name

    def __repr__(self):
        return repr(self.name)


class CFields(CGeneric):
    """ Contacts fields in Google csv """
    # pylint: disable=line-too-long, anomalous-backslash-in-string
    def __init__(self, alist=None, name=""):
        """ Fields taken from
		head -1 contacts.csv | tr , \\012 | sed 's/ //g;s/-//g' | grep -n . | sed 's/\(.*\):\(.*\)/    \1 : "\2",/'
        """
        super().__init__(name=name)
        self.fields = CFields._get_fields(DEF_FIELDS) if alist is None else []
        self.byname = self._dict_byname()

    def num_fields(self) -> int:
        anum = len(self.fields)
        assert anum > 10, self.name
        return anum

    def splash(self) -> str:
        """ Returns the first line, comma separated """
        astr = ",".join(self.fields)
        return astr

    def _dict_byname(self) -> dict:
        """ Returns the dictionary of field-name and (usual) index. """
        dct = {}
        for idx, name in enumerate(self.fields, 1):
            dct[name] = idx
        return dct

    @staticmethod
    def _get_fields(dct):
        res = [dct[key] for key in sorted(dct)]
        return res


class FieldsIndex(CGeneric):
    """ Fields indexing """
    def __init__(self, name=""):
        super().__init__(FieldsIndex.dormant_nicks()[1])
        self.byname, self.bykey = {}, {}
        self.bynick = {
            "Phone": [],
            "Email": [],
        }
        self._fi_version = self.name
        self._listed, self._unlisted = [], []
        self._my_fields = DEF_FIELDS
        self._initialize(self._my_fields)
        self.ignore_pre = self._international(
            COUNTRY_PREFIXES, COUNTRY_IGNORE
        )
        self.members = DEF_GRP_MEMBERSHIP
        self.phone_regexp = {
            "us": PHONE_REGEXP_US,
            "ww": PHONE_REGEXP_WW,
        }
        self.my_phone_regexp = self.phone_regexp["us"]
        self.my_phone_regcomp = None

    def listed(self) -> list:
        """ Returns the indexes of the used fields. """
        return [anum for anum, _ in self._listed]

    def unlisted(self) -> list:
        """ Returns the indexes of the dormant (unused) fields. """
        return [anum for anum, _ in self._unlisted]

    def _initialize(self, fields):
        used, unused, nums = [], [], []
        for idx, key in enumerate(sorted(fields), 1):
            name = fields[key]
            is_dormant = self._got_dormant(idx, name, unused)
            if is_dormant:
                continue
            self.byname[name] = idx
            used.append((idx, name))
            if name.count("1") == 1:
                nums.append(name)
        self.bykey = {}
        for name in nums:
            akey = name.replace("1", "")
            self.bykey[akey] = [name]
            for anum in range(2, 10):
                key = name.replace("1", str(anum))
                if key not in self.byname:
                    continue
                self.bykey[akey].append(key)
        self._listed, self._unlisted = used, unused
        self._hash_nicks(sorted(self.bynick))

    def _hash_nicks(self, keys):
        for key in keys:
            name = f"{key}Value"	# e.g. 'PhoneValue'
            if name not in self.bykey:
                continue
            res = []
            for field in self.bykey[name]:
                res.append(self.byname[field])
            self.bynick[key] = res

    def _got_dormant(self, idx, name, unused) -> bool:
        for dmnt in FieldsIndex.dormant_nicks()[0]:
            if dmnt in name:
                unused.append((idx, name))
                return True
        return False

    def _international(self, dct_prefix, ignored):
        res = []
        if not ignored:
            return res
        for pre in ignored:
            if pre in dct_prefix:
                assert pre[0] == "+", pre
                res.append(pre)
        return res

    @staticmethod
    def dormant_nicks():
        lst = (
            "Yomi",
            "Initials", "Nickname", "MaidenName",
            "Billing",		# 'BillingInformation'
            "Directory",	# 'DirectoryServer'
            "Mileage", "Priority",
            "Subject", "Relation", "CustomField",
        )
        return lst, F_IDX_VERSION
