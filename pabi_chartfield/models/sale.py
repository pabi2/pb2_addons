# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .chartfield import ChartFieldAction, HeaderTaxBranch


class SaleOrder(HeaderTaxBranch, models.Model):
    _inherit = 'sale.order'

    taxbranch_ids = fields.Many2many(
        compute='_compute_taxbranch_ids',
    )
    len_taxbranch = fields.Integer(
        compute='_compute_taxbranch_ids',
    )

    @api.one
    @api.depends('order_line')
    def _compute_taxbranch_ids(self):
        lines = self.order_line
        self._set_taxbranch_ids(lines)

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        res._set_header_taxbranch_id()
        return res

    @api.model
    def _action_invoice_create_hook(self, invoice_ids):
        # Special for invoice plan, where advance is created w/o taxbranch
        # We will use other invoice's taxbranch for it
        super(SaleOrder, self)._action_invoice_create_hook(invoice_ids)
        invoices = self.env['account.invoice'].browse(invoice_ids)
        no_taxbranch_invs = invoices.filtered(lambda i: not i.taxbranch_id)
        if no_taxbranch_invs:
            taxbranch_ids = list(set([x.taxbranch_id.id for x in invoices]))
            if False in taxbranch_ids:
                taxbranch_ids.remove(False)
            for inv in no_taxbranch_invs:
                if taxbranch_ids:
                    inv.write({'taxbranch_id': taxbranch_ids[0]})
        return


class SaleOderLine(ChartFieldAction, models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def create(self, vals):
        res = super(SaleOderLine, self).create(vals)
        res.update_related_dimension(vals)
        return res
