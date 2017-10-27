# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class ImportXLSXSpecialProject(models.TransientModel):
    _name = 'import.xlsx.special.project'

    map_type_id = fields.Many2one(
        'pabi.data.map.type',
        string='Project',
        required=True,
        domain="[('app_name', '=', 'special_project')]",
    )
    template_id = fields.Many2one(
        'ir.attachment',
        string='Template',
    )
    import_file = fields.Binary(
        string='Import File (*.xlsx)',
        required=True,
    )

    @api.onchange('map_type_id')
    def _onchange_map_type_id(self):
        if self.map_type_id and not self.map_type_id.default_template_id:
            raise ValidationError(
                _('%s has no default template!') % self.map_type_id.name)
        self.template_id = self.map_type_id.default_template_id

    @api.multi
    def action_import(self):
        self.ensure_one()
        if not self.import_file:
            raise ValidationError(_('Please choose excel file to import!'))
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        ctx = {'map_type': self.map_type_id.name}
        Import = self.env['import.xlsx.template']
        Import.with_context(ctx).import_template(self.import_file,
                                                 self.template_id,
                                                 active_model, active_id)
        return
