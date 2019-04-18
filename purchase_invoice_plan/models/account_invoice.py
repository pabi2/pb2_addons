# -*- coding: utf-8 -*-
from openerp import models, fields , api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    invoice_plan_ids = fields.One2many(
        'purchase.invoice.plan',
        'ref_invoice_id',
        string='Invoice Plan',
        copy=False,
        readonly=True,
    )
    
    is_invoice_plan = fields.Boolean(
        compute="_compute_is_invoice_plan",
        string='Is Invoice Plan',
        store=True,
    )
    
    installment = fields.Integer(
        related='invoice_plan_ids.installment',
        string='Installment',
    )
    
    @api.multi
    @api.depends('invoice_plan_ids')
    def _compute_is_invoice_plan(self):
        for invoice in self:
            if invoice.invoice_plan_ids:
                invoice.is_invoice_plan = True
            else:
                invoice.is_invoice_plan = False
