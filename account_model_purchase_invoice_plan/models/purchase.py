# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    date_contract_start = fields.Date(
        string='Contract Start Date',
        help="Hook Date",
    )
    is_fin_lease = fields.Boolean(
        string='Financial Lease',
        compute='_compute_is_fin_lease',
        store=True,
        help='If checked, this Invoice Plan will not participate in recurring',
    )

    @api.multi
    @api.depends('order_line.product_id')
    def _compute_is_fin_lease(self):
        for purchase in self:
            purchase.is_fin_lease = False
            fin_leases = purchase.order_line.\
                mapped('product_id').mapped('is_fin_lease')
            if len(set(fin_leases)) > 1:
                raise ValidationError(
                    _('Mixing financial lease in products is not allowed!'))
            purchase.is_fin_lease = fin_leases and fin_leases[0] or False
