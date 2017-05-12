# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Invest Construction Master",
    "summary": "",
    "version": "1.0",
    "category": "Accounting & Finance",
    "description": """
    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "depends": [
        "pabi_base",
        "l10n_th_account",  # use account.period.calendar
        "document_status_history",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/invest_construction_sequence.xml",
        "data/invest_construction_history_rule.xml",
        "views/invest_construction_view.xml",
    ],
    "application": False,
    "installable": True,
}
