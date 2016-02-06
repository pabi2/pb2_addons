# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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


from openerp import models, api, fields


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    sale_ids = fields.Many2many(
        'sale.order',
        'sale_order_invoice_rel', 'invoice_id', 'order_id',
        copy=False,
        string='Sales Orders',
        readonly=True,
        help="This is the list of sale orders linked to this invoice.")

    @api.multi
    def action_cancel(self):
        """ Only in invoice plan case, if any of the invoice
            is cancel, make invoice exception to sales order """
        for inv in self:
            self._cr.execute("""select max(order_id) from sale_order_invoice_rel
                                where invoice_id=%s""", (inv.id,))
            order_id = self._cr.fetchone()[0] or False
            if order_id: #and self.env['sale.order'].browse(order_id).use_invoice_plan:
                # Make sure the order's workflow instance is
                # point to the right subflow (this invoice)
                order_inst = self.env['workflow.instance'].search(
                    [('res_type', '=', 'sale.order'),
                     ('res_id', '=', order_id)])
                order_witem = self.env['workflow.workitem'].search(
                    [('inst_id', '=', order_inst.id)])[0]
                inv_inst = self.env['workflow.instance'].search(
                    [('res_type', '=', 'account.invoice'),
                     ('res_id', '=', inv.id)])
                order_witem.subflow_id = inv_inst.id
        res = super(account_invoice, self).action_cancel()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
