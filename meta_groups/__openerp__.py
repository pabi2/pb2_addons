# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'license': 'LGPL-3',
    "name" : "Meta Groups",
    "version" : "1.0",
    "author" : "Jakkrich.Cha",
    'category': 'Security',
    "summary": "Faster assignment of security groups (Bista).",
    'description': """
For Odoo Version 8.0(Contvert Version 1.0 to Version 8.0), this module allows you to create a Meta Group ('Group of Groups') to more efficiently assign users to the Application 
level groups.

For example, a Meta Group 'Inside Sales' can be created with the relevant Sales, Inventory, Purchasing, Accounting and Helpdesk group permission levels.

Assigning permissions to a new Inside Salesperson is as simple as adding them to a single Meta Group - they are added to the predefined groups 
automatically!
""",

    'maintainer': "Bista Solutions",
    'website': 'http://www.bistasolutions.com/erp-implementation-company/erp-customization-company',
    "depends" : ["base"],
    "init_xml" : [],
    "demo_xml" : [],
    "data" : [
        'views/access_right_view.xml',
        'wizard/access_rights_wizard_view.xml',
    ],
    "test" : [
    ],
    "auto_install": False,
    "application": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
