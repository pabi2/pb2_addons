# -*- coding: utf-8 -*-

from openerp import api, models, fields


class ChangeReleaseAmount(models.TransientModel):
    _name = "change.release.amount"

    to_release_amount = fields.Float(
        string="Amount To Release",
    )

    @api.model
    def default_get(self, fields):
        res = super(ChangeReleaseAmount, self).default_get(fields)
        active_id = self._context.get('active_id')
        budget = self.env['account.budget'].browse(active_id)
        res['to_release_amount'] = budget.to_release_amount
        return res

    @api.multi
    def change_amount(self):
        self.ensure_one()
        active_id = self._context.get('active_id')
        budget = self.env['account.budget'].browse(active_id)
        budget.to_release_amount = self.to_release_amount
