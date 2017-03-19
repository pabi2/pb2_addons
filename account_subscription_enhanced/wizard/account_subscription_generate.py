# -*- coding: utf-8 -*-
from datetime import datetime
from openerp import models, fields, api


class AccountSubscriptionGenerate(models.Model):
    _inherit = 'account.subscription.generate'

    date_type = fields.Selection(
        [('last_period', 'Last Period'),
         ('before_date', 'Before Specific Date')],
        string='Generate Enteries',
        default='last_period',
        required=True,
    )
    model_type_ids = fields.Many2many(
        'account.model.type',
        string='Model Type',
        required=True,
    )

    @api.onchange('date_type')
    def _onchange_last_period(self):
        if self.date_type == 'last_period':
            date = fields.Date.context_today(self)
            self.date = \
                datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-01')

    @api.multi
    def action_generate(self):
        _ids = self.model_type_ids._ids
        res = super(AccountSubscriptionGenerate,
                    self.with_context(model_type_ids=_ids)).action_generate()
        return res
