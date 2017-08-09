# -*- encoding: utf-8 -*-
from openerp.addons import jasper_reports


def print_voucher_parser(cr, uid, ids, data, context):
    return {
        'ids': data['parameters']['ids'],
    }


jasper_reports.report_jasper(
    'report.print_voucher',
    'account.move',  # Model View name
    parser=print_voucher_parser
)
