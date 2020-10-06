# -*- coding: utf-8 -*-
{
    'name': 'Budget Control Management',
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'author': 'Saran Lim.',
    'website': 'http://ecosoft.co.th',
    'depends': [
        'account_budget_activity',
        'pabi_budget_plan',
    ],
    'data': [
        'security/ir.model.access.csv',
        'xlsx_template/templates.xml',
        'xlsx_template/xlsx_template_wizard.xml',
        'xlsx_template/load_template.xml',
        'views/account_budget_init_view.xml',
        'views/account_budget_view.xml',
    ],
    'installable': True,
}
