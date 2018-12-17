# -*- coding: utf-8 -*-
from openerp import models, fields, api


class XLSXReportPurchaseOrderLine(models.TransientModel):
    _name = 'xlsx.report.purchase.order.line'
    _inherit = 'xlsx.report'

    # Search Criteria
    purchase_id = fields.Many2one(
        'purchase.order', string='Purchase Order',
    )
    limit = fields.Integer(
        string='Limit Records', default=1000
    )
    # Report Result
    results = fields.Many2many(
        'purchase.order.line', string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['purchase.order.line']
        dom = []
        if self.purchase_id:
            dom += [('order_id', '=', self.purchase_id.id)]
        self.results = Result.search(dom, limit=self.limit)
