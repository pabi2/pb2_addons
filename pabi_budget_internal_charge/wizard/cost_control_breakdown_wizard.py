# -*- coding: utf-8 -*-
from openerp import api, models, fields


class CostControlBreakdown(models.TransientModel):
    _inherit = "cost.control.breakdown"

    @api.model
    def default_get(self, fields):
        """ OVERWWITE """
        res = super(CostControlBreakdown, self).default_get(fields)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        costcontrol = self.env[active_model].browse(active_id)
        res['breakdown_line_ids'] = []
        for line in costcontrol.detail_ids:
            vals = {
                # Add here
                'charge_type': line.charge_type,
                # --
                'activity_group_id': line.activity_group_id.id,
                'activity_id': line.activity_id.id,
                'cost_control_id': line.cost_control_id.id,
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
            res['breakdown_line_ids'].append((0, 0, vals))
        return res

    @api.multi
    def submit_cost_control_breakdown(self):
        """ OVERWIRTE (for now) """
        self.ensure_one()
        active_id = self.env.context.get('active_id', False)
        active_model = self._context.get('active_model')
        costcontrol = self.env[active_model].browse(active_id)
        if costcontrol:
            costcontrol.detail_ids.unlink()
            ids = []
            for line in self.breakdown_line_ids:
                vals = {
                    # Add here
                    'charge_type': line.charge_type,
                    # --
                    'plan_id': costcontrol.plan_id.id,
                    'fk_costcontrol_id': costcontrol.id,
                    'section_id': costcontrol.plan_id.section_id.id,
                    'activity_group_id': line.activity_group_id.id,
                    'activity_id': line.activity_id.id,
                    'cost_control_id': costcontrol.cost_control_id.id,
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
                new_id = self.env['budget.plan.unit.line'].create(vals).id
                ids.append(new_id)
            costcontrol.write({'detail_ids': [(6, 0, ids)]})
        return True


class CostControlBreakdownLine(models.TransientModel):
    _inherit = "cost.control.breakdown.line"

    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
        required=True,
        default='external',
        help="Specify whether the budget plan line is for Internal Charge or "
        "External Charge. Internal charged is for Unit Based only."
    )
