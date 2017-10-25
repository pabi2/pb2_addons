# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class PABIDataMap(models.Model):
    _name = 'pabi.data.map'
    _description = 'Field mapping database, used for import/export'

    type = fields.Selection(
        [('sample', 'Sample')],
        string='Type',
        index=True,
        default='sample',
    )
    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        index=True,
    )
    field_id = fields.Many2one(
        'ir.model.fields',
        string='Field',
        domain="[('model_id', '=', model_id)]",
        index=True,
    )
    in_value = fields.Char(
        string='Input Value',
        index=True,
        help="Odoo's value, searchable by name_search",
    )
    out_value = fields.Char(
        string='Output Value',
        index=True,
        help="Mapped output value",
    )
    _sql_constraints = [
        ('in_value_uniq', 'unique(type, model_id, field_id, in_value)',
         'In value must be unique!'),
        ('out_value_uniq', 'unique(type, model_id, field_id, out_value)',
         'Out value must be unique!')
    ]

    @api.onchange('model_id')
    def _onchange_model_id(self):
        self.field_id = False

    @api.model
    def get_out_value(self, type, model_id, field_id, in_value=False):
        out_value = False
        if in_value:
            out_value = self.search(
                [('type', '=', type), ('model_id', '=', model_id),
                 ('field_id', '=', field_id), ('in_value', '=', in_value)],
                limit=1).out_value
        return out_value
