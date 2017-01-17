# -*- encoding: utf-8 -*-
from openerp.addons import jasper_reports
from print_voucher_wizard import *


def print_voucher_parser(cr, uid, ids, data, context):
    return {
        'ids': data['parameters']['ids'],
    }

# KV Voucher && DV Voucher
jasper_reports.report_jasper(
    'report.invoice.voucher',  # report_name in account_data.xml
    'account.move',  # Model View name
    parser=print_voucher_parser
)

# PV Voucher && RC Voucher
jasper_reports.report_jasper(
    'report.payment.voucher',  # report_name in account_data.xml
    'account.move',  # Model View name
    parser=print_voucher_parser
)

# RV Voucher
jasper_reports.report_jasper(
    'report.bank.receipt.voucher',  # report_name in account_data.xml
    'account.move',  # Model View name
    parser=print_voucher_parser
)
