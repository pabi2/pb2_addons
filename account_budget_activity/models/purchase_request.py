# -*- coding: utf-8 -*-
from openerp import api, fields, models
from .account_activity import ActivityCommon
from .budget_commit import CommitCommon
from .budget_commit import CommitLineCommon


class PurchaseRequest(CommitCommon, models.Model):
    _inherit = 'purchase.request'

    # Extension to budget_transition.py
    budget_commit_ids = fields.One2many(inverse_name='purchase_request_id')
    budget_transition_ids = fields.One2many(inverse_name='purchase_request_id')

    @api.multi
    def button_to_approve(self):
        for request in self:
            for line in request.line_ids:
                Analytic = self.env['account.analytic.account']
                line.analytic_account_id = \
                    Analytic.create_matched_analytic(line)
        return super(PurchaseRequest, self).button_to_approve()

    @api.multi
    def button_approved(self):
        for request in self:
            for line in request.line_ids:
                Analytic = self.env['account.analytic.account']
                line.analytic_account_id = \
                    Analytic.create_matched_analytic(line)
        return super(PurchaseRequest, self).button_approved()

    @api.multi
    def write(self, vals):
        # Create analytic when approved by PRWeb and be come To Accept in PR
        if vals.get('state') in ['to_approve']:
            for pr in self:
                currency_rate = pr._get_currency_rate_hook()
                pr.line_ids.filtered(
                    lambda l: l.request_state not in ('to_approve',)).\
                    _create_analytic_line(reverse=True,
                                          force_currency_rate=currency_rate)
        # Clear all budget, if any.
        if vals.get('state') in ('draft', 'done', 'rejected'):
            self.release_all_committed_budget()
        return super(PurchaseRequest, self).write(vals)

    @api.multi
    def _get_currency_rate_hook(self):
        """ HOOK """
        self.ensure_one()
        return []


class PurchaseRequestLine(CommitLineCommon, ActivityCommon, models.Model):
    _inherit = 'purchase.request.line'

    budget_commit_ids = fields.One2many(
        inverse_name='purchase_request_line_id',
    )
    budget_transition_ids = fields.One2many(
        inverse_name='purchase_request_line_id',
    )
    price_unit = fields.Float(
        string='Unit Price',
    )
    # We neeed the missing link to purchase_lines,
    # this is mock with view purchase_request_purchase_order_line_rel
    purchase_lines = fields.Many2many(
        'purchase.order.line',
        'purchase_request_purchase_order_line_rel',
        'purchase_request_line_id', 'purchase_order_line_id',
        string='Purchase Order Lines',
        compute='_compute_purchase_lines',
        store=True,
        help="purchase_request_purchase_order_line_rel is a View."
    )

    @api.multi
    def name_get(self):
        result = []
        for line in self:
            result.append(
                (line.id,
                 "%s / %s" % (line.request_id.name or '-',
                              line.name or '-')))
        return result

    @api.multi
    @api.depends('requisition_lines.purchase_line_ids.pur_line_id')
    def _compute_purchase_lines(self):
        for rec in self:
            rec.purchase_lines = \
                rec.requisition_lines.mapped('purchase_line_ids.pur_line_id')

    @api.model
    def _price_subtotal(self, line_qty):
        return self.price_subtotal
