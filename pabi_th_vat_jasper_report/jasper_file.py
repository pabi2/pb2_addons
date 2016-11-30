# -*- encoding: utf-8 -*-
from openerp.addons import jasper_reports


def report_sample_partner_orm_parser(cr, uid, ids, data, context):
    # For ORM, just pass ids
    return {
        
       }

jasper_reports.report_jasper(
    'report.vat_report_pdf',  # report_name in report_data.xml
    'account.vat.report',  # Model View name
    parser=report_sample_partner_orm_parser,
)
