# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class PurchaseWorkAcceptance(models.Model):
    _inherit = 'purchase.work.acceptance'

    @api.multi
    @api.constrains('acceptance_line_ids')
    def _check_duplicate_acceptance_line(self):
        for rec in self:
            product_lists = []
            for line in rec.acceptance_line_ids:
                product_lists.append(line.product_id.id)
            list_dup_product_ids = list(
                set([x for x in product_lists if product_lists.count(x) > 1])
            )
            for line in rec.acceptance_line_ids:
                if line.product_id.id in list_dup_product_ids:
                    if line.balance_qty != line.to_receive_qty:
                        raise ValidationError(
                            _(
                                "Duplicate product lines must be "
                                "fully received."
                            )
                        )
