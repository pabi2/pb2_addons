# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Trial Balance Extension for GFMIS",
    "summary": "",
    "version": "1.0",
    "category": "Human Resources",
    "description": """
Add ability to export Trial Balance with mapped account for GFMIS as xlsx
    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account_trial_balance_report",
        "pabi_utils",
    ],
    "data": [
        'security/ir.model.access.csv',
        "xlsx_template/xlsx_template_wizard.xml",
        "xlsx_template/templates.xml",
        "xlsx_template/load_template.xml",
        "data/pabi.data.map.type.csv",
        "data/pabi.data.map.csv",
        "views/account_view.xml",
        "views/trial_balance_report_view.xml",
    ],
}
