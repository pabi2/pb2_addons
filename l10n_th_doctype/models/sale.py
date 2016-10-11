# -*- coding: utf-8 -*-
# © 2016 Kitti U.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

_DOCTYPE = {'quotation': 'sale_quotation',
            'sale_order': 'sale_order'}


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    doctype_id = fields.Many2one(
        'res.doctype',
        string='Doctype',
        compute='_compute_doctype',
        store=True,
        readonly=True,
    )

    @api.one
    @api.depends('order_type')
    def _compute_doctype(self):
        refer_type = _DOCTYPE[self.order_type]
        doctype = self.env['res.doctype'].search([('refer_type', '=',
                                                   refer_type)], limit=1)
        self.doctype_id = doctype.id

    @api.model
    def create(self, vals):
        new_order = super(SaleOrder, self).create(vals)
        # Find doctype
        if new_order.doctype_id.sequence_id:
            sequence_id = new_order.doctype_id.sequence_id.id
            fiscalyear_id = self.env['account.fiscalyear'].find()
            next_number = self.with_context(fiscalyear_id=fiscalyear_id).\
                env['ir.sequence'].next_by_id(sequence_id)
            new_order.name = next_number
        return new_order
