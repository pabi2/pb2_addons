# -*- coding: utf-8 -*-
{
    'name': "Pabi Data Mart",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'pabi_account_move_document_ref',
        'pabi_utils',
    ],
    'data': [
        'xlsx_template/templates.xml',
        'xlsx_template/load_template.xml',
        'security/ir.model.access.csv',
        'reports/xlsx_report_account_move.xml',
    ],
}
