# -*- coding: utf-8 -*-
from openerp.addons import jasper_reports


def print_payment_export_parser(cr, uid, ids, data, context):
    return {
        'ids': data['parameters']['ids'],
    }


jasper_reports.report_jasper(
    'report.payment.export.form',
    'payment.export',  # Model View name
    parser=print_payment_export_parser
)


jasper_reports.report_jasper(
    'report.cheque.form',
    'payment.export',  # Model View name
    parser=print_payment_export_parser
)
