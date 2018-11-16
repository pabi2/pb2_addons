# -*- coding: utf-8 -*-
from openerp import models, fields, api
# from openerp.exceptions import ValidationError


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
            # kittiu: No more warning, 1 line is fin lease -> fin_lease = True
            # fin_leases =purchase.order_line.mapped('product_id.is_fin_lease')
            # if len(set(fin_leases)) > 1:
            #     raise ValidationError(
            #         _('Mixing financial lease in products is not allowed!'))
            # purchase.is_fin_lease = fin_leases and fin_leases[0] or False
            purchase.is_fin_lease = \
                purchase.order_line.filtered('product_id.is_fin_lease') and \
                True or False
