# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "NSTDA :: PABI2 - Project Member",
    "summary": "Project Member",
    "version": "8.0.1.0.0",
    "category": "Hidden",
    "description": """

PABI2 - Project Members
=======================
    * Project Member

    """,
    "website": "https://nstda.or.th/",
    "author": "Thapanat S.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "pabi_base",
    ],
    "data": [
        # security
        'security/ir.model.access.csv',
        # views
        'views/res_project_member_view.xml',
    ],
}
