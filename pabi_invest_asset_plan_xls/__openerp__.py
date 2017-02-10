# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "NSTDA :: PABI2 - Asset Item Import/Export XLS",
    "summary": "Create and maintain asset item from XLS",
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
        'pabi_budget_plan',
    ],
    'external_dependencies': {'python': ['openpyxl']},
    "data": [
        'wizard/output_excel_view.xml',
        'wizard/export_plan_view.xml',
        'views/invest_asset_item_view.xml',
    ],
}
