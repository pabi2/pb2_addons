# -*- coding: utf-8 -*-
# © 2016 Kitti U.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResDoctype(models.Model):
    _inherit = 'res.doctype'

    with_reversal = fields.Boolean(
        string='With Reversal',
        default=False,
    )
    reversal_sequence_id = fields.Many2one(
        'ir.sequence',
        string='Sequence',
        domain=[('special_type', '=', 'doctype')],
    )
    fiscal_reversal_sequence_ids = fields.One2many(
        related='reversal_sequence_id.fiscal_ids',
        string='Reversal Sequences by fiscalyear',
    )
