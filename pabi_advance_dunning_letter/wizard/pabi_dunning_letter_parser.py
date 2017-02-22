# -*- encoding: utf-8 -*-
from openerp.addons import jasper_reports


def advance_dunning_letter_parser(cr, uid, ids, data, context):
    if context.get('email_attachment', False):
        return {
            'ids': ids,
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
    'advance.dunning.letter',  # Model View name
    parser=advance_dunning_letter_parser,
)
