# -*- coding: utf-8 -*-
from openerp import models, api


class IRAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.multi
    def unlink(self):
        res_model = self.res_model
        res_id = self.res_id
        if len(self) == 1 and res_model and res_id and \
           (self.env.user.id == self.create_uid.id or
           self.env.user.has_group('base.group_erp_manager')):
            object = self.env[res_model].browse(res_id)
            if object._columns.get('state', False):
                if 'draft' in object.state:
                    self = self.sudo()
        return super(IRAttachment, self).unlink()
