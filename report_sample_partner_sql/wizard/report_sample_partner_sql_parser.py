# -*- encoding: utf-8 -*-
from openerp.addons import jasper_reports


def report_sample_partner_sql_parser(cr, uid, ids, data, context):
    # For SQL, just pass search criterias
    return {
        # 'ids': data['parameters']['ids'],
        'parameters': {
            'customer': data['parameters']['customer'],
            'supplier': data['parameters']['supplier'],
            }
       }

jasper_reports.report_jasper(
    'report.report_sample_partner_sql',  # report_name in report_data.xml
    'report.sample.partner.sql',  # Model View name
    parser=report_sample_partner_sql_parser,
)
