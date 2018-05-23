# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Unitlity Functions",
    "summary": "Common functions",
    "version": "1.0",
    "category": "Tools",
    "description": """

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
        "connector",
    ],
    "data": [
        "security/security_groups.xml",
        "security/security_rule.xml",
        "security/ir.model.access.csv",
        "data/xls_config.xml",
        "data/pabi_process.xml",
        "wizard/export_xlsx_template_wizard.xml",
        "wizard/import_xlsx_template_wizard.xml",
        "views/data_map_view.xml",
        "views/my_job_view.xml",
        "views/my_report_view.xml",
        "views/xlsx_import.xml",
        "views/xlsx_report.xml",
    ],
}
