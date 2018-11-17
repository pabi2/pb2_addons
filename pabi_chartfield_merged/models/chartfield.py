# -*- coding: utf-8 -*-
from openerp import api, fields
from openerp.addons.pabi_chartfield.models.chartfield import ChartField


class MergedChartField(ChartField):

    chartfield_id = fields.Many2one(
        'chartfield.view',
        string='Budget',
        compute='_compute_chartfield',
        inverse='_inverse_chartfield',
        domain=[('model', '!=', 'res.personnel.costcenter')],
    )

    @api.multi
    @api.depends('chartfield_id')
    def _inverse_chartfield(self):
        for rec in self:
            res_id = rec.chartfield_id.res_id
            model = rec.chartfield_id.model
            vals = {'section_id': False, 'project_id': False,
                    'invest_asset_id': False, 'personnel_costcenter_id': False,
                    'invest_construction_phase_id': False}
            if model == 'res.section':
                vals.update({'section_id': res_id})
            if model == 'res.project':
                vals.update({'project_id': res_id})
            if model == 'res.invest.construction.phase':
                vals.update({'invest_construction_phase_id': res_id})
            if model == 'res.invest.asset':
                vals.update({'invest_asset_id': res_id})
            if model == 'res.personnel.costcenter':
                vals.update({'personnel_costcenter_id': res_id})
            rec.write(vals)

    @api.multi
    @api.depends('project_id', 'section_id', 'personnel_costcenter_id',
                 'invest_asset_id', 'invest_construction_id')
    def _compute_chartfield(self):
        for rec in self:
            model, res_id = False, False
            if rec.section_id:
                model, res_id = ('res.section', rec.section_id.id)
            if rec.project_id:
                model, res_id = ('res.project', rec.project_id.id)
            if rec.invest_asset_id:
                model, res_id = ('res.invest.asset', rec.invest_asset_id.id)
            if rec.invest_construction_phase_id:
                model, res_id = ('res.invest.construction.phase',
                                 rec.invest_construction_phase_id.id)
            if rec.personnel_costcenter_id:
                model, res_id = ('res.personnel.costcenter',
                                 rec.personnel_costcenter_id.id)
            if res_id:
                Chart = self.env['chartfield.view']
                rec.chartfield_id = Chart.with_context(active_test=False).\
                    search([('model', '=', model), ('res_id', '=', res_id)])
            else:
                rec.chartfield_id = False

    @api.onchange('chartfield_id')
    def _onchange_chartfield_id(self):
        res_id = self.chartfield_id.res_id
        if self.chartfield_id.model == 'res.section':
            self.section_id = res_id
        if self.chartfield_id.model == 'res.project':
            self.project_id = res_id
        if self.chartfield_id.model == 'res.invest.construction.phase':
            self.invest_construction_phase_id = res_id
        if self.chartfield_id.model == 'res.invest.asset':
            self.invest_asset_id = res_id
        if self.chartfield_id.model == 'res.personnel.costcenter':
            self.personnel_costcenter_id = res_id
