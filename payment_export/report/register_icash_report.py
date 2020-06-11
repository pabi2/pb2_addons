# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import datetime


class PabiRegister_iCashReport(models.TransientModel):
    _name = 'pabi.register.icash.report'
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
        self.ensure_one()

        if self.register_id.state == 'draft':
            self.register_id._check_record_registered()
            out_file, out_name = self.get_report()

            self.env['ir.attachment'].create({
                'name': self.register_id.name+'.xlsx',
                'datas': out_file,
                'datas_fname': self.register_id.name+'.xlsx',
                'res_model': 'pabi.register.icash',
                'res_id': self.register_id.id,
                'type': 'binary',
            })
            self.register_id.write({'state': 'exported',
                                    'export_date': datetime.now()})

            for line in self.register_line_ids:
                line.partner_bank_id.write({
                    'register_no': self.register_id.name,
                    'register_date': datetime.now(),
                    'is_register': True})
