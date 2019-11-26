# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.tools.amount_to_text_en import amount_to_text
from openerp.addons.l10n_th_amount_text.amount_to_text_th \
    import amount_to_text_th

class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    # For reporting purpose only
    line_ids_name = fields.Text(
        compute='_compute_line_ids',
    )
    line_ids_amount = fields.Text(
        compute='_compute_line_ids',
    )
    # --
    # For Receipt for Supplier forms
    wa_total_fine = fields.Float(
        string='WA Total Fine',
        compute='_compute_wa_total_fine',
    )
    wa_voucher_diff_comment = fields.Char(
        string='WA Diff Comment',
        compute='_compute_wa_total_fine',
    )
    retention_amount = fields.Float(
        string='Retention Amount',
        compute='_compute_retention_amount',
    )
    retention_diff_comment = fields.Char(
        string='Retention Diff Comment',
        compute='_compute_retention_amount',
    )
    sale_installment_number = fields.Char(
        string='Installment',
        compute='_compute_sale_installment',
    )

    amount_wa_total = fields.Float(
        string='Amount total',
        compute='_compute_wa_amount',
    )
    amount_wa_total_text_en = fields.Char(
        string='Amount WA total Text (EN)',
        compute='_amount_wa_total_to_word_en',
    )
    amount_wa_total_text_th = fields.Char(
        string='Amount WA total Text (TH)',
        compute='_amount_wa_total_to_word_th',
    )


    @api.multi
    def _compute_sale_installment(self):
        for voucher in self:
            invoices = voucher.line_ids.mapped('invoice_id')
            if invoices:
                plans = self.env['sale.invoice.plan'].search(
                    [('ref_invoice_id', 'in', invoices.ids)]
                )
                installments = ', '.join([str(x.installment) for x in plans])
                voucher.sale_installment_number = installments

    @api.multi
    def _compute_line_ids(self):
        for rec in self:
            lines = rec.line_ids.sorted(key=lambda l: l.move_line_id.name)
            invoices = lines.mapped('invoice_id')
            amounts = lines.mapped('amount')
            amounts = ['{:,.2f}'.format(amount) for amount in amounts]
            rec.line_ids_name = '\n'.join(invoices.mapped('number'))
            rec.line_ids_amount = '\n'.join(amounts)

    def filter_print_report(self, res, reports):
        action = []
        if res.get('toolbar', False) and \
                res.get('toolbar').get('print', False):
            for act in res.get('toolbar').get('print'):
                if act.get('name') in reports:
                    action.append(act)
            res['toolbar']['print'] = action
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(AccountVoucher, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        # Customer Payment
        # if self._context.get('type', False) == 'receipt':
        #     reports = [
        #         u'Customer/Payment',
        #     ]
        #     self.filter_print_report(res, reports)
        # Customer Receipt
        if self._context.get('type', False) == 'sale' and\
                self._context.get('default_type', False) == 'sale':
            reports = []
            self.filter_print_report(res, reports)
        # Suplier Payment
        elif self._context.get('type', False) == 'payment':
            reports = [
                u'Print Cheque',
                u'Print Receipt',
            ]
            self.filter_print_report(res, reports)
        # Customer Receipt
        elif self._context.get('type', False) == 'purchase' and\
                self._context.get('default_type', False) == 'purchase':
            reports = []
            self.filter_print_report(res, reports)
        return res

    # For customer/supplier receipt report
    @api.multi
    def _compute_wa_total_fine(self):
        company = self.env.user.company_id
        for rec in self:
            # from invoice
            amount_from_invoice = abs(sum(rec.line_ids.mapped(
                'invoice_id.late_delivery_work_acceptance_id.total_fine')))
            # form payment diff
            accounts = [company.delivery_penalty_activity_id.account_id.id]
            diff_lines = rec.multiple_reconcile_ids.\
                filtered(lambda l: l.account_id.id in accounts)
            amount_from_diff = abs(sum(diff_lines.mapped('amount')))
            rec.wa_total_fine = amount_from_invoice + amount_from_diff
            comment_from_diff = ', '.join(diff_lines.mapped('note'))
            rec.wa_voucher_diff_comment = comment_from_diff
        return True

    @api.multi
    def _compute_retention_amount(self):
        company = self.env.user.company_id
        for rec in self:
            # from invoice
            amount_from_invoice = abs(sum(
                rec.line_ids.mapped('invoice_id').
                filtered('is_retention_return').  # Get only with PO retention
                mapped('amount_total'))) or 0.0
            # from voucher line retention
            amount_from_voucher = \
                abs(sum(rec.line_ids.mapped('amount_retention'))) or 0.0
            # from payment diff
            accounts = company.account_retention_customer_ids.ids + \
                company.account_retention_supplier_ids.ids
            diff_lines = rec.multiple_reconcile_ids.\
                filtered(lambda l: l.account_id.id in accounts)
            amount_from_diff = abs(sum(diff_lines.mapped('amount'))) or 0.0
            rec.retention_amount = amount_from_invoice + \
                amount_from_voucher + amount_from_diff
            comment_from_diff = ', '.join(diff_lines.mapped('note'))
            rec.retention_diff_comment = comment_from_diff
        return True
    
    @api.multi
    def _compute_wa_amount(self):
        for rec in self:
            wa_total_fine = rec.wa_total_fine or 0.0
            retention_amount = rec.retention_amount or 0.0
            rec.amount_wa_total = wa_total_fine + retention_amount 
        return True
    
    @api.multi
    def _amount_wa_total_to_word_en(self):
        res = {}
        minus = False
        amount_text = ''
        for obj in self:
            a = 'Baht'
            b = 'Satang'
            if obj.currency_id.name == 'JPY':
                a = 'Yen'
                b = 'Sen'
            if obj.currency_id.name == 'GBP':
                a = 'Pound'
                b = 'Penny'
            if obj.currency_id.name == 'USD':
                a = 'Dollar'
                b = 'Cent'
            if obj.currency_id.name == 'EUR':
                a = 'Euro'
                b = 'Cent'
            if obj.currency_id.name == 'SGD':
                a = 'Dollar'
                b = 'Cent'
            if obj.currency_id.name == 'CHF':
                a = 'Franc'
                b = 'Cent'
            if obj.currency_id.name == 'AUD':
                a = 'Dollar'
                b = 'Cent'
            if obj.currency_id.name == 'CNY':
                a = 'Yuan'
                b = ' '
            amount_text = amount_to_text(
                obj.amount_wa_total, 'en', a).replace(
                    'and Zero Cent', 'Only').replace(
                        'Cent', b).replace('Cents', b)
            final_amount_text = (minus and 'Minus ' +
                                 amount_text or amount_text).lower()
            obj.amount_wa_total_text_en = final_amount_text[:1].upper() + final_amount_text[1:]
        
    
    @api.multi
    def _amount_wa_total_to_word_th(self):
        minus = False
        amount_text = ''
        for rec in self:
            amount_wa_total = rec.amount_wa_total
            amount_wa_total_text = amount_to_text_th(amount_wa_total, rec.currency_id.name)
        rec.amount_wa_total_text_th  = minus and 'ลบ' + amount_wa_total_text or amount_wa_total_text
    
class AccountVoucherLine_Des(models.Model):
    _inherit = 'account.voucher.line'

    journal_description = fields.Text(
        string='Journal Description',
        compute='_compute_journal_description',
        readonly=True,
        size=1000,
    )
    
    @api.multi
    def _compute_journal_description(self):
        for rec in self:
            move_line = self.env['account.move.line'].search([('move_id','=',rec.voucher_id.move_id.id),
                                                         ('account_id','=',rec.account_id.id),('credit','=',rec.amount)])
            rec.journal_description = move_line.name
        
       
        