# -*- coding: utf-8 -*
{
    "name": "NSTDA :: PABI2 - Base Master Data",
    "summary": "Organization Structure of NSTDA",
    "version": "8.0.1.0.0",
    "category": "Hidden",
    "description": """

Structure of NSTDA
==================

SPA Structure:
--------------

   (type/tag)      (type/tag)   (type/tag)     (type/tag)    (type/tag)
      (org)           (org)        (org)         (org)         (org)
functional_area -> program_group -> program -> project_group -> project
                                   (spa(s))                   (mission)

ORG Structure:
--------------
org -> sector -> subsector -> division -> section -> costcenter
                                                       (mission)

    """,
    "website": "https://nstda.or.th/",
    "author": "Thapanat S., Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
        "account",
        "operating_unit",
    ],
    "data": [
        # Data
        'data/fund_data.xml',
        'data/project_info_data.xml',
        # security
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        # views
        'views/base_import.xml',
        'views/menu_view.xml',
        'views/res_fund_view.xml',
        'views/res_spa_structure_view.xml',
        'views/res_org_structure_view.xml',
        'views/res_personnel_structure_view.xml',
        'views/res_investment_structure_view.xml',
        'views/res_dimension_view.xml',
        'views/project_info_view.xml',
        'views/product_view.xml',
    ],
    "demo": [
    ]
}
