# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Unitlity Functions",
    "summary": "Common functions",
    "version": "1.0",
    "category": "Tools",
    "description": """

This module keeps all the commonly used functions. All with @api.model

Functions
=========

* xls
  * import_xls()
  * xls_to_csv()
  * import_csv()

* interface
  * create_model_data(model, data_dict)

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
        "connector",
    ],
    "data": [
        "security/security_groups.xml",
        "security/security_rule.xml",
        "security/ir.model.access.csv",
        "data/xls_config.xml",
        # "data/queue_data.xml",
        "wizard/export_xlsx_template_wizard.xml",
        "wizard/import_xlsx_template_wizard.xml",
        "views/data_map_view.xml",
        "views/my_report_view.xml",
    ],
}
