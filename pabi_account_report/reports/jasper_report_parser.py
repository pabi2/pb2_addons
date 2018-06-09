# -*- coding: utf-8 -*-
from openerp.addons import jasper_reports


def jasper_report_parser(cr, uid, ids, data, context):
    return data


jasper_reports.report_jasper(
    'report.payable_confirmation_letter',
    'account.move.line',
    parser=jasper_report_parser,
)

jasper_reports.report_jasper(
    'report.customer_payment_history',
    'payment.history.view',
    parser=jasper_report_parser,
)

jasper_reports.report_jasper(
    'report.bank_payment_history',
    'payment.history.view',
    parser=jasper_report_parser,
)

jasper_reports.report_jasper(
    'report.customer_receivable_follow_up',
    'receivable.follow.up.view',
    parser=jasper_report_parser,
)

jasper_reports.report_jasper(
    'report.bank_receivable_follow_up',
    'receivable.follow.up.view',
    parser=jasper_report_parser,
)
