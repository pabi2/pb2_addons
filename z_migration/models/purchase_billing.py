# -*- coding: utf-8 -*-
from openerp import models, api


class PurchaseBilling(models.Model):
    _inherit = 'purchase.billing'

    @api.multi
    def mork_validate_billing(self):
        self.validate_billing()
        return True
