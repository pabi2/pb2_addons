# -*- coding: utf-8 -*-
# © 2019 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'NSTDA :: MIS Accounting Financial Reports',
    'version': '8.0.1.0.0',
    'category': 'Reporting',
    'description': """
""",
    'author': 'Saran Lim.',
    'website': 'http://ecosoft.co.th',
    'depends': [
        'mis_builder',
        'pabi_report_xlsx_helper',
    ],
    'data': [
        'data/mis_report_bs.xml',
        'data/mis.report.kpi.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
