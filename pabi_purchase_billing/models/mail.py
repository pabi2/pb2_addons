# -*- coding: utf-8 -*-

from openerp import models, api


class Mail(models.Model):
    _inherit = "mail.mail"

    @api.model
    def _postprocess_sent_message(self, mail, mail_sent=True):
        if mail_sent and mail.model == 'purchase.billing':
            obj = self.env['purchase.billing'].browse(mail.res_id)
            obj.write({'email_sent':  True})
        return super(Mail, self)._postprocess_sent_message(mail,
                                                           mail_sent=mail_sent)
