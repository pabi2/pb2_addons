# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from __future__ import division
from openerp import models, api


class PurchaseLineInvoice(models.TransientModel):

    _inherit = 'purchase.order.line_invoice'

    @api.model
    def default_get(self, fields):
        if self._context['active_model'] == 'purchase.work.acceptance':
            active_id = self._context['active_id']
            WAcceptance = self.env['purchase.work.acceptance']
            lines = []
            acceptance = WAcceptance.browse(active_id)
            for wa_line in acceptance.acceptance_line_ids:
                po_line = wa_line.line_id
                max_quantity = po_line.product_qty - \
                    po_line.invoiced_qty - po_line.cancelled_qty
                if po_line.order_id.invoice_method == 'invoice_plan':
                    max_quantity = po_line.product_qty
                lines.append({
                    'po_line_id': po_line.id,
                    'product_qty': max_quantity,
                    'invoiced_qty': wa_line.to_receive_qty,
                    'price_unit': po_line.price_unit,
                })
            defaults = super(PurchaseLineInvoice, self).default_get(fields)
            defaults['line_ids'] = lines
        else:
            defaults = super(PurchaseLineInvoice, self).default_get(fields)
        return defaults

    @api.multi
    def makeInvoices(self):
        res = super(PurchaseLineInvoice, self).makeInvoices()
        if self._context['active_model'] == 'purchase.work.acceptance':
            active_id = self._context['active_id']
            WAcceptance = self.env['purchase.work.acceptance']
            acceptance = WAcceptance.browse(active_id)
            acceptance.invoice_created = True
        return res
