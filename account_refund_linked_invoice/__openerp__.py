# -*- coding: utf-8 -*-

#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

{
    'name': 'Refund With Invoice linked',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'description': """
        This modules based on V7 of account_refund_linked_invoice,
        but has been updated to V8

        * Adds a field in the refund to be able to find which
        is the linked invoice.
        * Adds new Refunded Amount field on original invoice.
        * Disallow creating of refund if refunded amount exceed
        the original invoice.

    """,
    'author': 'Julius Network Solutions, Ecosoft',
    'website': 'http://www.julius.fr, http://ecosoft.co.th',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_invoice_view.xml',
    ],
    'demo': [],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
