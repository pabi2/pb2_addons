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
    'report.cd_receivable_payment_history_group_by_customer',
    'cd.receivable.payment.history.view',
    parser=jasper_report_parser,
)

jasper_reports.report_jasper(
    'report.cd_receivable_payment_history_group_by_bank',
    'cd.receivable.payment.history.view',
    parser=jasper_report_parser,
)

jasper_reports.report_jasper(
    'report.cd_receivable_follow_up_group_by_customer',
    'cd.receivable.follow.up.view',
    parser=jasper_report_parser,
)

jasper_reports.report_jasper(
    'report.cd_receivable_follow_up_group_by_bank',
    'cd.receivable.follow.up.view',
    parser=jasper_report_parser,
)
