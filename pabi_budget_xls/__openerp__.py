# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "NSTDA :: PABI2 - Budget Import/Export XLS",
    "summary": "Create and maintain budget plan from XLS",
    "version": "8.0.1.0.0",
    "category": "Accounting & Finance",
    "description": """

    """,
    "website": "https://nstda.or.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,  # Mark uninstallable for now.
    "depends": [
        "account_budget_activity",
        'pabi_budget_plan',
        'pabi_budget_internal_charge',
        'pabi_attachment_helper',
    ],
    'external_dependencies': {'python': ['openpyxl']},
    "data": [
        'security/ir.model.access.csv',
        'wizard/import_unit_based_plan_view.xml',
        'wizard/export_unit_based_plan_view.xml',
        'wizard/export_invest_asset_item_view.xml',
        'wizard/import_invest_asset_item_view.xml',
        'views/budget_plan_history_view.xml',
        "views/budget_plan_view.xml",
        'views/excel_output.xml',
        'views/attachment_view.xml',
    ],
}
