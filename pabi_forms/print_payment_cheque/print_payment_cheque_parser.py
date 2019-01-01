# -*- coding: utf-8 -*-
from openerp.addons import jasper_reports


def print_payment_cheque_parser(cr, uid, ids, data, context):
    return {
        'ids': data['parameters']['ids'],
    }


jasper_reports.report_jasper(
    'report.supplier.payment.bay.cheque',
    'account.voucher',  # Model View name
    parser=print_payment_cheque_parser
)

jasper_reports.report_jasper(
    'report.supplier.payment.bbl.cheque',
    'account.voucher',  # Model View name
    parser=print_payment_cheque_parser
)

jasper_reports.report_jasper(
    'report.supplier.payment.ktb.cheque',
    'account.voucher',  # Model View name
    parser=print_payment_cheque_parser
)

jasper_reports.report_jasper(
    'report.supplier.payment.scb.cheque',
    'account.voucher',  # Model View name
    parser=print_payment_cheque_parser
)
