# -*- coding: utf-8 -*-
import logging

from openerp.models import BaseModel
from openerp import api

_logger = logging.getLogger(__name__)


@api.model
def name_search(self, name='', args=None, operator='ilike', limit=100):
    result = self._name_search(name, args, operator, limit=limit)
    if not result:
        trans_name = '%s,%s' % (self._model, 'name')
        translation_ids =\
            self.env['ir.translation'].search([('value', 'ilike', name),
                                               ('name', '=', trans_name)],
                                              limit=limit)
        record_ids = [t.res_id for t in translation_ids]
        record_ids = self.browse(record_ids)
        disp = ''
        for rec in record_ids:
            if rec:
                disp = str(rec.name)
                result.append((rec.id, disp))
    return result

BaseModel.name_search = name_search
