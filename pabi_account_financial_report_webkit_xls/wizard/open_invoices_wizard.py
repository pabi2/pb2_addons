# -*- coding: utf-8 -*-
from openerp.osv import orm
# import logging
# _logger = logging.getLogger(__name__)


class open_invoices_webkit_wizard(orm.TransientModel):
    _inherit = 'open.invoices.webkit'

    def xls_export(self, cr, uid, ids, context=None):
        return self.check_report(cr, uid, ids, context=context)

    def _print_report(self, cr, uid, ids, data, context=None):
        context = context or {}
        if context.get('xls_export'):
            # we update form with display account value
            data = self.pre_print_report(cr, uid, ids, data, context=context)
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'account.account_report_open_invoices_xls',
                    'datas': data}
        else:
            return super(open_invoices_webkit_wizard, self)._print_report(
                cr, uid, ids, data, context=context)
