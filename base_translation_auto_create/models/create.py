# -*- coding: utf-8 -*-
import openerp
from openerp import models


create_original = models.BaseModel.create


def _set_translation(self, record_id):
    model_fields = self.fields_get()
    trans_fields = [field for field, attrs in model_fields.iteritems()
                    if attrs.get('translate')]

    for field_name in trans_fields:
        context = self._context
        self.env['ir.translation'].with_context(context).\
            translate_fields(str(self._model), record_id.id, field_name)
    return True


@openerp.api.model
@openerp.api.returns('self', lambda value: value.id)
def create(self, vals):
    record_id = create_original(self, vals)
    if str(self._model) != 'ir.translation':
        _set_translation(self, record_id)
    return record_id


models.BaseModel.create = create
