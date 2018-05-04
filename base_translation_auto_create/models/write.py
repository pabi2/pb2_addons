# -*- coding: utf-8 -*-
import openerp
from openerp import models


write_original = models.BaseModel.write


def _set_translation(self, record_id):
    model_fields = self.fields_get()
    trans_fields = [field for field, attrs in model_fields.iteritems()
                    if attrs.get('translate')]

    for field_name in trans_fields:
        context = self._context
        self.env['ir.translation'].with_context(context).\
            translate_fields(str(self._model), record_id.id, field_name)
    return True


@openerp.api.multi
def write(self, vals):
    result = write_original(self, vals)
    if str(self._model) != 'ir.translation':
        for record_id in self:
            _set_translation(self, record_id)
    return result


models.BaseModel.write = write
