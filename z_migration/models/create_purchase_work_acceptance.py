# -*- coding: utf-8 -*-
from openerp import models, api


class CreatePurchaseWorkAcceptance(models.TransientModel):

    _inherit = 'create.purchase.work.acceptance'

    @api.model
    def mork_create_purchase_work_acceptance(self):
        prepare_create_acceptance = self.default_get(self._columns.keys())
        create_acceptance = self.create(prepare_create_acceptance)
        return create_acceptance.id

    @api.multi
    def mork_action_create_work_acceptance(self):
        acceptance = self._prepare_acceptance()
        acceptance.order_id = self._context.copy().get('active_id', False)
        return True
