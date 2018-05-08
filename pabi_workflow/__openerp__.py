# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "NSTDA :: PABI2 - Work Flow Configuration",
    "summary": "Work Flow Configuration",
    "version": "8.0.1.0.0",
    "category": "Hidden",
    "description": """

PABI2 - Work Flow Configuration
===============================

PABI2's Configuration work flow Odoo to Alfresco
    * Document Type
    * Level
    * Approval Amount
    * Boss Level Approval
    * Boss Special Level
    * Purchasing unit and responsible person
    * Special amount for Project Manager approval
    * Section Assignment

    """,
    "website": "https://nstda.or.th/",
    "author": "Thapanat S.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "pabi_base",
        "pabi_user_profile",
    ],
    "data": [
        # security
        'security/ir.model.access.csv',
        # views
        'views/wkf_config_base_view.xml',
        'views/wkf_config_boss_view.xml',
        'views/wkf_config_purchase_view.xml',
        'views/wkf_config_project_view.xml',
        'views/res_section_view.xml',
        # 'views/hr_employee_view.xml',
    ],
}
