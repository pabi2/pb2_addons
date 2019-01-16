# -*- coding: utf-8 -*-
from openerp.osv import fields, orm


class AccountingReport(orm.TransientModel):

    _inherit = "accounting.report"

    _columns = {
        'charge_type': fields.selection(
            [('internal', 'Internal'),
             ('external', 'External')],
            string='Charge Type',
        )
    }

    def _build_contexts(self, cr, uid, ids, data, context=None):
        result = super(AccountingReport, self)._build_contexts(
            cr, uid, ids, data, context=context)
        data2 = {}
        data2['form'] = self.read(
            cr, uid, ids, ['charge_type'], context=context)[0]
        result['charge_type'] = 'charge_type' in data2['form']\
                                and data2['form']['charge_type'] or False
        if 'active_test' in context:
            result['active_test'] = context['active_test']
        return result

    def _build_comparison_context(self, cr, uid, ids, data, context=None):
        result = super(AccountingReport, self)._build_comparison_context(
            cr, uid, ids, data, context=context)
        data['form'] = self.read(cr, uid, ids, ['charge_type'])[0]
        result['charge_type'] = 'charge_type' in data['form'] \
                                and data['form']['charge_type'] or False
        if 'active_test' in context:
            result['active_test'] = context['active_test']
        return result
