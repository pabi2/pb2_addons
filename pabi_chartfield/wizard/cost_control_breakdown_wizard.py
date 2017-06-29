# -*- coding: utf-8 -*-
from openerp import api, models, fields
import openerp.addons.decimal_precision as dp


class JobOrderBreakdown(models.TransientModel):
    _name = "budget.job.order.breakdown"

    breakdown_costcontrol_line_ids = fields.Many2many(
        'budget.unit.job.order.line',
        'job_order_id',
        'budget_id',
        string='Breakdown Lines',
    )
    cost_control_line_id = fields.Many2one(
        'budget.unit.job.order',
        string='Job Order Line',
        readonly=True,
    )

    @api.model
    def default_get(self, fields):
        res = super(JobOrderBreakdown, self).default_get(fields)
        active_id = self._context.get('active_id')
        res['breakdown_costcontrol_line_ids'] = []
        line_ids = self.env['budget.unit.job.order.line'].search(
            [('cost_control_line_id', '=', active_id)])
        res['breakdown_costcontrol_line_ids'] = tuple(line_ids.ids)
        res['cost_control_line_id'] = active_id
        return res

    @api.model
    def _prepare_breakdown_line_dict(self, line):
        vals = {
            'activity_group_id': line.activity_group_id.id,
            'activity_id': line.activity_id.id,
            'activity_unit_price': line.activity_unit_price,
            'activity_unit': line.activity_unit,
            'unit': line.unit,
            'm1': line.m1,
            'm2': line.m2,
            'm3': line.m3,
            'm4': line.m4,
            'm5': line.m5,
            'm6': line.m6,
            'm7': line.m7,
            'm8': line.m8,
            'm9': line.m9,
            'm10': line.m10,
            'm11': line.m11,
            'm12': line.m12,
        }
        return vals

    @api.multi
    def submit_cost_control_breakdown(self):
        for record in self:
            active_id = self.env.context.get('active_id', False)
            active_model = self._context.get('active_model')
            costcontrol = self.env[active_model].browse(active_id)
            if costcontrol:
                ids = []
                for line in record.breakdown_costcontrol_line_ids:
                    vals = self._prepare_breakdown_line_dict(line)
                    line_exist = self.env['account.budget.line'].search(
                        [('budget_id', '=', costcontrol.budget_id.id),
                         ('breakdown_line_id', '=', line.id)])
                    if line_exist:
                        line_exist.write(vals)
                        ids.append(line_exist.id)
                    else:
                        create_vals = {
                            'breakdown_line_id': line.id,
                            'budget_id': costcontrol.budget_id.id,
                            'fk_costcontrol_id': costcontrol.id,
                            'section_id': costcontrol.budget_id.section_id.id,
                            'cost_control_id': costcontrol.cost_control_id.id,
                        }
                        create_vals.update(vals)
                        new_id = self.env['account.budget.line'].\
                            create(create_vals).id
                        ids.append(new_id)
        return True


class JobOrderBreakdownLine(models.TransientModel):
    _name = "budget.job.order.breakdown.line"

    breakdown_id = fields.Many2one(
        'budget.job.order.breakdown',
        string='Job Order Breakdown',
        ondelete='cascade',
        index=True,
        required=True,
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
