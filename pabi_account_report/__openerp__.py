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
        'pabi_purchase_billing',
        'pabi_bank_statement_reconcile',
        'pabi_account',
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
        'reports/xlsx_report_payable_detail.xml',
        'reports/xlsx_report_payable_balance.xml',
        'reports/xlsx_report_purchase_billing.xml',
        'reports/xlsx_report_sla_purchase.xml',
        'reports/xlsx_report_sla_employee.xml',
        'reports/xlsx_report_supplier_receipt_follow_up.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
