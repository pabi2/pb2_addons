# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name' : 'ECOSOFT :: Partner Address in Thai',
    'version' : '1.0',
    'category' : 'Technical Settings',
    'description' : """

Address for Thailand
====================

If country is selected as Thailand, new fields will show up.

* Province (Chanwat)
* District (Amphoe)
* Township (Tambon)

Choosing Township will realize Province, District, and Zip Code

    """,
    'author' : 'Ecosoft',
    'website': 'www.ecosoft.co.th',
    'depends' : ['base'],
    'data': [
        'view/res_country_view.xml',
        'view/res_partner_view.xml',
        'security/ir.model.access.csv',
        'data/res.country.province.csv',
        'data/res.country.district.csv',
        'data/res.country.township.csv',
    ],
    'qweb' : [
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
