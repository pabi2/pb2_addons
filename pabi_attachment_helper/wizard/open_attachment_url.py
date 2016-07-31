# -*- coding: utf-8 -*-
from openerp import models, api


class OpenAttachmentURL(models.TransientModel):
    _name = "open.attachment.url"

    @api.multi
    def open(self):
        self.ensure_one()
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        attachment = self.env[active_model].browse(active_id)
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': attachment.url,
        }
