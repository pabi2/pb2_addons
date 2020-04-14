# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import datetime


class PabiRegister_iCashWizard(models.TransientModel):
    _name = 'pabi.register.icash.wizard'
    _inherit = 'xlsx.report'

    register_id = fields.Many2one(
        'pabi.register.icash',
        'Register iCash',
        default=lambda self: self._context.get('active_id', False),
    )
    register_line_ids = fields.Many2many(
        'pabi.register.icash.line',
        'Register iCash line',
        compute='_compute_results',
    )

    @api.multi
    def _compute_results(self):
        RegisterLine = self.env['pabi.register.icash.line']
        dom = []
        if self.register_id:
            dom = [('register_id', '=', self.register_id.id)]
        self.register_line_ids = RegisterLine.search(dom)
        print('\n Results: '+str(self.register_line_ids))
    
    @api.multi
    def action_get_report(self):
        if self.register_id.state == 'draft':
            self.register_id.state = 'exported'
            self.register_id.export_date = datetime.now()
            for line in self.register_line_ids:
                line.partner_bank_id.register_no = self.register_id.name
                line.partner_bank_id.register_date = datetime.now()
                line.partner_bank_id.is_register = True
        res = super(PabiRegister_iCashWizard, self).action_get_report()
        return res


