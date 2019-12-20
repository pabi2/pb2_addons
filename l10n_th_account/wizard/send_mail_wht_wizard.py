# -*- coding: utf-8 -*-
from openerp import models, fields, api


class SendMailWhtWizard(models.TransientModel):
    _name = 'send.mail.wht.wizard'

    @api.multi
    def send_mail(self):
        context = dict(self._context or '')
        awt_obj = self.env['account.wht.cert'].browse(context.get('active_ids'))
        for rec in awt_obj:
            rec.send_mail()
            
        return True