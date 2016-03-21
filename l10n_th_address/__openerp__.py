# -*- coding: utf-8 -*-

{
    'name': 'ECOSOFT :: Partner Address in Thai',
    'version': '1.0',
    'category': 'Technical Settings',
    'description': """

Address for Thailand
====================

If country is selected as Thailand, new fields will show up.

* Province (Chanwat)
* District (Amphoe)
* Township (Tambon)

Choosing Township will realize Province, District, and Zip Code

    """,
    'author': 'Ecosoft',
    'website': 'www.ecosoft.co.th',
    'depends': ['base'],
    'data': [
        'views/res_country_view.xml',
        'views/res_partner_view.xml',
        'security/ir.model.access.csv',
        'data/res.country.province.csv',
        'data/res.country.district.csv',
        'data/res.country.township.csv',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
