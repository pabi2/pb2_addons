# -*- coding: utf-8 -*-
{
    'name': "Account Subscription Enhancemnet",
    'summary': "",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'description': """

This module enhance Define Recurring Enteries window with followings,

* Enhance the compute line, so that it also consider month end. Ensuring that
  all subscription line will end on month end.
* Adding new field with sepcial type = Amount (manual), allowing user to
  manually or by calculation enter the amount in each subscription line.
* With the amount in each line, the recurring journal enteries will use this
  amount instead of what is in the model.

    """,
    'version': '0.1.0',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
