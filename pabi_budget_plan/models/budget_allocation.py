# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp import tools
from openerp.exceptions import ValidationError


class BudgetAllocation(models.Model):
    _name = 'budget.allocation'
    _auto = False
    # _inherit = ['mail.thread']
    _description = 'Budget Allocation'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscalyear',
        index=True,
        ondelete='cascade',
    )
    revision = fields.Integer(
        string='Revision',
        readonly=True,
        help="Revision number",
    )
    # Amount
    amount_unit_base = fields.Float(
        string='Unit Based',
        compute='_compute_amount',
    )
    amount_project_base = fields.Float(
        string='Project Based',
        compute='_compute_amount',
    )
    amount_personnel = fields.Float(
        string='Personnel Budget',
        compute='_compute_amount',
    )
    amount_invest_asset = fields.Float(
        string='Invest Asset',
        compute='_compute_amount',
    )
    amount_invest_construction = fields.Float(
        string='Invest Construction',
        compute='_compute_amount',
    )
    amount_total = fields.Float(
        string='Total',
        compute='_compute_amount',
    )
    # Policy ID
    unit_base_policy_id = fields.Many2one(
        'budget.policy',
        string='Unit Based',
        compute='_compute_policy_id',
    )
    project_base_policy_id = fields.Many2one(
        'budget.policy',
        string='Project Based',
        compute='_compute_policy_id',
    )
    personnel_policy_id = fields.Many2one(
        'budget.policy',
        string='Personnel',
        compute='_compute_policy_id',
    )
    invest_asset_policy_id = fields.Many2one(
        'budget.policy',
        string='Invest Asset',
        compute='_compute_policy_id',
    )
    invest_construction_policy_id = fields.Many2one(
        'budget.policy',
        string='Invest Construction',
        compute='_compute_policy_id',
    )
    _sql_constraints = [
        ('uniq_revision', 'unique(fiscalyear_id, revision)',
         'Duplicated revision of budget policy is not allowed!'),
    ]

    @api.multi
    def _compute_amount(self):
        chartviews = {'unit_base': 'amount_unit_base',
                      'project_base': 'amount_project_base',
                      'personnel': 'amount_personnel',
                      'invest_asset': 'amount_invest_asset',
                      'invest_construction': 'amount_invest_construction', }
        Policy = self.env['budget.policy']
        for rec in self:
            amount_total = 0.0
            # All policyes of the same revision / fiscalyear
            policies = Policy.search(
                [('revision', '=', rec.revision),
                 ('fiscalyear_id', '=', rec.fiscalyear_id.id)])
            for chart_view in chartviews:
                p = policies.filtered(lambda l: l.chart_view == chart_view)
                rec[chartviews[chart_view]] = p.new_policy_amount
                amount_total += p.new_policy_amount
            rec.amount_total = amount_total

    @api.multi
    def _compute_policy_id(self):
        chartviews = {
            'unit_base': 'unit_base_policy_id',
            'project_base': 'project_base_policy_id',
            'personnel': 'personnel_policy_id',
            'invest_asset': 'invest_asset_policy_id',
            'invest_construction': 'invest_construction_policy_id',
        }
        Policy = self.env['budget.policy']
        for rec in self:
            # All policyes of the same revision / fiscalyear
            policies = Policy.search(
                [('revision', '=', rec.revision),
                 ('fiscalyear_id', '=', rec.fiscalyear_id.id)])
            for chart_view in chartviews:
                p = policies.filtered(lambda l: l.chart_view == chart_view)
                rec[chartviews[chart_view]] = p

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        _sql = """
        select row_number() over (order by fiscalyear_id, revision) as id, *
        from (select distinct fiscalyear_id, revision
            from budget_policy
            order by fiscalyear_id, revision) a
        """
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, _sql))

    @api.multi
    def open_unit_base_policy(self):
        self.ensure_one()
        return self.open_policy(self.unit_base_policy_id.id)

    @api.multi
    def open_project_base_policy(self):
        self.ensure_one()
        return self.open_policy(self.project_base_policy_id.id)

    @api.multi
    def open_personnel_policy(self):
        self.ensure_one()
        return self.open_policy(self.personnel_policy_id.id)

    @api.multi
    def open_invest_asset_policy(self):
        self.ensure_one()
        return self.open_policy(self.invest_asset_policy_id.id)

    @api.multi
    def open_invest_construction_policy(self):
        self.ensure_one()
        return self.open_policy(self.invest_construction_policy_id.id)

    @api.model
    def open_policy(self, policy_id):
        if not policy_id:
            raise ValidationError(_('No related policy!'))
        view = self.env.ref('pabi_budget_plan.view_budget_policy_form')
        result = {
            'name': _("Budget Policy"),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'budget.policy',
            'view_id': view.id,
            'res_id': policy_id,
            'type': 'ir.actions.act_window',
            'context': {},
            'nodestroy': True,
        }
        return result
