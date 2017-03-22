# -*- coding: utf-8 -*-
from openerp.addons import jasper_reports


def pabi_hr_advance_status_report_parser(cr, uid, ids, data, context):
    # For ORM, just pass ids
    return {
        'ids': data['parameters']['ids'],
        'parameters': {
            'xxx': data['parameters']['ids'],
        }
    }


jasper_reports.report_jasper(
    'report.pabi_hr_advance_status_report', # report_name in report_data.xml
    'hr.expense.expense',
    parser=pabi_hr_advance_status_report_parser,
)

jasper_reports.report_jasper(
    'report.pabi_hr_advance_status_summary_report', # report_name in report_data.xml
    'hr.expense.expense',
    parser=pabi_hr_advance_status_report_parser,
)

jasper_reports.report_jasper(
    'report.pabi_hr_advance_status_detail_report', # report_name in report_data.xml
    'hr.expense.expense',
    parser=pabi_hr_advance_status_report_parser,
)
