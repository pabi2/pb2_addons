# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def message_intray(self, object, subject, body,
                       owner, boss, action, is_complete):
        """ Use this method to submit message as subtype intray
            Note: boss can be single or multiple (list of string)
        """
        bosses = []
        boss = boss or []
        if isinstance(boss, list) or isinstance(boss, tuple):
            bosses = boss
        elif isinstance(boss, basestring):
            bosses.append(boss)
        else:
            raise ValidationError(
                _('Invalid input param boss, must be str or list of str'))

        message_id = object.message_post(body=body, subject=subject,
                                         type='notification',
                                         subtype='pabi_intray.intray_message')
        url = 'toolbar=hide#id=%s&view_type=form&model=%s' % (object.id,
                                                              object._name)

        if bosses:
            for boss in bosses:
                vals = {'message_id': message_id,
                        'owner': owner,
                        'boss': boss,
                        'action': action,
                        'is_complete': is_complete,
                        'url': url}
        else:
            vals = {'message_id': message_id,
                    'owner': owner,
                    'action': action,
                    'is_complete': is_complete,
                    'url': url}
        self.env['pabi.intray'].create(vals)
        return True
