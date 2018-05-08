# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PABIDataMap(models.Model):
    _name = 'pabi.data.map'
    _description = 'Field mapping database, used for import/export'

    map_type_id = fields.Many2one(
        'pabi.data.map.type',
        string='Map Type',
        index=True,
        ondelete='cascade',
        requried=True,
    )
    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        index=True,
        required=True,
    )
    field_id = fields.Many2one(
        'ir.model.fields',
        string='Field',
        domain="[('model_id', '=', model_id)]",
        index=True,
        required=True,
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
        ('in_value_uniq',
         'unique(map_type_id, model_id, field_id, in_value)',
         'In value must be unique!'),
    ]

    @api.onchange('model_id')
    def _onchange_model_id(self):
        self.field_id = False

    @api.multi
    def write(self, vals):
        if 'field_id' in vals:
            if not vals['field_id']:
                vals['model_id'] = False
            elif not vals.get('model_id', False):
                field = self.env['ir.model.fields'].browse(vals['field_id'])
                vals['model_id'] = field.model_id.id
        return super(PABIDataMap, self).write(vals)

    @api.model
    def get_out_value(self, map_type, model, field, in_value=False):
        """
        map_type = Name of mapping type
        model = Name of model, i.e., account.account
        field = Database field, i.e., code
        in_value = Value in PABI2
        return: out_value
        """
        out_value = False
        if in_value:
            in_value = str(in_value)
            if in_value[-2:] == '.0':
                in_value = in_value[:-2]
            out_value = self.search(
                [('map_type_id.name', '=', map_type),
                 ('model_id.model', '=', model),
                 ('field_id.name', '=', field),
                 ('in_value', '=', in_value)],
                limit=1).out_value
        if isinstance(out_value, basestring):
            out_value = out_value.encode('utf-8')
        return out_value

    @api.model
    def get_in_value(self, map_type, model, field, out_value=False):
        """
        map_type = Name of mapping type
        model = Name of model, i.e., account.account
        field = Database field, i.e., code
        out_value = Value of other system
        return: in_value
        """
        in_value = False
        if out_value:
            out_value = str(out_value)
            if out_value[-2:] == '.0':
                out_value = out_value[:-2]
            in_value = self.search(
                [('map_type_id.name', '=', map_type),
                 ('model_id.model', '=', model),
                 ('field_id.name', '=', field),
                 ('out_value', '=', out_value)],
                limit=1).in_value
        return in_value


class PABIDataMapType(models.Model):
    _name = 'pabi.data.map.type'
    _description = 'Type of data map, will be created for each application'

    name = fields.Char(
        string='Name',
        required=True,
    )
    line_ids = fields.One2many(
        'pabi.data.map',
        'map_type_id',
        string='Map Details',
        ondelete='cascade',
        index=True,
    )
    app_name = fields.Selection(
        [],  # to be added for the calling apps.
        string='Application',
        help="Application can be used to group multiple map types",
    )
    default_template_id = fields.Many2one(
        'ir.attachment',
        string='Default Template',
        help="Default Template used during import/export xlxs",
    )
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be unique!'),
    ]
