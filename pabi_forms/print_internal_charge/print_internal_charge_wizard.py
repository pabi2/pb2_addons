# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


# สร้าง FIELD
class PrintInternalChargeWizard(models.TransientModel):
    _name = 'print.internal.charge.wizard'


    @api.multi
    def action_print_internal_charge(self):
        data = {'parameters': {}}
        ids = self._context.get('active_ids')
        data['parameters']['ids'] = ids
        report_name = 'internal_charge'
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
            'context': self._context,  # Requried for report wizard
        }
        return res
