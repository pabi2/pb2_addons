# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Asset Import Batch",
    "version": "8.0.1.0.0",
    "author": "Ecosoft",
    "website": "http://ecosoft.co.th",
    "category": "Customs Modules",
    "depends": [
        "pabi_asset_management",
        "pabi_account_report",
    ],
    "description": """This module allow import asset batch.""",
    "data": [
        "security/ir.model.access.csv",
        "data/sequence_data.xml",
        "views/asset_import_batch_view.xml",
        "xlsx_template/templates.xml",
        "xlsx_template/load_template.xml",
        "xlsx_template/xlsx_template_wizard.xml",
        "views/asset_export_report.xml",
        "views/asset_view.xml",
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
