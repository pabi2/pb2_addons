# -*- coding: utf-8 -*-
{
    "name": "Prepare data for Budget UAT",
    "summary": "",
    "category": "Tools",
    "description": """
    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'base',
        'pabi_procurement',
        'pabi_hr_expense',
    ],
    "data": [
        'test_fund_rule_data/res.project.csv',
        'test_fund_rule_data/res.project.budget.plan.csv',
    ],
}
