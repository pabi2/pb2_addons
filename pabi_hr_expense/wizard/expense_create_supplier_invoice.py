# -*- coding: utf-8 -*-
from lxml import etree
from openerp.osv.orm import setup_modifiers
from openerp import api, models, fields, _
from openerp.exceptions import ValidationError


class ExpenseCreateSupplierInvoice(models.TransientModel):
    _inherit = "expense.create.supplier.invoice"

#     invoice_rule = fields.Selection(
#         [('single_supplier_invoice', 'Single Supplier Invoice'),
#          ('multi_supplier_invoice', 'Multi Supplier Invoice')],
#         string="Invoice Rule",
#         default='single_supplier_invoice',
#     )
    use_attendee_list = fields.Boolean(
        string='Use Attendee List',
        default=False,
    )

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        Expense = self.env['hr.expense.expense']
        expense = Expense.browse(self._context.get('active_id'))
        no_multi_supplier = (expense.pay_to != 'supplier' or
                             expense.is_employee_advance or
                             expense.is_advance_clearing) or False
        result = super(ExpenseCreateSupplierInvoice, self).\
            fields_view_get(view_id=view_id, view_type=view_type,
                            toolbar=toolbar, submenu=submenu)
        if no_multi_supplier:
            doc = etree.XML(result['arch'])
            nodes = doc.xpath("//field[@name='use_attendee_list']")
            for node in nodes:
                node.set('invisible', '1')
                setup_modifiers(
                    node, result['fields'][node.attrib['name']])
            result['arch'] = etree.tostring(doc)
        return result

    @api.multi
    def action_create_supplier_invoice(self):
        self.ensure_one()
        Expense = self.env['hr.expense.expense']
        expense = Expense.browse(self._context.get('active_id', False))
        if not self.use_attendee_list or \
                ('is_employee_advance' in expense and
                 expense.is_employee_advance) or \
                ('is_advance_clearing' in expense and
                 expense.is_advance_clearing):
            return super(ExpenseCreateSupplierInvoice, self).\
                action_create_supplier_invoice()
        else:
            if len(expense.line_ids) != 1:
                raise ValidationError(
                    _('Attendee list can be used only for 1 expense line!'))
            lines = []
            amount_untaxed = sum([x.unit_amount * x.unit_quantity
                                  for x in expense.line_ids])
            expense_state = self._context.get('state', '')
            if expense_state == 'done':
                amount_untaxed = expense.to_invoice_amount
            if expense.attendee_employee_ids:
                for attendee in expense.attendee_employee_ids:
                    partner_id = attendee.employee_id.user_id.partner_id.id
                    parnter_name = attendee.employee_id.name
                    vals = {'partner_id': partner_id,
                            'partner_name': parnter_name,
                            'amount': 0.0,
                            }
                    lines.append((0, 0, vals))
            if expense.attendee_external_ids:
                for attendee in expense.attendee_external_ids:
                    vals = {'partner_id': False,
                            'partner_name': attendee.attendee_name,
                            'amount': 0.0,
                            }
                    lines.append((0, 0, vals))
            context = self._context.copy()
            context.update({'default_multi_supplier_invoice_line': lines,
                            'default_amount_untaxed': amount_untaxed,
                            'date_invoice': self.date_invoice,
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
