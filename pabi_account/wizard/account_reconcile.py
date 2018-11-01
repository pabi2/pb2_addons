# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountMoveLineReconcileWriteoff(models.TransientModel):
    _inherit = 'account.move.line.reconcile.writeoff'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    chartfield_id = fields.Many2one(
        'chartfield.view',
        string='Budget',
    )

    @api.v7
    def trans_rec_reconcile(self, cr, uid, ids, context=None):
        context = dict(context or {})
        data = self.read(cr, uid, ids, context=context)[0]
        context['force_partner_id'] = \
            data['partner_id'] and data['partner_id'][0] or False
        context['force_chartfield_id'] = \
            data['chartfield_id'] and data['chartfield_id'][0] or False
        context['force_comment'] = data['comment']
        return super(AccountMoveLineReconcileWriteoff, self).\
            trans_rec_reconcile(cr, uid, ids, context=context)
