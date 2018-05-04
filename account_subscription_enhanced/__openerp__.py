# -*- coding: utf-8 -*-
{
    'name': "Account Subscription Enhancement",
    'summary': "",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'description': """

This module enhance Define Recurring Entries window with followings,

* Enhance the compute line, so that it also consider month end. Ensuring that
  all subscription line will end on month end.
* Adding new field with sepcial type = Amount (manual), allowing user to
  manually or by calculation enter the amount in each subscription line.
* With the amount in each line, the recurring journal entries will use this
  amount instead of what is in the model.

* Model Type, and Generate Entries by Model Type

    """,
    'version': '0.1.0',
    'depends': [
        'account',
        'account_reversal',
        'l10n_th_account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/account_data.xml',
        'views/account_view.xml',
        'wizard/account_subscription_generate_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
