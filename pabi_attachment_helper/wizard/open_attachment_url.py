# -*- coding: utf-8 -*-
from openerp import models, api, fields


class OpenAttachmentURL(models.TransientModel):
    _name = "open.attachment.url"

    attachment_id = fields.Many2one(
        'ir.attachment',
        string='Attachment',
    )
    binary_file = fields.Binary(
        related='attachment_id.datas',
        string='File Name',
        readonly=True,
    )
    file_name = fields.Char(
        related='attachment_id.datas_fname',
        string='File Name',
    )
    type = fields.Selection(
        related='attachment_id.type',
    )

    @api.model
    def default_get(self, fields):
        res = super(OpenAttachmentURL, self).default_get(fields)
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        if active_model == 'ir.attachment':
            res['attachment_id'] = active_id
        else:
            record = self.env[active_model].browse(active_id)
            if 'attachment_id' in record._fields:
                res['attachment_id'] = record.attachment_id.id
            elif 'attachement_id' in record._fields:
                res['attachment_id'] = record.attachement_id.id
        return res

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
