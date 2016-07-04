# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .budget_plan_template import BudgetPlanCommon


class BudgetPlanUnit(BudgetPlanCommon, models.Model):
    _name = 'budget.plan.unit'
    _inherits = {'budget.plan.template': 'template_id'}
    _description = "Unit Based - Budget Plan"

    template_id = fields.Many2one(
        'budget.plan.template',
        required=True,
        ondelete='cascade',
    )
    plan_line_ids = fields.One2many(
        'budget.plan.unit.line',
        'plan_id',
        string='Budget Plan Lines',
        copy=False,
    )
    cost_control_ids = fields.One2many(
        'budget.plan.unit.cost.control',
        'plan_id',
        string='Cost Control',
        copy=True,
    )
    planned_overall = fields.Float(
        string='Budget Plan',
        compute='_compute_planned_overall',
        store=True,
    )

    @api.onchange('section_id')
    def _onchange_section_id(self):
        self.org_id = self.section_id.org_id

    # Call inherited methods
    @api.multi
    def unlink(self):
        for rec in self:
            rec.plan_line_ids.mapped('template_id').unlink()
        self.mapped('template_id').unlink()
        return super(BudgetPlanUnit, self).unlink()

    @api.model
    def convert_plan_to_budget_control(self, active_ids):
        head_src_model = self.env['budget.plan.unit']
        line_src_model = self.env['budget.plan.unit.line']

        self._convert_plan_to_budget_control(active_ids,
                                             head_src_model,
                                             line_src_model)


class BudgetPlanUnitLine(models.Model):
    _name = 'budget.plan.unit.line'
    _inherits = {'budget.plan.line.template': 'template_id'}
    _description = "Unit Based - Budget Plan Line"

    plan_id = fields.Many2one(
        'budget.plan.unit',
        string='Budget Plan',
        ondelete='cascade',
        index=True,
        required=True,
    )
    fk_costcontrol_id = fields.Many2one(
        'budget.plan.unit.cost.control',
        string='FK Cost Control',
        ondelete='cascade',
        index=True,
    )
    template_id = fields.Many2one(
        'budget.plan.line.template',
        required=True,
        ondelete='cascade',
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
    )

    @api.model
    def create(self, vals):
        res = super(BudgetPlanUnitLine, self).create(vals)
        res.write({'chart_view': res.plan_id.chart_view,
                   'fiscalyear_id': res.plan_id.fiscalyear_id.id})
        return res

    @api.multi
    def unlink(self):
        self.mapped('template_id').unlink()
        return super(BudgetPlanUnitLine, self).unlink()


class BudgetPlanUnitCostControl(models.Model):
    _name = 'budget.plan.unit.cost.control'

    plan_id = fields.Many2one(
        'budget.plan.unit',
        string='Budget Plan',
        ondelete='cascade',
        index=True,
        required=True,
    )
    cost_control_id = fields.Many2one(
        'cost.control',
        string='Cost Control',
    )
    amount_total = fields.Float(
        string='Total Amount',
        compute='_compute_amount_total',
    )
    detail_ids = fields.One2many(
        'budget.plan.unit.line',
        'fk_costcontrol_id',
        string='Cost Control Detail',
    )

    @api.multi
    @api.depends('detail_ids')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum([x.planned_amount for x in rec.detail_ids])
