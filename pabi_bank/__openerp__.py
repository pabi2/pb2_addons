# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Bank Master Data",
    "summary": "",
    "version": "1.0",
    "category": "Hidden",
    "description": """
    """,
    "website": "https://nstda.or.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "depends": [
        'l10n_th_fields',
        'payment_export',
    ],
    "data": [
        # 'translation/ir.translation.csv',  # Error Travis
        'security/ir.model.access.csv',
        'views/res_bank_view.xml',
    ],
    "application": False,
    "installable": True,
}
