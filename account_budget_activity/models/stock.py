# -*- coding: utf-8 -*-
from openerp import api, models, fields
from .account_activity import ActivityCommon


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    budget_commit_ids = fields.One2many(
        'account.analytic.line',
        string='Budget Commitment',
        compute='_compute_budget_commit_ids',
        readonly=True,
    )

    @api.multi
    def _compute_budget_commit_ids(self):
        Move = self.env['account.move']
        Analytic = self.env['account.analytic.line']
        for rec in self:
            _ids = Move.search(
                [('document', '=', rec.name)]).mapped('line_id').ids
            rec.budget_commit_ids = Analytic.search([('move_id', 'in', _ids)])


class StockMove(ActivityCommon, models.Model):
    _inherit = 'stock.move'

    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Sales Order Line',
        readonly=True,
        copy=True,
        index=True,
    )

    @api.model
    def _create_invoice_line_from_vals(self, move, invoice_line_vals):
        AnayticAccount = self.env['account.analytic.account']
        dimensions = AnayticAccount._analytic_dimensions()
        for d in dimensions:
            invoice_line_vals.update({d: move.purchase_line_id[d].id})
        return super(StockMove, self).\
            _create_invoice_line_from_vals(move, invoice_line_vals)

    @api.one
    def copy(self, default):
        """ For budget transition, we want to keep pruchase_line_id in move
        in case of return picking, we need to create new budget transition """
        if not default.get('split_from'):
            # we don't want to propagate the link to the sale order line
            # except in case of move split
            default['sale_line_id'] = False
        move = super(StockMove, self).copy(default)
        if move.origin_returned_move_id:
            origin_move = move.origin_returned_move_id
            move.write({
                'purchase_line_id': origin_move.purchase_line_id.id,
                'sale_line_id': origin_move.sale_line_id.id,
            })
        return move
