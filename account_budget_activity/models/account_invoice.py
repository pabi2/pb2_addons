# -*- coding: utf-8 -*-
from openerp import api, models, fields
from .account_activity import ActivityCommon


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    budget_commit_ids = fields.One2many(
        'account.analytic.line',
        string='Budget Commitment',
        compute='_compute_budget_commit_ids',
        readonly=True,
    )

    @api.multi
    def _compute_budget_commit_ids(self):
        Analytic = self.env['account.analytic.line']
        for rec in self:
            _ids = rec.move_id.line_id.ids + \
                rec.cancel_move_id.line_id.ids
            rec.budget_commit_ids = Analytic.search([('move_id', 'in', _ids)])

    @api.multi
    def action_move_create(self):
        ctx = {}
        trans = False
        for inv in self:
            for line in inv.invoice_line:
                Analytic = self.env['account.analytic.account']
                line.account_analytic_id = \
                    Analytic.create_matched_analytic(line)
            # Checking for transition
            trans = self.env['budget.transition'].search([
                ('invoice_line_id', 'in', inv.invoice_line.ids),
                ('forward', '=', False)])
        # If there is PO commit to return, force_no_budget_check
        if trans:
            self.ensure_one()  # With this, must ensure one
            ctx['force_no_budget_check'] = True
        return super(AccountInvoice, self.with_context(ctx)).\
            action_move_create()


class AccountInvoiceLine(ActivityCommon, models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def name_get(self):
        result = []
        for line in self:
            result.append(
                (line.id,
                 "%s / %s" % (line.invoice_id.name or '-',
                              line.name or '-')))
        return result
