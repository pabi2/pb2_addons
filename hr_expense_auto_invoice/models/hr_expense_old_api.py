# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, osv
from openerp.addons import decimal_precision as dp


class hr_expense_expense(osv.osv):
    _inherit = "hr.expense.expense"

    """
    Still can not move this function to v8,
    as it will result in unit test during installation.
    """
    def _amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for expense in self.browse(cr, uid, ids, context=context):
            total = 0.0
            for line in expense.line_ids:
                total += line.total_amount  # Change to total_amount
            res[expense.id] = total
        return res

    def _get_expense_from_line(self, cr, uid, ids, context=None):
        return [line.expense_id.id for line in
                self.pool.get('hr.expense.line').browse(cr, uid, ids,
                                                        context=context)]

    _columns = {
        'amount': fields.function(
            _amount, string='Total Amount',
            digits_compute=dp.get_precision('Account'),
            store={'hr.expense.line': (_get_expense_from_line,
                                       ['unit_amount', 'unit_quantity'], 10)}),
    }
