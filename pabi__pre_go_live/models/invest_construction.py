# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ResInvestConstruction(models.Model):
    _inherit = 'res.invest.construction'

    @api.multi
    @api.depends('phase_ids.amount_phase_approve')
    def _compute_amount_phase_approve(self):
        for rec in self:
            amount_total = sum([x.amount_phase_approve for x in rec.phase_ids])
            # FOR MIGRATION: remove this check temporarilly
            # if amount_total and float_compare(amount_total,
            #                                   rec.amount_budget,
            #                                   precision_digits=2) != 0:
            #     raise ValidationError(
            #         _("Sum of all phases approved budget <> "
            #           "Project's approved budget"))
            rec.amount_phase_approve = amount_total
