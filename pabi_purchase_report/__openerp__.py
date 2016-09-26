# -*- coding: utf-8 -*-

{
    'name': "PABI Purchase Report",
    'summary': "",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Tools',
    'version': '0.1.0',
    'depends': [
        'jasper_reports',
        'pabi_procurement',
    ],
    'data': [
        'pabi_contract_detail/report_data.xml',
        'pabi_contract_detail/wizard/pabi_contract_detail_report_wizard.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
