# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
from datetime import datetime
from datetime import timedelta
from pytz import timezone
from dateutil.relativedelta import relativedelta


class osv_memory_nstdajob_syncuser(models.TransientModel):
    _inherit = 'osv_memory.nstdajob_syncuser'

    @api.model
    def pre_send_mail(self, body=None):
        emails = self._get_email_to()
        ## Check send Email
        if emails: 
            values = {'state': 'outgoing',
                     'subject': 'Odoo Job :: แจ้งผลการรัน nstdajob_syncuser_notify',
                     'body_html': '<pre>%s</pre>' % body,
                     'email_from': 'no-reply@nstda.or.th',
                     'email_to': emails,
             }
            mail_result = self.send_mail(values)
        return True

    def send_mail(self, values):
        ir_config = self.env['ir.config_parameter']
        env_mail = self.env['mail.mail']
        base_url = ir_config.get_param("web.base.url")
        mail = env_mail.sudo().create(values)
        if mail:
            mail.sudo().send(mail.ids)
        return mail

    def _get_email_to(self):
        ir_config = self.env['ir.config_parameter']
        mails = ir_config.get_param("nstdajob_syncuser.email_notify")
        return mails
