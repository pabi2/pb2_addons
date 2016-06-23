# -*- coding: utf-8 -*-
from lxml import etree
from openerp.osv.orm import setup_modifiers
from openerp import api, models, fields


class ExpenseCreateSupplierInvoice(models.TransientModel):
    _name = "expense.create.supplier.invoice"

    date_invoice = fields.Date(
        string='Invoice Date',
        required=True,
        default=fields.Date.today(),
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
    )

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        Expense = self.env['hr.expense.expense']
        expense = Expense.browse(self._context.get('active_id'))
        result = super(ExpenseCreateSupplierInvoice, self).\
            fields_view_get(view_id=view_id, view_type=view_type,
                            toolbar=toolbar, submenu=submenu)
        if expense.pay_to != 'supplier':
            doc = etree.XML(result['arch'])
            nodes = doc.xpath("//field[@name='partner_id']")
            for node in nodes:
                node.set('invisible', '1')
                node.set('required', '0')
                setup_modifiers(node,
                                result['fields'][node.attrib['name']])
            result['arch'] = etree.tostring(doc)
        return result

    @api.multi
    def action_create_supplier_invoice(self):
        self.ensure_one()
        Expense = self.env['hr.expense.expense']
        expense = Expense.browse(self._context.get('active_id', False))
        expense.date_invoice = self.date_invoice
        expense.partner_id = self.partner_id
        expense.signal_workflow('done')
