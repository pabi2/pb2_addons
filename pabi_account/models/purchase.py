# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    invoice_count = fields.Integer(
        string='Supplier Invoice',
        compute='_compute_invoice_count',
    )
    payment_term_id = fields.Many2one(
        'account.payment.term',
        domain=[('expense', '=', True)],
    )

    @api.multi
    def _compute_invoice_count(self):
        Invoice = self.env['account.invoice']
        for rec in self:
            invoices = Invoice.search([('source_document', '=', rec.name)])
            rec.invoice_count = len(invoices)

    @api.multi
    def invoice_open(self):
        """ Overwrite
        Change po.invoice_ids to all invoice with reference PO """
        self.ensure_one()
        Invoice = self.env['account.invoice']
        Data = self.env['ir.model.data']

        action = self.env.ref('account.action_invoice_tree2')
        result = action.read()[0]

        invoices = Invoice.search([('source_document', '=', self.name)])

        if not invoices:
            raise ValidationError(_('Please create Invoices.'))

        if len(invoices) > 1:
            result['domain'] = [('id', 'in', invoices.ids)]
        else:
            res = Data.get_object_reference('account', 'invoice_supplier_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = invoices.ids and invoices.ids[0] or False
        return result

    @api.multi
    def _compute_plan_invoice_created(self):
        """ Overwrite, as now invoice_ids may not reflect real invoices
        so we use reference to document name instead """
        Invoice = self.env['account.invoice']
        for rec in self:
            invoices = Invoice.search([('source_document', '=', rec.name)])
            if not invoices or not rec.use_invoice_plan:
                rec.plan_invoice_created = False
            else:
                total_invoice_amt = 0
                num_valid_invoices = 0
                for i in invoices:
                    if i.state not in ('cancel'):
                        num_valid_invoices += 1
                    if i.state in ('open', 'paid'):
                        total_invoice_amt += i.amount_untaxed
                plan_invoice = len(list(set([i.installment for i in
                                             rec.invoice_plan_ids])))
                rec.plan_invoice_created = num_valid_invoices == plan_invoice
                rec.total_invoice_amount = total_invoice_amt
        return True
