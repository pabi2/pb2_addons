# -*- encoding: utf-8 -*-
from openerp.addons import jasper_reports


def pabi_dunning_letter_parser(cr, uid, ids, data, context):
    if context.get('email_attachment', False):
        return {
            'ids': ids,
            'parameters': {
                'due_days': context['due_days'],
                'date_print': context['date_print'],
            }
        }
    # For ORM, just pass ids
    return {
        'ids': data['parameters']['ids'],
        'parameters': {
            'due_days': data['parameters']['due_days'],
            'date_print': data['parameters']['date_print'],
        }
    }


jasper_reports.report_jasper(
    'report.pabi_dunning_letter',  # report_name in report_data.xml
    'hr.expense.expense',  # Model View name
    parser=pabi_dunning_letter_parser,
)
