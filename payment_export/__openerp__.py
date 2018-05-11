# -*- coding: utf-8 -*-
{
    "name": "Payment Export Pack",
    "version": "8.0.0.1.0",
    "license": 'AGPL-3',
    "author": "Ecosoft",
    "category": "Accounting & Finance",
    "depends": [
        "account_voucher",
        "l10n_th_fields",
        "base_document_export",
        "pabi_source_document",  # Use this for field invoice_source_documents
        # "pabi_name_search",
        "pabi_attachment_helper",
    ],
    "description": """

    """,
    "data": [
        "data/payment_export_sequence.xml",
        "data/config_parameter.xml",
        # "export_template/document.export.config.csv",# It will be duplicated
        "security/ir.model.access.csv",
        "views/account_view.xml",
        "wizard/cancel_reason_view.xml",
        "wizard/update_date_cheque_received.xml",
        "views/payment_export_view.xml",
        "views/cheque_lot_view.xml",
        "views/voucher_payment_receipt_view.xml",
        "report/payment_export_report_view.xml",
        "report/report.xml",
    ],
    'installable': True,
}
