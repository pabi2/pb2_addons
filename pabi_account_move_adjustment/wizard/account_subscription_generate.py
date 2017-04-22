# -*- coding: utf-8 -*-
from datetime import datetime
from openerp import models, fields, api, _


class AccountSubscriptionGenerate(models.TransientModel):
    _inherit = 'account.subscription.generate'

    calendar_period_id = fields.Many2one(
        'account.period',
        string='For Period',
        required=True,
    )
    message = fields.Text(
        string='Message',
        readonly=True,
    )
    model_type_ids = fields.Many2many(
        'account.model.type',
        string='Model Type',
        required=True,
    )

    @api.onchange('calendar_period_id')
    def _onchange_calendar_period(self):
        self.date = False
        self.message = False
        if self.calendar_period_id:
            self.date = self.calendar_period_id.date_stop
            dt = datetime.strptime(self.date, '%Y-%m-%d').strftime('%d/%m/%Y')
            message = _('\n This will generate recurring entries '
                        'before or equal to "%s".\n'
                        ' And all journal date will be "%s".') % (dt, dt)
            self.message = message

    @api.multi
    def action_generate(self):
        res = super(AccountSubscriptionGenerate, self).action_generate()
        action = self.env.ref('pabi_account_move_adjustment.'
                              'action_journal_adjust_budget')
        result = action.read()[0]
        result.update({'domain': res['domain']})
        return result
