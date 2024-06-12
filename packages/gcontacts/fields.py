# -*- coding: utf-8 -*-
#
# (c)2024  Henrique Moreira

""" fields -- from google contacts

Author: Henrique Moreira
"""

# pylint: disable=missing-function-docstring

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


class CFields():
    """ Contacts fields in Google csv """
    # pylint: disable=line-too-long, anomalous-backslash-in-string
    def __init__(self, alist=None, name=""):
        """ Fields taken from
		head -1 contacts.csv | tr , \\012 | sed 's/ //g;s/-//g' | grep -n . | sed 's/\(.*\):\(.*\)/    \1 : "\2",/'
        """
        self.name = name if name else "?"
        self.fields = CFields._get_fields(DEF_FIELDS) if alist is None else []
        self.byname = self._dict_byname()

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
