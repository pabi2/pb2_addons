# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.addons.pabi_chartfield.models.chartfield import CHART_VIEW_FIELD


class BudgetPlanUnit(models.Model):
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
    amount_budget_request = fields.Float(
        string='Budget Request',
        compute='_compute_budget_request',
        store=True,
    )
    amount_budget_policy = fields.Float(
        string='Budget Policy',
    )

    @api.multi
    @api.depends('plan_line_ids')
    def _compute_budget_request(self):
        for rec in self:
            planned_amounts = rec.plan_line_ids.mapped('planned_amount')
            rec.amount_budget_request = sum(planned_amounts)

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

    @api.multi
    def button_submit(self):
        for rec in self:
            res = rec.template_id.\
                _get_chained_dimension(CHART_VIEW_FIELD[rec.chart_view])
            rec.write(res)
            for line in rec.plan_line_ids:
                res = line.mapped('template_id').\
                    _get_chained_dimension(CHART_VIEW_FIELD[line.chart_view])
                line.write(res)
        return self.mapped('template_id').button_submit()

    @api.multi
    def button_draft(self):
        return self.mapped('template_id').button_draft()

    @api.multi
    def button_cancel(self):
        return self.mapped('template_id').button_cancel()

    @api.multi
    def button_reject(self):
        return self.mapped('template_id').button_reject()

    @api.multi
    def button_approve(self):
        return self.mapped('template_id').button_approve()

    @api.model
    def _prepare_copy_fields(self, source_model, target_model):
        src_fields = [f for f, _x in source_model._fields.iteritems()]
        no_fields = [
            'id', 'state', 'display_name', '__last_update', 'state'
            'write_date', 'create_date', 'create_uid', 'write_uid',
            'date', 'date_approve', 'date_submit', 'date_from', 'date_to',
            'template_id', 'validating_user_id', 'creating_user_id',
        ]
        trg_fields = [f for f, _x in target_model._fields.iteritems()]
        return list((set(src_fields) & set(trg_fields)) - set(no_fields))

    @api.model
    def convert_plan_to_budget_control(self, active_ids):
        head_src_model = self.env['budget.plan.unit']
        head_trg_model = self.env['account.budget']
        line_src_model = self.env['budget.plan.unit.line']
        line_trg_model = self.env['account.budget.line']

        header_fields = self._prepare_copy_fields(head_src_model,
                                                  head_trg_model)
        line_fields = self._prepare_copy_fields(line_src_model,
                                                line_trg_model)

        for plan in self.browse(active_ids):
            vals = {}
            for key in header_fields:
                vals.update({key: (hasattr(plan[key], '__iter__') and
                                   plan[key].id or plan[key])})
            budget = head_trg_model.create(vals)
            for line in plan.plan_line_ids:
                for key in line_fields:
                    vals.update({key: (hasattr(line[key], '__iter__') and
                                       line[key].id or line[key])})
                vals.update({'budget_id': budget.id})
                line_trg_model.create(vals)


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
