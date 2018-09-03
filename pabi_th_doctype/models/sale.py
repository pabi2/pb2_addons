# -*- coding: utf-8 -*-
from openerp import models, api

_DOCTYPE = {'quotation': 'sale_quotation',
            'sale_order': 'sale_order'}


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            # Automatic Workflow = POS Order
            if vals.get('workflow_process_id', False):
                doctype = self.env['res.doctype'].get_doctype('pos_order')
                fiscalyear_id = self.env['account.fiscalyear'].find()
                # --
                self = self.with_context(doctype_id=doctype.id,
                                         fiscalyear_id=fiscalyear_id)
                next = self.env['ir.sequence'].next_by_doctype()
                if next:
                    vals['name'] = next
        return super(SaleOrder, self).create(vals)
