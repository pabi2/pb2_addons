# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
import datetime
import re
import time
import calendar


class PurchaseBilling(models.Model):
    _name = 'purchase.billing'
    _description = 'Purchase Billing'
    _inherit = ['mail.thread']

    name = fields.Char(
        string='Billing Number',
        readonly=True,
        size=500,
        copy=False,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.user.company_id.currency_id,
        required=True,
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
        string='Prepared By',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env.user,
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
        size=1000,
    )
    supplier_invoice_ids = fields.Many2many(
        'account.invoice',
        'supplier_invoice_purchase_billing_rel',
        'billing_id', 'invoice_id',
        string='Supplier Invoices',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
    )
    amount_total = fields.Float(
        string='Total Amount',
        compute='_compute_amount_total',
        readonly=True,
        store=True,
    )
    email_sent = fields.Boolean(
        string='Email Sent',
        readonly=False,
    )
    date_sent = fields.Date(
        string='Billing Sent Date',
        readonly=True,
        states={'billed': [('readonly', False)]},
        track_visibility='onchange',
    )
    count_invoice = fields.Integer(
        string='Count Invoice',
        compute='_count_invoice',
        store=False,
    )
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Billing Number must be unique!'),
    ]

    @api.constrains('date_due')
    def _validate_date_due(self):
        day = datetime.datetime.strptime(self.date_due, '%Y-%m-%d').date().day
        check_day = datetime.datetime.\
            strptime(self.date_due, '%Y-%m-%d').date()
        date_list = []
        THHoliday = self.env['thai.holiday']
        date_due_setting = self.env.user.company_id.date_due_day
        regex = r"\d{1,2}"
        matches = re.findall(regex, date_due_setting)
        for match in matches:
            if check_day.month == 2:
                match = calendar.monthrange(check_day.year, check_day.month)[1]
            check = check_day.replace(day=int(match))
            check = datetime.datetime.strftime(check, "%Y-%m-%d")
            check_string = THHoliday.find_previous_working_day(check)
            final_check_day = datetime.datetime.\
                strptime(check_string, '%Y-%m-%d').date().day
            #  if 0 < int(final_check_day) < 29 and int(final_check_day) \
            #          not in date_list:
            if int(final_check_day) not in date_list:
                date_list.append(int(final_check_day))
            else:
                raise ValidationError(
                    _("""Wrong due date configuration.
                         Please check the due date setting.""")
                )
        if day not in date_list and not \
                self._context.get('bypass_due_date_check', False):
            raise ValidationError(
                _("""You specified wrong due date.
                     It has to be in %s
                """ % (date_list,))
            )

    @api.constrains('date_sent')
    def _validate_date_sent(self):
        for rec in self:
            date_sent = rec.date_sent
            if date_sent and date_sent < time.strftime('%Y-%m-%d'):
                raise ValidationError(
                    _("You specified wrong billing sent date "
                      "It must be more than or equal %s"
                        % (time.strftime('%d/%m/%Y'))))

    @api.multi
    @api.depends('supplier_invoice_ids')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = \
                sum(rec.supplier_invoice_ids.mapped('amount_total'))
        return True

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = self.env['account.invoice'].onchange_payment_term_date_invoice(
            self.partner_id.property_supplier_payment_term.id,
            self.date)
        self.date_due = res['value']['date_due']
        self.supplier_invoice_ids = False

    @api.onchange('currency_id')
    def _onchane_currency_id(self):
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
    def action_send_bill(self):
        self.ensure_one()
        try:
            template_id = self.env.ref(
                'pabi_purchase_billing.email_template_purchase_billing'
            ).id
        except ValueError:
            template_id = False

        try:
            compose_form_id = self.env.ref(
                'mail.email_compose_message_wizard_form').id
        except ValueError:
            compose_form_id = False

        ctx = dict(self.env.context)
        ctx.update({
            'default_model': 'purchase.billing',
            'default_res_id': self._ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

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

    @api.multi
    def _count_invoice(self):
        Invoice = self.env['account.invoice']
        for rec in self:
            dom = [('purchase_billing_id', '=', rec.id)]
            rec.count_invoice = Invoice.search_count(dom)
        return True

    @api.multi
    def action_open_invoice(self):
        self.ensure_one()
        action = self.env.ref('account.action_invoice_tree2')
        result = action.read()[0]
        dom = [('purchase_billing_id', '=', self.id)]
        result.update({'domain': dom})
        return result


class PurchaseBillingDate(models.TransientModel):
    _name = 'purchase.billing.sent.date'

    date_sent = fields.Date(
        string='Billing Sent Date',
        track_visibility='onchange',
    )

    @api.multi
    def update_billing_date(self):
        self.ensure_one()
        active_ids = self._context.get('active_ids')
        billings = self.env['purchase.billing'].browse(active_ids)
        billings.write({'date_sent': self.date_sent})
