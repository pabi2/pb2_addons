# -*- coding: utf-8 -*-
from openerp import api, models
from .chartfield import \
    ChartField


class PurchaseRequisitionLine(ChartField, models.Model):
    _inherit = 'purchase.requisition.line'

    @api.onchange('costcenter_id')
    def _onchange_costcenter_id(self):

        self.org_id = self.costcenter_id.org_id
        self.sector_id = self.costcenter_id.sector_id
        self.division_group_id = self.costcenter_id.division_group_id
        self.division_id = self.costcenter_id.division_id
        self.department_id = self.costcenter_id.department_id
        self.costcenter_id = self.costcenter_id

        self.spa_id = False
        self.mission_id = False
        self.program_scheme_id = False
        self.program_group_id = False
        self.program_id = False
        self.project_group_id = False
        self.project_id = False

    @api.onchange('project_id')
    def _onchange_project_id(self):

        self.org_id = False
        self.sector_id = False
        self.division_group_id = False
        self.division_id = False
        self.department_id = False
        self.costcenter_id = False

        self.spa_id = self.project_id.program_id.current_spa_id
        self.mission_id = self.project_id.mission_id
        self.program_scheme_id = self.project_id.program_scheme_id
        self.program_group_id = self.project_id.program_group_id
        self.program_id = self.project_id.program_id
        self.project_group_id = self.project_id.project_group_id
        self.project_id = self.project_id
