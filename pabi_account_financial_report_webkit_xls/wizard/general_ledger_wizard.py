# -*- coding: utf-8 -*-
from openerp.osv import orm
# import logging
# _logger = logging.getLogger(__name__)


class general_ledger_webkit_wizard(orm.TransientModel):
    _inherit = 'general.ledger.webkit'

    def xls_export(self, cr, uid, ids, context=None):
        return self.check_report(cr, uid, ids, context=context)

    def _print_report(self, cr, uid, ids, data, context=None):
        context = context or {}
        if context.get('xls_export'):
            # we update form with display account value
            data = self.pre_print_report(cr, uid, ids, data, context=context)

            # PABI2
            data['specific_report'] = True

            return {'type': 'ir.actions.report.xml',
                    'report_name': 'account.account_report_general_ledger_xls',
                    'datas': data}
        else:
            return super(general_ledger_webkit_wizard, self)._print_report(
                cr, uid, ids, data, context=context)
