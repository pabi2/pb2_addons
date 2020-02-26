# -*- coding: utf-8 -*-
import ast
from openerp import api, models, fields


class ProjectInterfaceWizard(models.TransientModel):
    _name = "project.interface.wizard"
    _description = 'Update Project by Interface Test'

    data_dict = fields.Text(
        string='Data Dict',
        required=True,
    )

    @api.multi
    def action_update_project(self):
        self.ensure_one()
        active_id = self._context.get('active_id', False)
        res_project = self.env['res.project'].search([('id', '=', active_id)])
        # change unicode to dict
        data_dict = ast.literal_eval(self.data_dict)
        res_project.update_project(data_dict)
        return True
