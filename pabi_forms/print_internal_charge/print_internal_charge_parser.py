
from openerp.addons import jasper_reports

def print_internal_charge_parser(cr, uid, ids, data, context):
    return {
        'ids': data['parameters']['ids'],
    }

jasper_reports.report_jasper(
    'report.internal.charge', #report data name
    'hr.expense.expense',  # Model View name
    parser=print_internal_charge_parser
)