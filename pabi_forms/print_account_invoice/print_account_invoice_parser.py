# -*- coding: utf-8 -*-
from openerp.addons import jasper_reports


def print_account_invoice_parser(cr, uid, ids, data, context):
    return {
        'ids': data['parameters']['ids'],
    }


# jasper_reports.report_jasper(
#     'account.invoice.form',  # report_name in account_data.xml
#     'account.invoice',  # Model View name
#     parser=print_account_invoice_parser
# )

jasper_reports.report_jasper(
    'report.customer.invoice.en.form',
    'account.invoice',  # Model View name
    parser=print_account_invoice_parser
)

jasper_reports.report_jasper(
    'report.customer.invoice.th.form',
    'account.invoice',  # Model View name
    parser=print_account_invoice_parser
)

jasper_reports.report_jasper(
    'report.customer.tax.receipt.picking.form.en',
    'account.invoice',  # Model View name
    parser=print_account_invoice_parser
)

jasper_reports.report_jasper(
    'report.customer.tax.receipt.picking.form.th',
    'account.invoice',  # Model View name
    parser=print_account_invoice_parser
)
