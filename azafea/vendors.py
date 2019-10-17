# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


# The following is a mapping of vendors to try and keep the data normalized.
#
# Keys must be lower case.
#
# Please keep this sorted by value, then by key, with an empty line between each group.
MAPPING = {
    "acer": "Acer",
    "acer inc.": "Acer",
    "acer, inc.": "Acer",

    "aldo": "ALDO COMPONENTES ELETRONICOS",
    "aldo componentes eletronicos ltda": "ALDO COMPONENTES ELETRONICOS",

    "apple computer, inc.": "Apple",
    "apple inc.": "Apple",

    "asus": "ASUS",
    "asus_flash": "ASUS",
    "asustek computer inc": "ASUS",
    "asustek computer inc.": "ASUS",

    "axioo": "AXIOO",

    "bangho": "Bangho",

    "bgh e-nova": "BGH",

    "Biostar": "BIOSTAR",
    "biostar group": "BIOSTAR",

    "casper bilgisayar sistemleri a.s": "Casper",
    "casper bilgisayar sistemleri a.s.": "Casper",
    "casper bilgisayar sistemleri.a.s": "Casper",
    "casper bilgisayar sistemleri.a.s.": "Casper",

    "centrium": "Centrium",

    "clevo": "CLEVO",
    "clevo co.": "CLEVO",

    "compal": "Compal",

    "compaq": "COMPAQ",
    "compaq presario 061": "COMPAQ",
    "compaq-presario": "COMPAQ",
    "compaq-presario 061": "COMPAQ",

    "compumax": "Compumax",
    "compumax computer": "Compumax",
    "compumax computer s.a.s": "Compumax",
    "compumax computer s.a.s.": "Compumax",

    "coradir s.a": "CORADIR",
    "coradir s.a.": "CORADIR",

    "daten": "Daten",
    "daten technologia": "Daten",
    "daten tecnologia": "Daten",
    "daten tecnologia ltda": "Daten",
    "daten tecnologia ltda.": "Daten",

    "dell inc": "Dell",
    "dell inc.": "Dell",

    "digibras": "Digibras",
    "digibras ind. do brasil": "Digibras",

    "digitron": "Digitron",

    "emachines": "eMachines",
    "emachines, inc.": "eMachines",

    "endless": "Endless",

    "foxconn": "Foxconn",

    "gateway": "Gateway",

    "gigabyte technology co., ltd.": "GIGA-BYTE",
    "gigabyte tecohnology co., ltd.": "GIGA-BYTE",
    "gigabyte": "GIGA-BYTE",

    "google": "Google",

    "haier information technology (su zhou) co., ltd": "Haier",
    "haiercomputer": "Haier",

    "hewlett-packard": "HP",
    "hp-pavilion": "HP",
    "hp pavilion 061": "HP",

    "intel": "Intel",
    "intel corp.": "Intel",
    "intel corporation": "Intel",

    "corporativo lanix s.a de c.v": "Lanix",
    "corporativo lanix s.a de c.v.": "Lanix",
    "corporativo lanix s.a. de c.v.": "Lanix",
    "corporativo lanix, s.a. de c.v": "Lanix",
    "corporativo lanix, s.a. de c.v.": "Lanix",
    "lanis": "Lanix",
    "lanix": "Lanix",
    "lanix todos los derechos reservados": "Lanix",

    "lenovo": "Lenovo",
    "lenovo product": "Lenovo",

    "lg electronics": "LG",
    "lg electronics inc.": "LG",

    "medion": "MEDION",

    "microsoft corporation": "Microsoft",

    "micro-star int'l co., ltd.": "MSI",
    "micro-star int'l co.,ltd.": "MSI",
    "micro-star interantional co.,ltd": "MSI",
    "micro-star interantonal co.,ltd": "MSI",
    "micro-star international": "MSI",
    "micro-star international co., ltd": "MSI",
    "micro-star international co., ltd.": "MSI",
    "micro-star international co.,ltd": "MSI",

    "packard bell bv": "Packard Bell",

    "pegatron": "PEGATRON",
    "pegatron computer inc.": "PEGATRON",
    "pegatron corporation": "PEGATRON",

    "desenvolvido para positivo informatica": "POSITIVO",
    "desenvolvido para positivo informatica s/a": "POSITIVO",
    "positivo": "POSITIVO",
    "positivo informatica ltda": "POSITIVO",
    "positivo informatica s/a": "POSITIVO",
    "positivo informatica sa": "POSITIVO",
    "positivo tecnologia sa": "POSITIVO",

    "qbex electronics corp.": "QBEX",

    "samsung": "Samsung",
    "samsung electronics co.,ltd": "Samsung",
    "samsung electronics co., ltd.": "Samsung",

    "semp toshiba informatica ltda": "Semp Toshiba",

    "shuttle": "Shuttle",
    "shuttle inc": "Shuttle",

    "sony corporation": "Sony",

    "system76": "System76",
    "system76, inc": "System76",
    "system76, inc.": "System76",

    "thomson computing": "Thomson",

    "topstar corporation": "Topstar",
    "topstar corporationine trail - m crb": "Topstar",

    "trekstor": "TREKSTOR",

    "trigem computer, inc": "TriGem",
    "trigem computer, inc.": "TriGem",
    "trigem computer,inc.": "TriGem",

    "tsinghua tongfang co., ltd": "TSINGHUA TONGFANG",
    "tsinghua tongfang co.,ltd": "TSINGHUA TONGFANG",

    "tuxedo computers": "TUXEDO",

    "vaio corporation": "VAIO",

    "viewsonic corp.": "ViewSonic",
    "viewsonic corporation": "ViewSonic",

    "vinga twizzle j116": "VINGA",

    # TODO: Should we keep "Innotek"?
    "innotek gmbh": "VirtualBox",

    "vmware, inc.": "VMware",

    "winfast": "WinFast",

    "wipro": "Wipro",

    "wortmann": "WORTMANN",
    "wortmann ag": "WORTMANN",
    "wortmann_ag": "WORTMANN",

    "zmax": "Zmax",
    "zmax computadores": "Zmax",
    "zmax013520010213": "Zmax",
    "zmaxpc": "Zmax",

    "zyrex": "Zyrex",
    "zyrex computer": "Zyrex",
    "zyrex computer system": "Zyrex",
    "zyrex computer systems": "Zyrex",

    # Keep all the "unknown" vendors last
    "-": "unknown",
    "---": "unknown",
    ".": "unknown",
    "...............": "unknown",
    "_": "unknown",
    "default string": "unknown",
    "empty": "unknown",
    "invalid": "unknown",
    "n/a": "unknown",
    "none": "unknown",
    "o.e.m": "unknown",
    "odm": "unknown",
    "oem": "unknown",
    "oem pc": "unknown",
    "standard": "unknown",
    "stem manufacturer": "unknown",
    "system manufacter": "unknown",
    "system manufacturer": "unknown",
    "to be filled by oem": "unknown",
    "to be filled by o.e.m": "unknown",
    "to be filled by o.e.m.": "unknown",
    "unbranded": "unknown",
    "unknow": "unknown",
    "unknown": "unknown",
    "xxxxxx": "unknown",
}


def normalize_vendor(vendor: str) -> str:
    return MAPPING.get(vendor.lower(), vendor)
