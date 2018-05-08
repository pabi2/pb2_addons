# -*- coding: utf-8 -*-
from openerp.addons import jasper_reports


def pabi_advance_dunning_letter_parser(cr, uid, ids, data, context):
    if context.get('email_attachment', False):
        return {
            'ids': context['ids'],
            'parameters': {
                'date_print': context['date_print'],
            }
        }
    # For ORM, just pass ids
    return {
        'ids': data['parameters']['ids'],
        'parameters': {
            'date_print': data['parameters']['date_print'],
        }
    }


jasper_reports.report_jasper(
    'report.advance_dunning_letter',  # report_name in report_data.xml
    'pabi.advance.dunning.letter.line',  # Model View name
    parser=pabi_advance_dunning_letter_parser,
)
