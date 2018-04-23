# -*- coding: utf-8 -*-
from openerp import api, models


class BudgetTechnicalCloseWizard(models.TransientModel):
    _name = "budget.technical.close.wizard"

    @api.multi
    def action_close(self):
        self.ensure_one()
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        record = self.env[active_model].browse(active_id)
        record.action_technical_closed()
