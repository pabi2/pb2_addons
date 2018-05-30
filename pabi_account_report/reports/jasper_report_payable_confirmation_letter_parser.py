# -*- coding: utf-8 -*-
from openerp.addons import jasper_reports


def jasper_report_payable_confirmation_letter_parser(cr, uid, ids, data,
                                                     context):
    return data


jasper_reports.report_jasper(
    'report.payable_confirmation_letter',
    'account.move.line',
    parser=jasper_report_payable_confirmation_letter_parser,
)
