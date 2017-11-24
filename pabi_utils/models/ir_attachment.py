# -*- coding: utf-8 -*-
from openerp import models, fields, api


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        if self._context.get('domain_template_ids', False):
            args += [('id', 'in', self._context['domain_template_ids'][0][2])]
        return super(IrAttachment, self).name_search(name=name, args=args,
                                                     operator=operator,
                                                     limit=limit)
