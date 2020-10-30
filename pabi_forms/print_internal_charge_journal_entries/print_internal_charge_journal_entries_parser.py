from openerp.addons import jasper_reports

def print_internal_charge_journal_entries_parser(cr, uid, ids, data, context):
    return {
        'ids': data['parameters']['ids'],
    }

jasper_reports.report_jasper(
    'report.internal.charge.journal.entries', #report data name
    'account.move',  # Model View name
    parser=print_internal_charge_journal_entries_parser
)