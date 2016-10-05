# -*- encoding: utf-8 -*-
from openerp.addons import jasper_reports


# PND 53
def report_pnd53_form_parser(cr, uid, ids, data, context):
    # For ORM, just pass ids
    return {
        'ids': data['parameters']['ids'],
        'parameters': {
            'company_taxid': data['parameters']['company_taxid'],
            'company_branch': data['parameters']['company_branch'],
            }
       }

jasper_reports.report_jasper(
    'report.report_pnd53_form',  # report_name in report_data.xml
    'account.voucher',  # Model View name
    parser=report_pnd53_form_parser,
)


# PND 3
def report_pnd3_form_parser(cr, uid, ids, data, context):
    # For ORM, just pass ids
    return {
        'ids': data['parameters']['ids'],
        'parameters': {
            'company_taxid': data['parameters']['company_taxid'],
            'company_branch': data['parameters']['company_branch'],
            }
       }

jasper_reports.report_jasper(
    'report.report_pnd3_form',  # report_name in report_data.xml
    'account.voucher',  # Model View name
    parser=report_pnd3_form_parser,
)
