# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.addons.pabi_chartfield.models.chartfield import \
    CHART_VIEW_LIST, CHART_VIEW_FIELD, ChartField


class BudgetPrepareUnit(models.Model):
    _name = 'budget.prepare.unit'
    _inherits = {'budget.prepare.template': 'template_id'}
    _description = "Unit Based - Budget Prepare"

    template_id = fields.Many2one(
        'budget.prepare.template',
        required=True,
        ondelete='cascade',
    )
    prepare_line_ids = fields.One2many(
        'budget.prepare.unit.line',
        'prepare_id',
        string='Budget Prepare Lines',
        copy=False,
    )
    cost_control_ids = fields.One2many(
        'budget.prepare.unit.cost.control',
        'prepare_id',
        string='Cost Control',
        copy=True,
    )

    @api.onchange('section_id')
    def _onchange_section_id(self):
        self.org_id = self.section_id.org_id

    # Call inherited methods
    @api.multi
    def unlink(self):
        self.prepare_line_ids.mapped('template_id').unlink()
        self.mapped('template_id').unlink()
        return super(BudgetPrepareUnit, self).unlink()

    @api.multi
    def button_submit(self):
        for rec in self:
            res = rec.template_id.\
                _get_chained_dimension(CHART_VIEW_FIELD[rec.chart_view])
            rec.write(res)
            for line in rec.prepare_line_ids:
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


class BudgetPrepareUnitLine(models.Model):
    _name = 'budget.prepare.unit.line'
    _inherits = {'budget.prepare.line.template': 'template_id'}
    _description = "Unit Based - Budget Prepare Line"

    chart_view = fields.Selection(
        related='prepare_id.chart_view',
        store=True,
    )
    prepare_id = fields.Many2one(
        'budget.prepare.unit',
        string='Budget Prepare',
        ondelete='cascade',
        index=True,
        required=True,
    )
    fk_costcontrol_id = fields.Many2one(
        'budget.prepare.unit.cost.control',
        string='FK Cost Control',
        ondelete='cascade',
        index=True,
    )
    template_id = fields.Many2one(
        'budget.prepare.line.template',
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

    @api.multi
    def unlink(self):
        self.mapped('template_id').unlink()
        return super(BudgetPrepareUnitLine, self).unlink()


class BudgetPrepareUnitCostControl(models.Model):
    _name = 'budget.prepare.unit.cost.control'

    prepare_id = fields.Many2one(
        'budget.prepare.unit',
        string='Budget Prepare',
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
        'budget.prepare.unit.line',
        'fk_costcontrol_id',
        string='Cost Control Detail',
    )

    @api.multi
    @api.depends('detail_ids')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum([x.planned_amount for x in rec.detail_ids])
