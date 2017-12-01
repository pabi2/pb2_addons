# -*- coding: utf-8 -*-
{
    'name': 'Asynchronous Actions',
    'version': '8.0.1.0.0',
    'author': 'Kitti U. (Ecosoft)',
    'license': 'AGPL-3',
    'category': 'Generic Modules',
    'depends': [
        'connector',
        'purchase_invoice_plan',
        'pabi_procurement',
        # 'pabi_th_tax_report',
        'account_subscription_enhanced',
        'pabi_hr_salary',
    ],
    'data': [
        'views/my_queue_job_view.xml',
        'action_purchase_create_inovice/create_invoice_view.xml',
        # 'action_run_tax_report/tax_report_wizard.xml',
        'action_generate_entries/account_subscription_generate_view.xml',
        'action_open_hr_salary/hr_salary_view.xml',
    ],
    'installable': True,
    'application': False,
}
