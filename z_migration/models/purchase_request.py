# -*- coding: utf-8 -*-
from openerp import models, api


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    @api.multi
    def mork_button_approved(self):
        self.button_approved()
        return True

    @api.multi
    def mork_button_to_approve(self):
        self.button_to_approve()
        return True
