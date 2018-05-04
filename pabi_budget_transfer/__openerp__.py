# -*- coding: utf-8 -*-
{
    'name': "NSTDA :: PABI2 Budget Transfer",
    'summary': "",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'version': '0.1.0',
    'depends': [
        'account_budget_activity',
        'pabi_chartfield',
        'account_auto_fy_sequence',
    ],
    'data': [
        # 'security/rule_section_budget_transfer.xml',
        'security/ir.model.access.csv',
        'data/section_transfer_data.xml',
        'data/sequence.xml',
        'views/section_budget_transfer_view.xml',
        'views/account_budget_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
