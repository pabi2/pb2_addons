# -*- coding: utf-8 -*-
from openerp import models, api, fields


class AccountAutoReconcile(models.Model):
    _name = 'account.auto.reconcile'

    name = fields.Char(
        string='Code',
        required=True,
        size=20,
        help="Normally use source document number",
    )
    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'Auto Reconcile Name must be unique'),
    ]

    @api.model
    def get_auto_reconcile_id(self, name):
        auto_reconcile = self.search([('name', '=', name)])
        if auto_reconcile:
            return auto_reconcile.id
        else:
            return self.create({'name': name}).id


class AccountMove(models.Model):
    _inherit = 'account.move'

    auto_reconcile_id = fields.Many2one(
        'account.auto.reconcile',
        string='Auto Reconcile ID',
        size=20,
        help="To group journal entry for auto reconcilation",
    )

    @api.multi
    def post(self):
        """ For case crate JE manual, to reconcile with another JE """
        res = super(AccountMove, self).post()
        MoveLine = self.env['account.move.line']
        for move in self:
            if move.auto_reconcile_id:
                mlines = MoveLine.search([('auto_reconcile_id', '=',
                                           move.auto_reconcile_id.id)])
                mlines.reconcile_special_account()
        return res
