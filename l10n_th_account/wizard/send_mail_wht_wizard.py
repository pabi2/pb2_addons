# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

class SendMailWhtWizard(models.TransientModel):
    _name = 'send.mail.wht.wizard'

    @api.multi
    def send_mail(self):
        context = dict(self._context or '')
        awt_obj = self.env['account.wht.cert'].browse(context.get('active_ids'))
        error_pv_list = []
        for rec in awt_obj:
            try:
                rec.send_mail()
            except:
                error_pv_list.append(rec.number)
                
        if error_pv_list:
            seperator = ', '
            error_pv = seperator.join(error_pv_list)
            raise ValidationError(
                _('Please fill Email Accountant in (%s). ') %(error_pv))
            
        return True