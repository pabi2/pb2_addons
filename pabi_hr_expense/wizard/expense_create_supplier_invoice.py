# -*- coding: utf-8 -*-
# © 2016 Kitti U.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from lxml import etree
from openerp.osv.orm import setup_modifiers
from openerp import api, models, fields


class ExpenseCreateSupplierInvoice(models.TransientModel):
    _inherit = "expense.create.supplier.invoice"

    invoice_rule = fields.Selection(
        [('single_supplier_invoice', 'Single Supplier Invoice'),
         ('multi_supplier_invoice', 'Multi Supplier Invoice')],
        string="Invoice Rule",
        default='single_supplier_invoice',
    )

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        result = super(ExpenseCreateSupplierInvoice, self).\
            fields_view_get(view_id=view_id, view_type=view_type,
                            toolbar=toolbar, submenu=submenu)
        if self._context.get('is_employee_advance', False) or\
                self._context.get('is_advance_clearing', False)\
                and view_type == 'form':
            doc = etree.XML(result['arch'])
            nodes = doc.xpath("//field[@name='invoice_rule']")
            for node in nodes:
                node.set('invisible', '1')
                setup_modifiers(node,
                                result['fields'][node.attrib['name']])
            result['arch'] = etree.tostring(doc)
        return result

    @api.multi
    def action_create_supplier_invoice(self):
        self.ensure_one()
        Expense = self.env['hr.expense.expense']
        expense = Expense.browse(self._context.get('active_id', False))
        if self.invoice_rule == 'single_supplier_invoice' or ('is_employee_advance' in expense and
                expense.is_employee_advance)\
                or ('is_advance_clearing' in expense and expense.is_advance_clearing):
            return super(ExpenseCreateSupplierInvoice, self).action_create_supplier_invoice()
        else:
            lines = []
#             total_attendee = len(expense.attendee_employee_ids.ids) + len(expense.attendee_external_ids.ids)
# 
#             if total_attendee > 0:
#                 amount = expense.amount / total_attendee
            if expense.attendee_employee_ids:
                for attendee in expense.attendee_employee_ids:
                    partner = attendee.employee_id.address_home_id.id
                    parnter_name = attendee.employee_id.address_home_id.name
                    lines.append((0, 0, {'employee_id': attendee.employee_id.id,
                                         'partner_id': partner,
                                         'partner_name': parnter_name,
                                         'taxid': False,
                                         }
                                ))
            if expense.attendee_external_ids:
                for attendee in expense.attendee_external_ids:
                    lines.append((0, 0, {'employee_id': False,
                                         'partner_id': False,
                                         'partner_name': attendee.attendee_name,
                                         'taxid': False,
                                         }
                                ))
            context = self._context.copy()
            context.update({'default_multi_supplier_invoice_line': lines,
                            'expense_id': expense.id})
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'expense.create.multi.supplier.invoice',
                'view_mode': 'form',
                'view_type': 'form',
                'views': [(False, 'form')],
                'target': 'new',
                'context': context,
            }
