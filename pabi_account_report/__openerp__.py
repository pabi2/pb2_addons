# -*- coding: utf-8 -*-
{
    'name': 'NSTDA :: Accounting Reports',
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'description': """
""",
    'author': 'Kitti U.',
    'website': 'http://ecosoft.co.th',
    'depends': [
        'payment_export',
        'pabi_purchase_contract',
        'pabi_utils',
    ],
    'data': [
        'data/menu.xml',
        'xlsx_template/templates.xml',
        'xlsx_template/load_template.xml',
        # Reports
        'reports/xlsx_report_partner_list.xml',
        'reports/xlsx_report_partner_detail.xml',
        'reports/xlsx_report_advance_status.xml',
        'reports/xlsx_report_supplier_invoice_detail.xml',
        'reports/xlsx_report_cheque_register.xml',
        'reports/xlsx_report_purchase_contract.xml',
        'reports/xlsx_report_advance_payment.xml',
        'reports/xlsx_report_payable_balance.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
