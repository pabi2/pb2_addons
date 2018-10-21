# -*- coding: utf-8 -*-
{
    'name': "Bank Account Transfer",
    'author': "Ecosoft",
    'website': "http://www.ecosoft.co.th/",
    'category': 'Accounting & Finance',
    'version': '0.1',
    'depends': [
        'pabi_utils',
        'l10n_th_doctype_base',
    ],
    'data': [
        'data/account_data.xml',
        'data/doctype_data.xml',
        'security/ir.model.access.csv',
        'views/bank_account_transfer_view.xml',
        'xlsx_template/templates.xml',
        'xlsx_template/xlsx_template_wizard.xml',
        'xlsx_template/load_template.xml',
    ],
}
