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
        'pabi_purchase_work_acceptance',
        'pabi_asset_management',
    ],
    'data': [
        'views/pabi_purchase_report_view.xml',
        'pabi_contract_detail/report_data.xml',
        'pabi_contract_detail/security/ir.model.access.csv',
        'pabi_contract_detail/wizard/pabi_contract_detail_report_wizard.xml',
        'pabi_monthly_work_acceptance/report_data.xml',
        'pabi_monthly_work_acceptance/security/ir.model.access.csv',
        'pabi_monthly_work_acceptance/wizard/'
        'pabi_monthly_work_acceptance_report_wizard.xml',
        'pabi_purchase_summarize/report_data.xml',
        'pabi_purchase_summarize/security/ir.model.access.csv',
        'pabi_purchase_summarize/wizard/'
        'pabi_purchase_summarize_report_wizard.xml',
        'pabi_supplier_evaluation/report_data.xml',
        'pabi_supplier_evaluation/security/ir.model.access.csv',
        'pabi_supplier_evaluation/wizard/'
        'pabi_supplier_evaluation_report_wizard.xml',
        'pabi_supplier_summarize/report_data.xml',
        'pabi_supplier_summarize/security/ir.model.access.csv',
        'pabi_supplier_summarize/wizard/'
        'pabi_supplier_summarize_report_wizard.xml',
        'pabi_stock_card/report_data.xml',
        'pabi_stock_card/security/ir.model.access.csv',
        'pabi_stock_card/wizard/pabi_stock_card_report_wizard.xml',
        'pabi_stock_card_for_accounting/report_data.xml',
        'pabi_stock_card_for_accounting/security/ir.model.access.csv',
        'pabi_stock_card_for_accounting/wizard/'
        'pabi_stock_card_for_accounting_report_wizard.xml',
        'pabi_fixed_asset_non_standard_report/report_data.xml',
        'pabi_fixed_asset_non_standard_report/security/ir.model.access.csv',
        'pabi_fixed_asset_non_standard_report/wizard/'
        'pabi_fixed_asset_non_standard_report_wizard.xml',
        'pabi_fixed_asset_standard_report/report_data.xml',
        'pabi_fixed_asset_standard_report/security/ir.model.access.csv',
        'pabi_fixed_asset_standard_report/wizard/'
        'pabi_fixed_asset_standard_report_wizard.xml',
        # 'pabi_yearly_purchase/report_data.xml',
        # 'pabi_yearly_purchase/wizard/pabi_yearly_purchase_report_wizard.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
