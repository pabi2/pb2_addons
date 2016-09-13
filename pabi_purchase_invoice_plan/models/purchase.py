# -*- coding: utf-8 -*-
from openerp import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    by_fiscalyear = fields.Boolean(
        string='By Fiscal Year',
    )


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
    )
    by_fiscalyear = fields.Boolean(
        related='order_id.by_fiscalyear',
        string='By Fiscal Year',
    )


class PurchaseInvoicePlan(models.Model):
    _inherit = "purchase.invoice.plan"

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
    )