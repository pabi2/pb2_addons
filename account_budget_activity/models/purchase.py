# -*- coding: utf-8 -*-
from openerp import api, fields, models
from .account_activity import ActivityCommon
from .budget_commit import CommitCommon
from .budget_commit import CommitLineCommon


class PurchaseOrder(CommitCommon, models.Model):
    _inherit = 'purchase.order'

    # Extension to budget_transition.py
    budget_commit_ids = fields.One2many(inverse_name='purchase_id')
    budget_transition_ids = fields.One2many(inverse_name='purchase_id')

    @api.multi
    def wkf_confirm_order(self):
        for purchase in self:
            for line in purchase.order_line:
                Analytic = self.env['account.analytic.account']
                line.account_analytic_id = \
                    Analytic.create_matched_analytic(line)
        return super(PurchaseOrder, self).wkf_confirm_order()

    @api.model
    def _prepare_inv_line(self, account_id, order_line):
        res = super(PurchaseOrder, self).\
            _prepare_inv_line(account_id, order_line)
        AnayticAccount = self.env['account.analytic.account']
        dimensions = AnayticAccount._analytic_dimensions()
        for d in dimensions:
            res.update({d: order_line[d].id})
        return res

    @api.model
    def _prepare_order_line_move(self, order, order_line,
                                 picking_id, group_id):
        res = super(PurchaseOrder, self).\
            _prepare_order_line_move(order, order_line,
                                     picking_id, group_id)
        AnayticAccount = self.env['account.analytic.account']
        dimensions = AnayticAccount._analytic_dimensions()
        for d in dimensions:
            for r in res:
                r.update({d: order_line[d].id})
        return res

    # When draft, cancel or set done, clear all budget
    @api.multi
    def write(self, vals):
        if vals.get('state') in ('draft', 'done', 'cancel'):
            self.release_all_committed_budget()
        return super(PurchaseOrder, self).write(vals)


class PurchaseOrderLine(CommitLineCommon, ActivityCommon, models.Model):
    _inherit = 'purchase.order.line'

    budget_commit_ids = fields.One2many(inverse_name='purchase_line_id')
    budget_transition_ids = fields.One2many(inverse_name='purchase_line_id')

    requisition_line_id = fields.Many2one(
        'purchase.requisition.line',
        string='Purchase Requisition Line',
    )

    @api.multi
    def name_get(self):
        result = []
        for line in self:
            result.append(
                (line.id,
                 "%s / %s" % (line.order_id.name or '-',
                              line.name or '-')))
        return result

    @api.multi
    def onchange_product_id(
            self, pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft'):
        res = super(PurchaseOrderLine, self).onchange_product_id(
            pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=date_order, fiscal_position_id=fiscal_position_id,
            date_planned=date_planned, name=name,
            price_unit=price_unit, state=state)
        if not res['value'].get('date_planned', False):
            date_planned = date_planned or fields.Date.context_today(self)
            res['value'].update({'date_planned': date_planned})
        return res

    @api.model
    def _price_subtotal(self, line_qty):
        line_price = self._calc_line_base_price(self)
        taxes = self.taxes_id.compute_all(line_price, line_qty,
                                          self.product_id,
                                          self.order_id.partner_id)
        cur = self.order_id.pricelist_id.currency_id
        return cur.round(taxes['total'])

    # When confirm PO Line, create full analytic lines
    @api.multi
    def action_confirm(self):
        res = super(PurchaseOrderLine, self).action_confirm()
        self._create_analytic_line(reverse=True)
        return res
