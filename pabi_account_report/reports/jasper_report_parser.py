# -*- coding: utf-8 -*-
from openerp.addons import jasper_reports


def jasper_report_payable_confirmation_letter_parser(cr, uid, ids, data,
                                                     context):
    return data


def jasper_report_payment_history_parser(cr, uid, ids, data, context):
    return data


jasper_reports.report_jasper(
    'report.payable_confirmation_letter',
    'account.move.line',
    parser=jasper_report_payable_confirmation_letter_parser,
)

jasper_reports.report_jasper(
    'report.customer_payment_history',
    'payment.history.view',
    parser=jasper_report_payment_history_parser,
)

jasper_reports.report_jasper(
    'report.bank_payment_history',
    'payment.history.view',
    parser=jasper_report_payment_history_parser,
)
