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
        'web_widget_x2many_2d_matrix',
        'pabi_budget_plan',
    ],
    "data": [
        'security/ir.model.access.csv',
        'wizard/budget_import_wiz_view.xml',
        'wizard/budget_export_wiz_view.xml',
        "views/account_budget_view.xml",
        'views/output_xls_report.xml',
        'views/attachment_view.xml'
    ],
}
