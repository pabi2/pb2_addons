# -*- coding: utf-8 -*-
import logging
import os
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

    # @api.model
    # def load_xlsx_template(self, addon, template_ids, file_dir):
    #     print addon
    #     print template_ids
    #     print file_dir
    #     for xml_id in template_ids:
    #         try:
    #             xmlid = '%s.%s' % (addon, xml_id)
    #             att = self.env.ref(xmlid)
    #             file_path = '%s/%s' % (file_dir, att.datas_fname)
    #             att.datas = open(file_path, 'rb').read().encode('base64')
    #         except ValueError, e:
    #             _logger.exception(e.message)

    @api.model
    def load_xlsx_template(self, att_ids, folder):
        for att in self.browse(att_ids):
            try:
                file_dir = os.path.dirname(os.path.realpath(__file__))
                # While can't find better solution, we get the addon dir by
                # so, make sure that the calling addon in in the same foloer
                # with this pabi_utils
                file_dir = file_dir.replace('/pabi_utils/models', '')
                file_path = '%s/%s/%s' % (file_dir, folder, att.datas_fname)
                att.datas = open(file_path, 'rb').read().encode('base64')
            except ValueError, e:
                _logger.exception(e.message)
