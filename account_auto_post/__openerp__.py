# -*- coding: utf-8 -*-
{
    'name': 'Account Posting Scheduled Job',
    'version': '1.0',
    'author': 'Ecosoft',
    'summary': 'Account Posting Scheduled Job',
    'description': """
This module will auto post journal entries that has not been posted yet.
To configure, go to menu > Settings > Technical > Scheduler,
then open Account Auto Post

Arguments:
==========
* () --> Post all journals
* ([1,2,3],) --> Post journals with journal_id in (1,2,3)
* ([],[4,5,6],) --> Exclude journals with journal_id in (4,5,6)
    """,
    'category': 'Accounting',
    'website': 'http://www.ecosoft.co.th',
    'images': [],
    'depends': ['account'],
    'demo': [],
    'data': ['data/ir_cron_data.xml'
             ],
    'test': [
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}
