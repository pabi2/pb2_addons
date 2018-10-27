# -*- coding: utf-8 -*-
from openerp import api, fields, models
from .account_activity import ActivityCommon
from .budget_commit import CommitCommon
from .budget_commit import CommitLineCommon


class SaleOrder(CommitCommon, models.Model):
    _inherit = 'sale.order'

    # Extension to budget_transition.py
    budget_commit_ids = fields.One2many(inverse_name='sale_id')
    budget_transition_ids = fields.One2many(inverse_name='sale_id')

    @api.multi
    def action_wait(self):
        for sale in self:
            for line in sale.order_line:
                Analytic = self.env['account.analytic.account']
                line.account_analytic_id = \
                    Analytic.create_matched_analytic(line)
        return super(SaleOrder, self).action_wait()

    @api.model
    def _prepare_order_line_procurement(self, order, line, group_id=False):
        res = super(SaleOrder, self).\
            _prepare_order_line_procurement(order, line, group_id)
        AnayticAccount = self.env['account.analytic.account']
        dimensions = AnayticAccount._analytic_dimensions()
        for d in dimensions:
            res.update({d: line[d].id})
        return res


class SaleOrderLine(CommitLineCommon, ActivityCommon, models.Model):
    _inherit = 'sale.order.line'

    budget_commit_ids = fields.One2many(inverse_name='sale_line_id')
    budget_transition_ids = fields.One2many(inverse_name='sale_line_id')

    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
    )

    # @api.multi
    # def _compute_budget_commit_bal(self):
    #     for rec in self:
    #       rec.budget_commit_bal = sum(rec.budget_commit_ids.mapped('amount'))
    #
    # @api.multi
    # def release_committed_budget(self):
    #     _field = 'sale_line_id'
    #     Analytic = self.env['account.analytic.line']
    #     for rec in self:
    #         aline = Analytic.search([(_field, '=', rec.id)],
    #                                 order='create_date desc', limit=1)
    #         if aline and rec.budget_commit_bal:
    #             aline.copy({'amount': -rec.budget_commit_bal})

    @api.multi
    def name_get(self):
        result = []
        for line in self:
            result.append(
                (line.id,
                 "%s / %s" % (line.order_id.name or '-',
                              line.name or '-')))
        return result

    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):
        res = super(SaleOrderLine, self).\
            _prepare_order_line_invoice_line(line, account_id)
        AnayticAccount = self.env['account.analytic.account']
        dimensions = AnayticAccount._analytic_dimensions()
        for d in dimensions:
            res.update({d: line[d].id})
        return res

    @api.model
    def _price_subtotal(self, line_qty):
        line_price = self._calc_line_base_price(self)
        taxes = self.tax_id.compute_all(line_price, line_qty,
                                        self.product_id,
                                        self.order_id.partner_id)
        cur = self.order_id.pricelist_id.currency_id
        return cur.round(taxes['total'])

    # When confirm PO Line, create full analytic lines
    @api.multi
    def button_confirm(self):
        res = super(SaleOrderLine, self).button_confirm()
        self._create_analytic_line(reverse=True)
        return res

    # When cancel or set done
    @api.multi
    def write(self, vals):
        # Create negative amount for the remain product_qty - open_invoiced_qty
        if vals.get('state') in ('done', 'cancel'):
            self.filtered(lambda l: l.state not in ('done',
                                                    'draft', 'cancel')).\
                _create_analytic_line(reverse=False)
        return super(SaleOrderLine, self).write(vals)
