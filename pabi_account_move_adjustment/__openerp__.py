# -*- coding: utf-8 -*-
{
    'name': 'Account Move - Adjustment Types',
    'version': '8.0.1.0.0',
    'author': 'Ecosoft',
    'summary': 'Journal Entries Adjustmnet Doctypes',
    'description': """

New Menus

* Journal Adj.Bud.
* Journal Adj.No.Bud.

Note: following are arequiremen for system to properly create analytic line

1. journal line must choose account of user type = Profit & Loss
2. journal line must have analytic account
    (which is normally auto created if Product/Activity selected)
3. journal must have analytic journal, otherwise warning will show.

    """,
    'category': 'Accounting',
    'website': 'http://www.ecosoft.co.th',
    'images': [],
    'depends': [
        'account',
        'account_subscription_enhanced',
        'pabi_account_move_document_ref',
        'pabi_chartfield_merged',
        'pabi_utils',
    ],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'data/journal_data.xml',
        'xlsx_template/templates.xml',
        'xlsx_template/xlsx_template_wizard.xml',
        'xlsx_template/load_template.xml',
        'wizard/create_journal_entry_wizard.xml',
        'wizard/edit_desc.xml',
        'wizard/account_move_change_date_due.xml',
        'views/account_view.xml',
        'views/account_invoice_view.xml',
        'views/account_move_priority_view.xml',
    ],
    'test': [
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
