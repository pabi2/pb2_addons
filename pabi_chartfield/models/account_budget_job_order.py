# -*- coding: utf-8 -*-
import openerp.addons.decimal_precision as dp
from openerp import models, fields, api


class BudgetUnitJobOrder(models.Model):
    _name = 'budget.unit.job.order'

    budget_id = fields.Many2one(
        'account.budget',
        string='Budget Control',
        ondelete='cascade',
        index=True,
        required=True,
    )
    cost_control_id = fields.Many2one(
        'cost.control',
        string='Job Order',
    )
    amount_total = fields.Float(
        string='Total Amount',
        compute='_compute_amount_total',
    )
#     detail_ids = fields.One2many(
#         'account.budget.line',
#         'fk_costcontrol_id',
#         string='Job Order Detail',
#     )
    plan_cost_control_line_ids = fields.One2many(
        'budget.unit.job.order.line',
        'cost_control_line_id',
        string="Job Order Lines",
        copy=False,
    )

    @api.multi
    @api.depends('plan_cost_control_line_ids')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = \
                sum([x.planned_amount for x in rec.plan_cost_control_line_ids])


class BudgetUnitJobOrderLine(models.Model):
    _name = 'budget.unit.job.order.line'

    cost_control_line_id = fields.Many2one(
        'budget.unit.job.order',
        string='Job Order Line',
        index=True,
        ondelete='cascade',
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        domain="[('activity_group_ids', 'in', activity_group_id)]",
    )
    name = fields.Char(
        string='Description',
    )
    m1 = fields.Float(
        string='Oct',
    )
    m2 = fields.Float(
        string='Nov',
    )
    m3 = fields.Float(
        string='Dec',
    )
    m4 = fields.Float(
        string='Jan',
    )
    m5 = fields.Float(
        string='Feb',
    )
    m6 = fields.Float(
        string='Mar',
    )
    m7 = fields.Float(
        string='Apr',
    )
    m8 = fields.Float(
        string='May',
    )
    m9 = fields.Float(
        string='Jun',
    )
    m10 = fields.Float(
        string='Jul',
    )
    m11 = fields.Float(
        string='Aug',
    )
    m12 = fields.Float(
        string='Sep',
    )
    planned_amount = fields.Float(
        string='Planned Amount',
        compute='_compute_planned_amount',
        digits_compute=dp.get_precision('Account'),
        store=True,
    )
    activity_unit_price = fields.Float(
        string="Unit Price",
    )
    activity_unit = fields.Float(
        string="Activity Unit",
    )
    unit = fields.Float(
        string="Unit",
    )
    total_budget = fields.Float(
        string="Total Budget",
        compute="_compute_total_budget",
    )

    @api.depends('unit',
                 'activity_unit',
                 'activity_unit_price')
    def _compute_total_budget(self):
        for line in self:
            line.total_budget =\
                line.unit * line.activity_unit * line.activity_unit_price

    @api.multi
    def write(self, vals):
        for record in self:
            line_exist = self.env['account.budget.line'].\
                search([('breakdown_line_id', '=', record.id)])
            if line_exist:
                line_exist.write(vals)
        return super(BudgetUnitJobOrderLine, self).write(vals)

    @api.multi
    @api.depends('m1', 'm2', 'm3', 'm4', 'm5', 'm6',
                 'm7', 'm8', 'm9', 'm10', 'm11', 'm12',)
    def _compute_planned_amount(self):
        for rec in self:
            planned_amount = sum([rec.m1, rec.m2, rec.m3, rec.m4,
                                  rec.m5, rec.m6, rec.m7, rec.m8,
                                  rec.m9, rec.m10, rec.m11, rec.m12
                                  ])
            rec.planned_amount = planned_amount  # from last year
