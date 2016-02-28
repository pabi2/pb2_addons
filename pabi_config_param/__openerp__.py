# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "NSTDA :: PABI2 - System Parameters",
    "summary": "System Parameters for NSTDA",
    "version": "8.0.1.0.0",
    "category": "Uncategorized",
    "description": """

m2x Options
===========

* web_m2x_options.create: False
* web_m2x_options.create_edit: False
* web_m2x_options.m2o_dialog: True
* web_m2x_options.limit: 10
* web_m2x_options.search_more: True

    """,
    "website": "https://nstda.or.th/",
    "author": "Kitit U.,",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "web_m2x_options",
    ],
    "data": [
        "data/config_param.xml",
    ],
}
