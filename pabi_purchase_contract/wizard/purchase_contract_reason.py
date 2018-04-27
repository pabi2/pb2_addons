# -*- coding: utf-8 -*-
import os
from openerp import models, fields, api
from openerp.exceptions import ValidationError
from openerp.tools.translate import _
import datetime
from pytz import timezone


class PurchaseContractReason(models.TransientModel):
    _name = 'purchase.contract.reason'
    _description = 'Contract Note'

    description = fields.Text(
        string='Description',
    )
    datas = fields.Binary(
        string='Document',
    )
    datas_fname = fields.Char(
        string='Filename',
        size=500,
    )

    @api.multi
    def send_termination(self):
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        POC = self.env[active_model]
        poc = POC.browse(active_id)  # This poc
        # Allow terminate only if no rev in the same series terminated before
        terminated = POC.search_count([('poc_code', '=', poc.poc_code),
                                       ('state', '=', 'terminate')])
        if terminated:
            raise ValidationError(_('Already terminated!'))
        new_poc_id = poc.action_button_reversion()['res_id']
        new_poc = POC.browse(new_poc_id)  # New poc
        employee = self.env.user.employee_id
        description = _('Terminated By: %s\nReason: %s') % \
            (employee.display_name, self.description)
        # Write data to newly created contract revision
        new_poc.write({
            'state': 'terminate',
            'termination_uid': employee.id,
            'termination_date': datetime.datetime.now(timezone('UTC')),
            'description': description, })
        tempname = self.datas_fname.replace('_R%s' % poc.poc_rev, '')
        filename, file_extension = os.path.splitext(tempname)
        name = '%s_R%s%s' % (filename, new_poc.poc_rev, file_extension)
        # Attachment
        self.env['ir.attachment'].create({
            'datas': self.datas,
            'datas_fname': name,
            'name': name,
            'res_model': active_model,
            'res_id': new_poc.id,
        })

        form = self.env.ref('pabi_purchase_contract.'
                            'purchase_contract_form_view')
        return {
            'type': 'ir.actions.act_window',
            'name': _('PO Contrat'),
            'res_model': 'purchase.contract',
            'res_id': new_poc.id,
            'views': [(form.id, 'form')],
            'view_id': form.id,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'nodestroy': True,
            'target': 'current',
        }

    @api.multi
    def send_cancel(self):
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        POC = self.env[active_model]
        poc = POC.browse(active_id)  # This poc
        employee = self.env.user.employee_id
        description = _('Cancelled By: %s\nReason: %s') % \
            (employee.display_name, self.description)
        poc.write({'state': 'cancel_generate',
                   'cancel_uid': employee.id,
                   'cancel_date': datetime.datetime.now(timezone('UTC')),
                   'description': description})
        return {'type': 'ir.actions.act_window_close'}
