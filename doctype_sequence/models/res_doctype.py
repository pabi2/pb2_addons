# -*- coding: utf-8 -*-
# © 2016 Kitti U.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResDoctype(models.Model):
    _name = 'res.doctype'
    _description = 'Doctype'

    name = fields.Char(
        string='Name',
        readonly=True,
    )
    refer_type = fields.Selection([
        ('sale', 'Sale Receipt'),
        ('purchase', 'Purchase Receipt'),
        ('payment', 'Supplier Payment'),
        ('receipt', 'Customer Payment'),
        ],
        string='Refer to window',
        readonly=True,
    )
    sequence_id = fields.Many2one(
        'ir.sequence',
        string='Sequence',
    )
