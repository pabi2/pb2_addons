# -*- coding: utf-8 -*-
from openerp import tools
from openerp import api, models, fields
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


class ChartfieldView(models.Model):
    _name = 'chartfield.view'
    _auto = False
    _order = 'seq, code'

    seq = fields.Integer(
        string='Sequence',
    )
    type = fields.Selection(
        [('sc:', 'Section'),
         ('pj:', 'Project'),
         ('cp:', 'Construction Phase'),
         ('ia:', 'Invest Asset'),
         ('pc:', 'Personnel'), ],
        string='Type',
    )
    model = fields.Char(
        string='Model',
    )
    id = fields.Integer(
        string='ID',
    )
    res_id = fields.Integer(
        string='Resource ID',
    )
    code = fields.Char(
        string='Code',
    )
    name = fields.Char(
        string='Name',
    )
    name_short = fields.Char(
        string='Short Name',
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter',
    )
    active = fields.Boolean(
        string='Active',
    )

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            name = rec.name
            name_short = ('name_short' in rec) and rec['name_short'] or False
            result.append((rec.id, "%s%s" %
                           (rec.code and '[' + rec.code + '] ' or '',
                            name_short or name or '')))
        return result

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        _sql = """
        select * from (
        (select 1 seq, 'sc:' as type, 'res.section' as model,
        id+1000000 as id, id as res_id, code, name,
        name_short, costcenter_id, active
        from res_section)
            union all
        (select 2 seq, 'pj:' as type, 'res.project' as model,
        id+2000000 as id, id as res_id, code, name, name_short,
        costcenter_id, active
        from res_project)
            union all
        (select 3 seq, 'cp:' as type, 'res.invest.construction.phase' as model,
        p.id+3000000 as id, p.id as res_id, p.code, c.name as name,
        phase as name_short, p.costcenter_id, p.active
        from res_invest_construction_phase p join res_invest_construction c on
        c.id = p.invest_construction_id)
            union all
        (select 4 seq, 'ia:' as type, 'res.invest.asset' as model,
        id+4000000 as id, id as res_id, code, name, name_short,
        costcenter_id, active
        from res_invest_asset)
            union all
        (select 5 seq, 'pc:' as type, 'res.personnel.costcenter' as model,
        id+5000000 as id, id as res_id, code, name, name_short,
        costcenter_id, active
        from res_personnel_costcenter)
        ) a
        """
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, _sql,))
