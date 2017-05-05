# -*- coding: utf-8 -*-
from openerp import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    transdebt_partner_ids = fields.Many2many(
        'res.partner',
        'res_partner_transdebt_partner_rel',
        'partner_id', 'transdebt_partner_id',
        string='Debt Transfer Partners',
        help="These partners will be avialble for selection in "
        "Supplier Payment, if user choose to transfer debit to "
        "other supplier. And it will be used in Payment Export.",
    )
