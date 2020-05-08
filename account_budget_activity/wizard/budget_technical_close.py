# -*- coding: utf-8 -*-
from openerp import api, models, fields


class BudgetTechnicalCloseWizard(models.TransientModel):
    _name = "budget.technical.close.wizard"

    reason_text = fields.Text(
        string='Reason',
    )
    
    @api.multi
    def action_close(self):
        self.ensure_one()
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        record = self.env[active_model].browse(active_id)
        record.action_technical_closed()
        record.write({'reason_text': self.reason_text,})
