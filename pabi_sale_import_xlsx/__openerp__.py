# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Sales Import XLSX",
    "version": "1.0",
    "description": """
    """,
    "website": "https://ecosoft.co.th/",
    "author": "Ecosoft",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'sale',
        'pabi_utils',
    ],
    "data": [
        'xlsx_template/templates.xml',
        'xlsx_template/xlsx_import_wizard.xml',
        'xlsx_template/load_template.xml',
    ],
}
