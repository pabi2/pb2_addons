# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "NSTDA :: PABI2 - User Profile",
    "summary": "User profile",
    "version": "8.0.1.0.0",
    "category": "Hidden",
    "description": """

PABI2 - User's profile
======================

Add more user's profile
    * Employee ID.
    * Full Name
    * Org. Structure
    * Master Employee's Position

    """,
    "website": "https://nstda.or.th/",
    "author": "Thapanat S.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "hr_expense",
        "pabi_base",
        "res_partner_ext",
    ],
    "data": [
        # security
        'security/ir.model.access.csv',
        # views
        'views/hr_position_view.xml',
        'views/hr_status_view.xml',
        'views/hr_employee_view.xml',
    ],
}
