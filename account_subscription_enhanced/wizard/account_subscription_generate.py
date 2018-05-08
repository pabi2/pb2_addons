# -*- coding: utf-8 -*-
import ast
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _


class AccountSubscriptionGenerate(models.Model):  # Change to a Model
    _inherit = 'account.subscription.generate'
    _rec_name = 'id'
    _order = 'id desc'

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    calendar_period_id = fields.Many2one(
        'account.period.calendar',
        string='For Period',
        domain=[('state', '=', 'draft')],
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date = fields.Date(
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    message = fields.Text(
        string='Message',
        readonly=True,
    )
    model_type_ids = fields.Many2many(
        'account.model.type',
        string='Model Types',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done')],
        string='Status',
        readonly=True,
        default='draft',
    )
    move_ids = fields.Many2many(
        'account.move',
        'subscription_generate_account_move_rel',
        'subscription_id', 'move_id',
        string='Journal Entries',
        readonly=True,
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
        model_type_ids = self.model_type_ids._ids
        end_period_date = self.date
        date = datetime.strptime(self.date, "%Y-%m-%d") + relativedelta(days=1)
        self.date = date.strftime('%Y-%m-%d')
        res = super(AccountSubscriptionGenerate,
                    self.with_context(model_type_ids=model_type_ids,
                                      end_period_date=end_period_date,  # Pass
                                      )).action_generate()
        domain = ast.literal_eval(res['domain'])
        move_ids = domain[0][2]
        self.write({'move_ids': [(6, 0, move_ids)],
                    'state': 'done'})
        return True

    @api.multi
    def open_entries(self):
        self.ensure_one()
        return {
            'name': _("Journal Entries"),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': self._context,
            'nodestroy': True,
            'domain': [('id', 'in', self.move_ids.ids)],
        }
