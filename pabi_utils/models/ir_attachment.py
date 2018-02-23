# -*- coding: utf-8 -*-
import logging
from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        if self._context.get('domain_template_ids', False):
            args += [('id', 'in', self._context['domain_template_ids'][0][2])]
        return super(IrAttachment, self).name_search(name=name, args=args,
                                                     operator=operator,
                                                     limit=limit)

    @api.model
    def load_xlsx_template(self, addon, template_ids, file_dir):
        for xml_id in template_ids:
            try:
                xmlid = '%s.%s' % (addon, xml_id)
                att = self.env.ref(xmlid)
                file_path = '%s/%s' % (file_dir, att.datas_fname)
                att.datas = open(file_path, 'rb').read().encode('base64')
            except ValueError, e:
                _logger.exception(e.message)
