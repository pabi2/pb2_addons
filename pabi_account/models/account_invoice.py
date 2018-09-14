# -*- coding: utf-8 -*-
import ast
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from openerp.addons.l10n_th_account.models.res_partner \
    import INCOME_TAX_FORM


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    validate_user_id = fields.Many2one(
        'res.users',
        string='Validated By',
        readonly=True,
        copy=False,
    )
    validate_date = fields.Date(
        'Validate On',
        readonly=True,
        copy=False,
    )
    payment_count = fields.Integer(
        string='Payment Count',
        compute='_compute_payment_count',
        readonly=True,
    )
    payment_type = fields.Selection(
        [('cheque', 'Cheque'),
         ('transfer', 'Transfer'),
         ],
        string='Payment Type',
        help="Specified Payment Type, can be used to screen Payment Method",
    )
    currency_rate = fields.Float(
        string='Currency Rate',
        compute='_compute_currency_rate',
        store=True,
    )
    ref_docs = fields.Char(
        string='Reference Doc',
        compute='_compute_ref_docs',
        store=True,
    )
    invoice_description = fields.Text(
        string='Invoice Description',
        compute='_compute_invoice_description',
        store=True,
        size=1000,
        help="Compute summary description of entire invoice lines",
    )
    income_tax_form = fields.Selection(
        INCOME_TAX_FORM,
        string='Income Tax Form',
        help="If invoice has withholding tax, this field is required.",
    )
    has_wht = fields.Boolean(
        string='Has WHT in invoice line',
        compute='_compute_has_wht',
    )
    number_preprint = fields.Char(
        string='Preprint Number',
        size=500,
        copy=False,
    )
    display_name2 = fields.Char(
        string='Partner Name',
        related='partner_id.display_name2',
        store=True,
    )
    partner_code = fields.Char(
        string='Partner Code',
        related='partner_id.search_key',
        store=True,
    )
    date_invoice = fields.Date(
        string='Posting Date',  # Change label
        # default=lambda self: fields.Date.context_today(self),
    )
    date_document = fields.Date(
        string='Document Date',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
        default=lambda self: fields.Date.context_today(self),
    )
    recreated_invoice_id = fields.Many2one(
        'account.invoice',
        string='Recreated Invoice',
        readonly=True,
        help="New invoice created to replace this cancelled invoice."
    )
    legacy_ref = fields.Char(
        string='Legacy Ref.',
        readonly=False,
        size=500,
    )
    _sql_constraints = [('number_preprint_uniq', 'unique(number_preprint)',
                        'Preprint Number must be unique!')]

    @api.multi
    def action_cancel(self):
        for rec in self:
            # For invoice created by Picking, cancel invoice should
            # set back invoice_state of picking to 2binvoiced
            # This will allow recreate invoice form picking
            moves = rec.invoice_line.mapped('move_id')
            moves.write({'invoice_state': '2binvoiced'})
        return super(AccountInvoice, self).action_cancel()

    @api.multi
    def write(self, vals):
        # Set date
        if vals.get('date_invoice') and not vals.get('date_document'):
            for rec in self:
                if not rec.date_document:
                    vals['date_document'] = vals['date_invoice']
                    break
        return super(AccountInvoice, self).write(vals)

    @api.multi
    def confirm_paid(self):
        return super(AccountInvoice, self.sudo()).confirm_paid()

    @api.multi
    @api.depends('invoice_line.invoice_line_tax_id')
    def _compute_has_wht(self):
        for rec in self:
            rec.has_wht = False
            for line in rec.invoice_line:
                for tax in line.invoice_line_tax_id:
                    if tax.is_wht:
                        rec.has_wht = True
                        break
                if rec.has_wht:
                    break

    @api.onchange('has_wht')
    def _onchange_has_wht(self):
        self.income_tax_form = \
            self.has_wht and self.partner_id.income_tax_form or False

    @api.model
    def create(self, vals):
        """ As invoice created, set default income_tax_form, if needed """
        invoice = super(AccountInvoice, self).create(vals)
        if invoice.has_wht:
            # Update invoice's income_tax_form = partner's income_tax_form
            self._cr.execute("""
                update account_invoice av set income_tax_form =
                (select income_tax_form from res_partner p
                where p.id = av.partner_id) where av.id = %s
            """, (invoice.id, ))
        return invoice

    @api.multi
    @api.depends('invoice_line')
    def _compute_invoice_description(self):
        for invoice in self:
            description = ''
            for line in invoice.invoice_line:
                # description += line.name + ' ' + \
                #     '{:,}'.format(line.quantity) + \
                #     (line.uos_id and (' ' + line.uos_id.name) or '') + '\n'

                # Remove quantity and uos out from description
                description += line.name + '\n'
            invoice.invoice_description = \
                len(description) > 0 and description or False

    @api.multi
    @api.depends('tax_line',
                 'tax_line.detail_ids',
                 'tax_line.detail_ids.invoice_number')
    def _compute_ref_docs(self):
        for rec in self:
            header_text = ''
            for tax in rec.tax_line:
                for detail in tax.detail_ids:
                    if not header_text:
                        header_text = detail.invoice_number
                    else:
                        header_text = (header_text + ',' +
                                       detail.invoice_number)
                    rec.ref_docs = header_text

    @api.multi
    @api.depends('currency_id')
    def _compute_currency_rate(self):
        for rec in self:
            company = rec.company_id
            context = self._context.copy()
            ctx_date = rec.date_invoice
            if not ctx_date:
                ctx_date = fields.Date.today()
            context.update({'date': ctx_date})
            # get rate of company currency to current invoice currency
            rate = self.env['res.currency'].\
                with_context(context)._get_conversion_rate(company.currency_id,
                                                           rec.currency_id)
            rec.currency_rate = rate

    @api.multi
    def _compute_payment_count(self):
        for rec in self:
            move_ids = [move_line.move_id.id for move_line in rec.payment_ids]
            voucher_ids = self.env['account.voucher'].\
                search([('move_id', 'in', move_ids)])._ids
            rec.payment_count = len(voucher_ids)

    @api.multi
    def invoice_validate(self):
        result = super(AccountInvoice, self.sudo()).invoice_validate()
        for invoice in self:
            invoice.write({'validate_user_id': self.env.user.id,
                           'validate_date': fields.Date.today()})
            # Not allow negative amount
            if invoice.amount_total < 0.0:
                raise ValidationError(_('Negative total amount not allowed!'))
        return result

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(AccountInvoice, self).line_get_convert(line, part, date)
        res.update({
            'taxbranch_id': line.get('taxbranch_id', False),
        })
        return res

    # We can't really use constraint, need to check on validate
    # When an invoice is saved, finally it is not negative, but beginning it
    # could be
    # --
    # @api.multi
    # @api.constrains('amount_total')
    # def _check_amount_total(self):
    #     for rec in self:
    #         print rec.amount_total
    #         if rec.amount_total < 0.0:
    #             raise Warning(_('Negative Total Amount is not allowed!'))

    @api.multi
    def action_open_payments(self):
        self.ensure_one()
        move_ids = self.payment_ids.mapped('move_id')._ids
        Voucher = self.env['account.voucher']
        voucher_ids = Voucher.search([('move_id', 'in', move_ids)])._ids
        action = False
        if self.type in ('in_invoice', 'in_refund'):
            action = self.env.ref('account_voucher.action_vendor_payment')
        if self.type in ('out_invoice', 'out_refund'):
            action = self.env.ref('account_voucher.action_vendor_receipt')
        if not action:
            raise ValidationError(_('No Action'))
        action = action.read([])[0]
        action['domain'] =\
            "[('id','in', [" + ','.join(map(str, voucher_ids)) + "])]"
        ctx = ast.literal_eval(action['context'])
        ctx.update({
            'filter_invoices': self.ids  # account_move_line.search()
        })
        action['context'] = ctx
        return action

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        move_lines = super(AccountInvoice,
                           self).finalize_invoice_move_lines(move_lines)
        new_move_lines = []
        # Tax Accounts
        vats = self.env['account.tax'].search([('is_wht', '=', False)])
        tax_account_ids = vats.mapped('account_collected_id').ids
        tax_account_ids += vats.mapped('account_paid_id').ids
        for line_tuple in move_lines:
            if line_tuple[2]['account_id'] in tax_account_ids:
                line_tuple[2]['taxinvoice_taxbranch_id'] = \
                    self.taxbranch_id.id
            new_move_lines.append(line_tuple)
        return new_move_lines

    @api.model
    def _prepare_pettycash_invoice_line(self, pettycash):
        inv_line = super(AccountInvoice, self).\
            _prepare_pettycash_invoice_line(pettycash)
        inv_line.section_id = pettycash.partner_id.employee_id.section_id
        return inv_line

    @api.multi
    def recover_cancelled_invoice(self):
        """ For accountant to rectify his/her mistake, for cases,
        - Invoice from purchase.order (+ case invoice plan)
        - Invoices from WA
        - Invoice from stock.picking
        """
        self.ensure_one()
        if self.state != 'cancel':
            raise ValidationError(_('Only cancelled invoice is allowed!'))
        if self.recreated_invoice_id:
            raise ValidationError(_('Invoice already been recreated'))
        Data = self.env['ir.model.data']
        # Invoice created from PO
        if self.purchase_ids:
            purchase = self.purchase_ids[0]
            if purchase.state == 'cancel':
                raise ValidationError(
                    _('Can not recreate invoice, PO already cancelled'))
            # 1) Case invoices created from PO
            if purchase.invoice_method in ['order', 'invoice_plan']:
                # Create new invoice from PO and set manually correct
                purchase.action_invoice_create()
                purchase.signal_workflow('invoice_ok')
                # --
                self.recreated_invoice_id = max(purchase.invoice_ids.ids)
            # 2) Case invoices created from IN
            elif purchase.invoice_method == 'picking':
                moves = self.invoice_line.mapped('move_id')
                picking = moves.mapped('picking_id')
                if len(picking) != 1:
                    raise ValidationError(
                        _('This invoice does not reference to 1 picking.'))
                if picking.state != 'done' or \
                        picking.invoice_state != '2binvoiced':
                    raise ValidationError(
                        _('Picking not in valid status to recreate invoice'))
                # Mock create invoice wizard
                StockInvoice = self.env['stock.invoice.onshipping']
                ctx = {'active_ids': [picking.id], 'active_id': picking.id}
                stock_invoice = StockInvoice.with_context(ctx).create({})
                stock_invoice.open_invoice()
                # --
                self.recreated_invoice_id = max(picking.ref_invoice_ids.ids)
            # 3) Case invoice created by WA
            elif purchase.invoice_method == 'manual':
                WA = self.env['purchase.work.acceptance']
                acceptance = WA.search([('invoice_created', '=', self.id)])
                if not acceptance:
                    raise ValidationError(_('No WA specific for this invoice'))
                LineInvoice = self.env['purchase.order.line_invoice']
                res = WA.open_order_line([acceptance.id])
                ctx = {'active_model': 'purchase.work.acceptance',
                       'active_id': acceptance.id}
                res['context'].update(ctx)
                line_inv = LineInvoice.with_context(res['context']).create({})
                res = line_inv.makeInvoices()
                invoice_dom = ast.literal_eval(res.get('domain', 'False'))
                invoice_ids = invoice_dom and invoice_dom[0][2] or []
                self.recreated_invoice_id = \
                    invoice_ids and invoice_ids[0] or False
            else:
                raise ValidationError(
                    _('Current purchase invoice method is not supported'))
            if self.recreated_invoice_id:
                self.recreated_invoice_id.write({
                    'supplier_invoice_number': self.supplier_invoice_number,
                    'date_due': self.date_due,
                    'payment_type': self.payment_type,
                })
            # Redirect to new invoice
            if self.recreated_invoice_id:
                action = self.env.ref('account.action_invoice_tree2')
                result = action.read()[0]
                res = Data.get_object_reference('account',
                                                'invoice_supplier_form')
                result['views'] = [(res and res[1] or False, 'form')]
                result['res_id'] = self.recreated_invoice_id.id or False
                return result
        return True


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    account_id_readonly = fields.Many2one(
        'account.account',
        string='Account',
        related='account_id',
        readonly=True,
    )

    @api.multi
    def onchange_account_id(self, product_id, partner_id, inv_type,
                            fposition_id, account_id):
        res = super(AccountInvoiceLine, self).onchange_account_id(
            product_id, partner_id, inv_type, fposition_id, account_id)
        account = self.env['account.account'].browse(account_id)
        if not res.get('value'):
            res['value'] = {}
        res['value'].update({'name': account.name})
        return res


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        related='invoice_id.taxbranch_id',
        string='Tax Branch',
        readonly=True,
        store=True,
    )

    @api.model
    def _prepare_invoice_tax_detail(self):
        res = super(AccountInvoiceTax, self).\
            _prepare_invoice_tax_detail()
        res.update({'taxbranch_id': self.invoice_id.taxbranch_id.id})
        return res

    @api.model
    def move_line_get(self, invoice_id):
        res = super(AccountInvoiceTax, self).move_line_get(invoice_id)
        tax_move_by_taxbranch = self.env.user.company_id.tax_move_by_taxbranch
        if tax_move_by_taxbranch:
            invoice = self.env['account.invoice'].browse(invoice_id)
            for r in res:
                r.update({'taxbranch_id': invoice.taxbranch_id.id})
        return res
