# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - HR Salary Interface with PABIWeb",
    "summary": "",
    "version": "1.0",
    "category": "Human Resources",
    "description": """
This module focus mainly on creating PDF and submit to Alfresco workflow
    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "hr_salary",
        "pabi_web_config",
        "pabi_utils",
        "account_budget_activity",
    ],
    "data": [
        "security/ir.model.access.csv",
        "xlsx_template/xlsx_template_wizard.xml",
        "xlsx_template/templates.xml",
        "views/hr_salary_view.xml",
    ],
}
