# -*- coding: utf-8 -*-
import os
import base64
from openerp import SUPERUSER_ID, tools
from openerp import models, fields, api


class Attachment(models.Model):
    _inherit = 'ir.attachment'

    budget_template_type = fields.Selection(
        selection=[
            ('plan_unit_based', 'Unit Based'),
            ('plan_invest_asset_plan', 'Invest Asset Item'),
        ]
    )
    budget_plan_id = fields.Many2one(
        'budget.plan.unit',
        string="Budget Plan",
        copy=False,
    )
    invest_asset_plan_id = fields.Many2one(
        'invest.asset.plan',
        string="Invest Asset Plan",
        copy=False,
    )

    @api.model
    def _create_plan_template(self, type, filename):
        templates = self.search_count([('budget_template_type', '=', type)])
        if templates < 1:
            path = os.path.join('pabi_budget_xls', 'template', filename)
            image_file = tools.file_open(path, 'rb')
            try:
                file_data = image_file.read()
                self.create({
                    'name': 'Export Template -' + filename,
                    'datas': base64.encodestring(file_data),
                    'datas_fname': filename,
                    'description': 'Export Template -' + filename,
                    'budget_template_type': type,
                })
            except:
                pass

    def init(self, cr):
        if 'budget.plan.unit' not in self._models_check:
            self._models_check.update({'budget.plan.unit': 'budget_plan_id'})
        if 'invest.asset.plan' not in self._models_check:
            self._models_check.update(
                {'invest.asset.plan': 'invest_asset_plan_id'})
        self._create_plan_template(
            cr, SUPERUSER_ID, 'plan_unit_based',
            'BudgetPlan_UnitBased.xlsx')
        self._create_plan_template(
            cr, SUPERUSER_ID, 'plan_invest_asset_plan',
            'BudgetPlan_InvestmentAssetItem.xlsx')
