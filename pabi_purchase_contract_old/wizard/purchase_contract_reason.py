# -*- coding: utf-8 -*-
import os
from openerp import models, fields, api
from openerp.tools.translate import _
import datetime
from pytz import timezone


class PurchaseContractReason(models.TransientModel):
    _name = "purchase.contract.reason"
    _description = "Contract Note"

    def _get_poc_files_id(self):
        if self.context is None:
            self.context = {}
        return self.context.get('files_ids', False)

    description = fields.Text(string="Description")
    datas = fields.Binary(string="Document")
    datas_fname = fields.Char(string="Filename", size=500)

    @api.multi
    def send_termination(self):
        data = {}
        data_file = []
        before_new_poc_rev = 0
        newline = _("Termination By") + ": "
        if self._context is None:
            self._context = {}
        if 'poc_id' in self._context:
            poc_obj = self.env['purchase.contract']
            poc = poc_obj.browse(self._context['poc_id'])[0]
            poc.action_button_reversion()
            poc_ids = poc_obj.search([['poc_code', '=', poc.poc_code]])
            if len(poc_ids) > 0:
                before_new_poc_rev = len(poc_ids) - 1
            poc_last = poc_obj.search([['poc_code', '=', poc.poc_code],
                                       ['poc_rev', '=', before_new_poc_rev]],
                                      limit=1)
            if self.datas_fname:
                data = {'datas': self.datas,
                        'datas_fname': self.datas_fname,
                        'name': self.datas_fname,
                        'res_model': self._context['res_model']}
                data_file.append([0, False, data])
            Employees = self.env['hr.employee']
            Emp = Employees.search(
                [['user_id', '=', self._uid]],
                limit=1)
            if Emp:
                newline += str(Emp.display_name) + "\n "
                newline += _("Reason") + ": "
                description = str(poc.description or '')
                description += newline
                description += str(self.description)
                poc_last.write({'termination_uid': Emp.id})
            termination_date = datetime.datetime.now(timezone('UTC'))
            poc_last.write(
                {'state': 'Y',
                 'termination_date': termination_date,
                 'description': description})
            poc = poc_obj.search([['poc_code', '=', poc.poc_code]])
            NextRev = len(poc)
            tempname = self.datas_fname.replace(
                "_R" + str(NextRev - 1) + ".",
                ""
            )
            filename, file_extension = os.path.splitext(tempname)
            name = filename + '_R' + str(NextRev - 1) + file_extension
            attachment = self.env['ir.attachment']
            attachment.create({
                'datas': self.datas,
                'datas_fname': name,
                'name': name,
                'res_model': self._context['res_model'],
                'res_id': poc_last.id,
            })
        form = self.env.ref(
            'pabi_purchase_contract.purchase_contract_form_view',
            False
        )
        return {
            'type': 'ir.actions.act_window',
            'name': _('PO Contrat'),
            'res_model': 'purchase.contract',
            'res_id': poc_last.id,
            'views': [(form.id, 'form')],
            'view_id': form.id,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'nodestroy': True,
            'target': 'current',
        }

    @api.multi
    def send_cancel(self):
        newline = _("Cancel By") + ": "
        if self._context is None:
            self._context = {}
        if 'poc_id' in self._context:
            poc_obj = self.env['purchase.contract']
            poc = poc_obj.browse(self._context['poc_id'])[0]
            Employees = self.env['hr.employee']
            Emp = Employees.search([['user_id',
                                     '=',
                                     self._uid]
                                    ], limit=1)
            if Emp:
                newline += str(Emp.display_name) + "\n"
                newline += _("Reason") + ": "
                poc.write({'cancel_uid': Emp.id})
            cancel_date = datetime.datetime.now(timezone('UTC'))
            description = str(poc.description or '') + newline
            description += self.description + "\n\n"
            poc.write({'state': 'X',
                       'cancel_date': cancel_date,
                       'description': description})
        return {'type': 'ir.actions.act_window_close'}
