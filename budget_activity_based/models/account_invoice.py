# -*- coding: utf-8 -*-
import itertools
from lxml import etree
from openerp.osv.orm import setup_modifiers
from openerp import api, fields, models, _
from openerp.exceptions import except_orm, Warning


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_move_create(self):
        for inv in self:
            for line in inv.invoice_line:
                if line.activity_id:
                    Analytic = self.env['account.analytic.account']
                    line.account_analytic_id = \
                        Analytic.create_matched_analytic(line)
        res = super(AccountInvoice, self).action_move_create()
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        required=True,
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        required=True,
    )

    @api.onchange('activity_id')
    def _onchange_activity_id(self):
        self.activity_group_id = self.activity_id.activity_group_id
        self.account_id = self.activity_id.account_id or \
            self.activity_id.activity_group_id.account_id
        # Set Analytic and Account
        Analytic = self.env['account.analytic.account']
        analytic = Analytic.get_matched_analytic(self)
        self.account_analytic_id = analytic
