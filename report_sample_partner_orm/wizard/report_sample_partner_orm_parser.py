# -*- coding: utf-8 -*-
from openerp.addons import jasper_reports


def report_sample_partner_orm_parser(cr, uid, ids, data, context):
    # For ORM, just pass ids
    return {
        'ids': data['parameters']['ids'],
        'parameters': {
            'xxx': data['parameters']['ids'],
        }
    }


jasper_reports.report_jasper(
    'report.report_sample_partner_orm',  # report_name in report_data.xml
    'report.sample.partner.orm',  # Model View name
    parser=report_sample_partner_orm_parser,
)
