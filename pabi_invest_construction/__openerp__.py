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
        "account_budget_activity",
        "pabi_budget_plan_monitor",  # Get prev fy from monitor report
        "l10n_th_account",  # use account.period.calendar
        "document_status_history",
        "pabi_utils",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/invest_construction_sequence.xml",
        "data/invest_construction_history_rule.xml",
        "wizard/project_close_phase_wizard.xml",
        "wizard/project_plan_report.xml",
        "views/invest_construction_view.xml",
        "views/account_budget_view.xml",
    ],
    "application": False,
    "installable": True,
}
