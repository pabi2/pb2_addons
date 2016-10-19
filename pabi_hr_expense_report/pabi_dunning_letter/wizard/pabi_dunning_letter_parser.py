# -*- encoding: utf-8 -*-
from openerp.addons import jasper_reports


def pabi_dunning_letter_parser(cr, uid, ids, data, context):
    # For ORM, just pass ids
    return {
        'ids': data['parameters']['ids'],
        'parameters': {
            'due_days': data['parameters']['due_days'],
        }
    }

jasper_reports.report_jasper(
    'report.pabi_dunning_letter',  # report_name in report_data.xml
    'hr.expense.expense',  # Model View name
    parser=pabi_dunning_letter_parser,
)
