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

from openerp.osv import fields, osv


class sale_advance_payment_inv(osv.osv_memory):
    
    _inherit = "sale.advance.payment.inv"

    def _get_advance_payment_method(self, cr, uid, context=None):
        res = super(sale_advance_payment_inv, self)._get_advance_payment_method(cr, uid, context=context)
        if context.get('active_model', False) == 'sale.order':
            sale_id = context.get('active_id', False)
            if sale_id:
                sale = self.pool.get('sale.order').browse(cr, uid, sale_id)
                # IF use invoice plan, only 'all' is allowed.
                if sale.use_invoice_plan:
                    res = [('all', 'Invoice the whole sales order')]
        return res

    _columns = {
        'advance_payment_method': fields.selection(_get_advance_payment_method,
            'What do you want to invoice?', required=True,),                
    }
    _defaults = {
        'advance_payment_method': lambda self,cr,uid,c: self._get_advance_payment_method(cr,uid,context=c)[0][0],
    }
    

sale_advance_payment_inv()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
