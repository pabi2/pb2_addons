# -*- coding: utf-8 -*-
from openerp import api, models, fields
import openerp.addons.decimal_precision as dp


class CostControlBreakdown(models.TransientModel):
    _name = "cost.control.breakdown"

    breakdown_line_ids = fields.One2many(
        'cost.control.breakdown.line',
        'breakdown_id',
        string='Breakdown Lines',
    )
    breakdown_costcontrol_line_ids = fields.Many2many(
        'budget.plan.unit.cost.control.line',
        string='Breakdown Lines',
    )
    cost_control_line_id = fields.Many2one(
        'budget.plan.unit.cost.control',
        string='Job Order Line',
        readonly=True,
    )

    @api.model
    def default_get(self, fields):
        res = super(CostControlBreakdown, self).default_get(fields)
        active_id = self._context.get('active_id')
        res['breakdown_costcontrol_line_ids'] = []
        line_ids = self.env['budget.plan.unit.cost.control.line'].search(
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
            'm0': line.m0,
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
                    line_exist = self.env['budget.plan.unit.line'].search(
                        [('plan_id', '=', costcontrol.plan_id.id),
                         ('breakdown_line_id', '=', line.id)])
                    if line_exist:
                        line_exist.write(vals)
                        ids.append(line_exist.id)
                    else:
                        create_vals = {
                            'breakdown_line_id': line.id,
                            'plan_id': costcontrol.plan_id.id,
                            'fk_costcontrol_id': costcontrol.id,
                            'section_id': costcontrol.plan_id.section_id.id,
                            'cost_control_id': costcontrol.cost_control_id.id,
                        }
                        create_vals.update(vals)
                        new_id = self.env['budget.plan.unit.line'].\
                            create(create_vals).id
                        ids.append(new_id)
                costcontrol.write({'detail_ids': [(6, 0, ids)]})
        return True


class CostControlBreakdownLine(models.TransientModel):
    _name = "cost.control.breakdown.line"

    breakdown_id = fields.Many2one(
        'cost.control.breakdown',
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
    m0 = fields.Float(
        string='0',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m1 = fields.Float(
        string='1',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m2 = fields.Float(
        string='2',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m3 = fields.Float(
        string='3',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m4 = fields.Float(
        string='4',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m5 = fields.Float(
        string='5',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m6 = fields.Float(
        string='6',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m7 = fields.Float(
        string='7',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m8 = fields.Float(
        string='8',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m9 = fields.Float(
        string='9',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m10 = fields.Float(
        string='10',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m11 = fields.Float(
        string='11',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m12 = fields.Float(
        string='12',
        required=False,
        digits_compute=dp.get_precision('Account'),
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
            rec.planned_amount = planned_amount + rec.m0  # from last year
