# -*- coding: utf-8 -*-
{
    'name': 'Skip Due Date on Thai Holidays',
    'version': "8.0.1.0.0",
    'author': 'Ecosoft',
    'summary': '',
    'description': """

Skip Due Date on Thai Holidays
==============================

    - Install Thai Holidays in Calendar.
    - Provides the method to find next working day.

    """,
    'category': 'Tools',
    'sequence': 4,
    'website': 'http://www.ecosoft.co.th',
    'license': 'AGPL-3',
    'depends': ['calendar'],
    'data': [
        'data/res.users.csv',
        'data/calendar.event.csv',
        'security/ir.model.access.csv',
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
