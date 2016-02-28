# -*- coding: utf-8 -*-
from openerp import api, models
from .chartfield import \
    ChartField


class PurchaseOrderLine(ChartField, models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('costcenter_id')
    def _onchange_costcenter_id(self):
        self.mission_id = self.costcenter_id.mission_id
        self.spa_id = self.costcenter_id.program_id.current_spa_id  # Current
        self.program_base_type_id = self.costcenter_id.program_base_type_id
        self.program_type_id = self.costcenter_id.program_type_id
        self.program_id = self.costcenter_id.program_id
        self.org_id = self.costcenter_id.org_id
        self.project_id = False
        self.division_id = self.costcenter_id.division_id
        self.department_id = self.costcenter_id.department_id
        self.costcenter_id = self.costcenter_id

    @api.onchange('project_id')
    def _onchange_project_id(self):
        self.mission_id = self.project_id.mission_id
        self.spa_id = self.project_id.program_id.current_spa_id  # Current SPA
        self.program_base_type_id = self.project_id.program_base_type_id
        self.program_type_id = self.project_id.program_type_id
        self.program_id = self.project_id.program_id
        self.org_id = self.project_id.org_id
        self.project_id = self.project_id
        self.division_id = False
        self.department_id = False
        self.costcenter_id = False
