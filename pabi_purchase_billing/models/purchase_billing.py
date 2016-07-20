# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class PurchaseBilling(models.Model):
    _name = "purchase.billing"
    _inherit = ['mail.thread']

    name = fields.Char(
        string='Billing Number',
        readonly=True,
        copy=False,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        required=True,
        readonly=True,
        domain=[('supplier', '=', True)],
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('billed', 'Billed'),
         ('cancel', 'Cancelled')],
        string='Status',
        index=True,
        readonly=True,
        default='draft',
        copy=False,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Perpared By',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self._uid,
    )
    date = fields.Date(
        string='Billing Date',
        copy=False,
        default=lambda self: fields.Date.context_today(self),
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date_due = fields.Date(
        string='Due Date',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    note = fields.Text(
        string='Notes',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    supplier_invoice_ids = fields.Many2many(
        'account.invoice',
        'supplier_invoice_purchase_billing_rel',
        'billing_id', 'invoice_id',
        string='Supplier Invoices',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    amount_total = fields.Float(
        string='Total Amount',
        compute='_compute_amount_total',
        readonly=True,
        store=True,
    )
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Billing Number must be unique!'),
    ]

    @api.one
    @api.depends('supplier_invoice_ids')
    def _compute_amount_total(self):
        self.amount_total = sum([x.amount_total
                                 for x in self.supplier_invoice_ids])

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = self.env['account.invoice'].onchange_payment_term_date_invoice(
            self.partner_id.property_supplier_payment_term.id,
            self.date)
        self.date_due = res['value']['date_due']
        self.supplier_invoice_ids = False

    @api.multi
    def validate_billing(self):
        self.write({'state': 'billed'})
        for rec in self:
            rec.supplier_invoice_ids.write({'date_invoice': rec.date,
                                            'date_due': rec.date_due,
                                            'purchase_billing_id': rec.id})
            if not rec.name:
                rec.name = self.env['ir.sequence'].get('purchase.billing')
        self.message_post(body=_('Billing is billed.'))

    @api.multi
    def action_cancel_draft(self):
        self.write({'state': 'draft'})
        self.message_post(body=_('Billing is reset to draft'))
        return True

    @api.multi
    def cancel_billing(self):
        self.write({'state': 'cancel'})
        for rec in self:
            rec.supplier_invoice_ids.write({'date_invoice': False,
                                            'date_due': False,
                                            'purchase_billing_id': False})
        self.message_post(body=_('Billing is cancelled'))
        return True

    @api.multi
    def unlink(self):
        for billing in self:
            if billing.state not in ('draft', 'cancel'):
                raise ValidationError(
                    _('Cannot delete billing(s) which are already billed.'))
        return super(PurchaseBilling, self).unlink()
