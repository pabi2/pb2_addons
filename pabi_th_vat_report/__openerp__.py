# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Vat Report Extended",
    "summary": "",
    "version": "1.0",
    "category": "",
    "description": """
Vat Report By TaxBranch
    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'pabi_account',
        'l10n_th_vat_report',
    ],
    "data": [
        "wizard/vat_report_wiz_view.xml",
        "report/vat_report_view.xml",
    ],
}
