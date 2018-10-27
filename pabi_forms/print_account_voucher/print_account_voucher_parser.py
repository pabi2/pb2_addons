# -*- coding: utf-8 -*-
from openerp.addons import jasper_reports


def print_account_voucher_parser(cr, uid, ids, data, context):
    return {
        'ids': data['parameters']['ids'],
    }


jasper_reports.report_jasper(
    'report.receipt_customer_form_en',
    'account.voucher',  # Model View name
    parser=print_account_voucher_parser
)

jasper_reports.report_jasper(
    'report.receipt_customer_form_th',
    'account.voucher',  # Model View name
    parser=print_account_voucher_parser
)

jasper_reports.report_jasper(
    'report.receipt_supplier_form_en',
    'account.voucher',  # Model View name
    parser=print_account_voucher_parser
)

jasper_reports.report_jasper(
    'report.receipt_supplier_form_th',
    'account.voucher',  # Model View name
    parser=print_account_voucher_parser
)

jasper_reports.report_jasper(
    'report.customer.receipt.form.en',
    'account.voucher',  # Model View name
    parser=print_account_voucher_parser
)

jasper_reports.report_jasper(
    'report.customer.receipt.form.th',
    'account.voucher',  # Model View name
    parser=print_account_voucher_parser
)

jasper_reports.report_jasper(
    'report.customer.tax.receipt.form.en',
    'account.voucher',  # Model View name
    parser=print_account_voucher_parser
)

jasper_reports.report_jasper(
    'report.customer.tax.receipt.form.th',
    'account.voucher',  # Model View name
    parser=print_account_voucher_parser
)

jasper_reports.report_jasper(
    'report.customer.tax.receipt.200.form.en',
    'account.voucher',  # Model View name
    parser=print_account_voucher_parser
)

jasper_reports.report_jasper(
    'report.customer.tax.receipt.200.form.th',
    'account.voucher',  # Model View name
    parser=print_account_voucher_parser
)
