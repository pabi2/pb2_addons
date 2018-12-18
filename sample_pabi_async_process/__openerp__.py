# -*- coding: utf-8 -*-
{
    'name': 'Asynchronous Actions (SAMPLE)',
    'version': '8.0.1.0.0',
    'author': 'Kitti U. (Ecosoft)',
    'license': 'AGPL-3',
    'category': 'Generic Modules',
    'depends': [
        'pabi_utils',
        'hr',
        'pabi_import_journal_entries',
        'purchase',
    ],
    'data': [
        # Action Wizard
        'pabi_action_do_something/pabi_process.xml',
        'pabi_action_do_something/pabi_action_do_something.xml',
        # Others
        'action_import_je_split_entries/pabi_process.xml',
        'action_import_je_split_entries/pabi_import_journal_entries.xml',
        # XLSX Report
        'xlsx_report_purchase_order_line/templates.xml',
        'xlsx_report_purchase_order_line/load_template.xml',
        'xlsx_report_purchase_order_line/xlsx_report_purchase_order_line.xml',
        # Import/Export Excel
        'pabi_import_export_sale_order/templates.xml',
        'pabi_import_export_sale_order/load_template.xml',
        'pabi_import_export_sale_order/xlsx_template.xml',
        'pabi_import_export_sale_order/sale_order.xml',
    ],
    'installable': True,
    'application': False,
}
