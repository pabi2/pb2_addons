# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def actoin_wait(self):
        res = super(SaleOrder, self).actoin_wait()
        # Case Invoice Plan + Advance: all line must charge same budget
        # So that, advance line know which budget to use.
        for rec in self:
            if rec.use_invoice_plan and rec.use_deposit:
                if len(rec.order_line.mapped('account_analytic_id')) != 1:
                    raise ValidationError(
                        _('No mixing of costcenter when use Advance!'))
        return res

    @api.model
    def _prepare_deposit_invoice_line(self, name, order, amount):
        res = super(SaleOrder, self).\
            _prepare_deposit_invoice_line(name, order, amount)
        AnayticAccount = self.env['account.analytic.account']
        dimensions = AnayticAccount._analytic_dimensions()
        for d in dimensions:
            if d in ('product_id', 'activity_group_id',
                     'activity_id', 'activity_rpt_id'):
                continue  # Do not need to copy above dimension.
            res.update({d: order.order_line[0][d].id})
        return res
