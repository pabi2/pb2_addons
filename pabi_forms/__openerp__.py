# -*- coding: utf-8 -*-

{
    'name': 'NSTDA :: PABI2 - Forms',
    'version': '8.0.1.0.0',
    'author': 'Ecosoft',
    'website': 'http://ecosoft.co.th',
    'depends': [
        'jasper_reports',
        'hr',
        'l10n_th_amount_text_ext',
        'l10n_th_fields',
        'pabi_account',
        'purchase_invoice_line_percentage',
        'purchase_invoice_plan',
    ],
    'data': [
        "jasper_data.xml",
        # 'template.xml',
        'qweb_reports/report_layout.xml',
        'qweb_reports/report_invoice.xml',
        'qweb_reports/report_payment.xml',
        'qweb_data.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
