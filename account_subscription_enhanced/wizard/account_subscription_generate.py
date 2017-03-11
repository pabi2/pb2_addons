# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountSubscriptionGenerate(models.Model):
    _inherit = 'account.subscription.generate'

    model_type_ids = fields.Many2many(
        'account.model.type',
        string='Model Type',
        required=True,
    )

    @api.multi
    def action_generate(self):
        _ids = self.model_type_ids._ids
        res = super(AccountSubscriptionGenerate,
                    self.with_context(model_type_ids=_ids)).action_generate()
        return res
