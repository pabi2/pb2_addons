# -*- coding: utf-8 -*-
from openerp import models, api


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def message_intray(self, object, subject, body,
                       owner, boss, action, is_complete):
        """ Use this method to submit message as subtype intray """
        message_id = object.message_post(body=body, subject=subject,
                                         type='notification',
                                         subtype='pabi_intray.intray_message')
        url = 'toolbar=hide#id=%s&view_type=form&model=%s' % (object.id,
                                                              object._name)
        vals = {'message_id': message_id,
                'owner': owner,
                'boss': boss,
                'action': action,
                'is_complete': is_complete,
                'url': url}
        self.env['pabi.intray'].create(vals)
        return True
