# -*- coding: utf-8 -*-

from openerp import fields, models, api
import datetime
import openerp.addons.decimal_precision as dp
from openerp.addons.l10n_th_amount_text.amount_to_text_th \
    import amount_to_text_th


class PurchaseWorkAcceptance(models.Model):
    _name = 'purchase.work.acceptance'
    _description = 'Purchase Work Acceptance'

    _STATES = [
        ('draft', 'Draft'),
        ('evaluation', 'Evaluation'),
        ('done', 'Done'),
    ]

    @api.one
    @api.depends('date_receive', 'date_contract_end')
    def _fine_amount_to_word_th(self):
        res = {}
        minus = False
        order = self.order_id
        amount_total = self.total_fine
        if amount_total < 0:
            minus = True
            amount_total = -amount_total
        amount_text = amount_to_text_th(amount_total, order.currency_id.name)
        self.amount_total_fine_text_th = minus and\
            'ลบ' + amount_text or amount_text
        return res

    @api.one
    @api.depends('date_receive', 'date_contract_end')
    def _fine_per_day_to_word_th(self):
        res = {}
        minus = False
        order = self.order_id
        fine_per_day = self.fine_per_day
        if fine_per_day < 0:
            minus = True
            fine_per_day = -fine_per_day
        amount_text = amount_to_text_th(fine_per_day, order.currency_id.name)
        self.amount_fine_per_day_text_th = minus and\
            'ลบ' + amount_text or amount_text
        return res

    @api.onchange('manual_fine')
    def _onchange_manual_fine(self):
        self.total_fine = self.manual_fine

    @api.onchange('date_scheduled_end')
    def _onchange_date_scheduled_end(self):
        THHoliday = self.env['thai.holiday']
        next_working_end_date = THHoliday.\
            find_next_working_day(self.date_scheduled_end)
        self.date_contract_end = next_working_end_date

    @api.onchange('is_manual_fine')
    def _onchange_is_manual_fine(self):
        if not self.is_manual_fine:
            self._compute_total_fine()
            self.manual_fine = 0.0
            self.manual_days = 0

    @api.onchange('date_invoice')
    def _onchange_date_invoice(self):
        Invoice = self.env['account.invoice']
        InvoiceLine = self.env['account.invoice.line']
        self.write_to_invoice = True
        invoice = []
        sup_inv = self.supplier_invoice
        if len(self.acceptance_line_ids) > 0 and self.date_invoice:
            for accept_line in self.acceptance_line_ids:
                if accept_line.product_id.type == 'service':
                    # inv plan case
                    if accept_line.inv_line_id:
                        invoice = Invoice.search([
                            ('id', '=', accept_line.inv_line_id.invoice_id.id),
                        ])
                    # service case
                    else:
                        invoice_line = InvoiceLine.search([
                            ('purchase_line_id', '=', accept_line.line_id.id),
                        ])
                        for inv_line in invoice_line:
                            invoice = Invoice.search([
                                ('id', '=', inv_line.invoice_id.id),
                            ])
                elif accept_line.product_id.type == 'product':
                    invoice = Invoice.search([
                        ('origin', 'like', self.order_id.name),
                    ])
                if len(invoice) > 0:
                    for inv in invoice:
                        inv.write({
                            'date_invoice': self.date_invoice,
                            'supplier_invoice_number': sup_inv,
                            'reference': self.order_id.name,
                        })

    @api.model
    def _check_product_type(self):
        check_type = False
        for line in self.acceptance_line_ids:
            if not check_type:
                check_type = line.product_id.type
                continue
            # if check_type != line.product_id.type:
            #     raise UserError(
            #         _("All products must have the same type. %s"
            #           % (self.name,)))
        return check_type

    @api.model
    def _calculate_service_fine(self):
        total_fine = 0.0
        today = fields.Date.context_today(self)
        if not self.date_receive:
            self.date_receive = today.strftime('%Y-%m-%d')
        received = datetime.datetime.strptime(
            self.date_receive,
            "%Y-%m-%d",
        )
        if not self.date_contract_end:
            self.date_contract_end = today.strftime('%Y-%m-%d')
        end_date = datetime.datetime.strptime(
            self.date_contract_end,
            "%Y-%m-%d",
        )
        delta = end_date - received
        overdue_day = delta.days
        total_fine_per_day = 0.0
        if overdue_day < 0:
            for line in self.acceptance_line_ids:
                fine_rate = self.order_id.fine_rate
                unit_price = line.line_id.price_unit
                to_receive_qty = 1
                fine_per_day = (fine_rate*0.1) * (to_receive_qty * unit_price)
                total_fine_per_day += fine_per_day
                total_fine += -1 * overdue_day * fine_per_day
                total_fine = 100.0 if 0 < total_fine < 100.0 else total_fine
            self.total_fine = total_fine
            self.fine_per_day = total_fine_per_day
            self.overdue_day = -1 * overdue_day

    @api.model
    def _calculate_incoming_fine(self):
        total_fine = 0.0
        today = fields.Date.context_today(self)
        if not self.date_receive:
            self.date_receive = today.strftime('%Y-%m-%d')
        received = datetime.datetime.strptime(
            self.date_receive or '',
            "%Y-%m-%d",
        )
        if not self.date_contract_end:
            self.date_contract_end = today.strftime('%Y-%m-%d')
        end_date = datetime.datetime.strptime(
            self.date_contract_end,
            "%Y-%m-%d",
        )
        delta = end_date - received
        overdue_day = delta.days
        total_fine_per_day = 0.0
        if overdue_day < 0:
            for line in self.acceptance_line_ids:
                fine_rate = self.order_id.fine_rate
                unit_price = line.line_id.price_unit
                to_receive_qty = line.to_receive_qty
                fine_per_day = (fine_rate*0.1) * (to_receive_qty * unit_price)
                total_fine_per_day += fine_per_day
                total_fine += -1 * overdue_day * fine_per_day
                total_fine = 100.0 if 0 < total_fine < 100.0 else total_fine
            self.total_fine = total_fine
            self.fine_per_day = total_fine_per_day
            self.overdue_day = -1 * overdue_day

    @api.one
    @api.depends('date_receive', 'date_contract_end')
    def _compute_total_fine(self):
        product_type = self._check_product_type()
        if product_type == 'service':
            self._calculate_service_fine()
        else:
            self._calculate_incoming_fine()
        if self.manual_fine > 0:
            self.total_fine = self.manual_fine

    name = fields.Char(
        string="Acceptance No.",
        default=lambda self:
        self.env['ir.sequence'].get('purchase.work.acceptance'),
        readonly=True,
    )
    date_contract_start = fields.Date(
        string="Contract Start Date",
        default=lambda self: fields.Date.context_today(self),
    )
    date_scheduled_end = fields.Date(
        string="Scheduled End Date",
        default=lambda self: fields.Date.context_today(self),
    )
    date_contract_end = fields.Date(
        string="Contract End Date",
        default=lambda self: fields.Date.context_today(self),
    )
    date_receive = fields.Date(
        string="Receive Date",
        default=lambda self: fields.Date.context_today(self),
    )
    is_manual_fine = fields.Boolean(
        string="Use Manual Fine",
    )
    manual_fine = fields.Float(
        string="Manual Fine",
        default=0.0,
    )
    manual_days = fields.Integer(
        string="No. of Days",
        default=1,
    )
    fine_per_day = fields.Float(
        string="Fine per Day",
        default=0.0,
    )
    amount_fine_per_day_text_th = fields.Char(
        string='Fine per Day TH Text',
        compute='_fine_per_day_to_word_th',
        store=True,
    )
    overdue_day = fields.Integer(
        string="Overdue Days",
        default=0,
    )
    total_fine = fields.Float(
        string="Total Fine",
        compute="_compute_total_fine",
    )
    amount_total_fine_text_th = fields.Char(
        string='Total Fine TH Text',
        compute='_fine_amount_to_word_th',
        store=True,
    )
    supplier_invoice = fields.Char(
        string="Invoice No.",
    )
    date_invoice = fields.Date(
        string="Invoice Date",
    )
    write_to_invoice = fields.Boolean(
        string="Write to invoice date",
    )
    acceptance_line_ids = fields.One2many(
        'purchase.work.acceptance.line',
        'acceptance_id',
        string='Work Acceptance',
    )
    order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
    )
    eval_receiving = fields.Selection(
        selection=[
            ('3', 'On time'),
            ('2', 'Late for 1-7 days'),
            ('1', 'Late for 8-14 days'),
            ('0', 'Late more than 15 days'),
        ],
        string='Rate - Receiving',
    )
    eval_quality = fields.Selection(
        selection=[
            ('2', 'Better than expectation'),
            ('1', 'As expectation'),
        ],
        string='Rate - Quality',
    )
    eval_service = fields.Selection(
        selection=[
            ('3', 'Excellent'),
            ('2', 'Good'),
            ('1', 'Satisfactory'),
            ('0', 'Needs Improvement'),
        ],
        string='Rate - Service',
    )
    state = fields.Selection(
        selection=_STATES,
        copy=False,
        default='draft',
    )

    @api.multi
    def action_evaluate(self):
        self.ensure_one()
        self.state = 'evaluation'

    @api.multi
    def action_done(self):
        self.ensure_one()
        self.state = 'done'

    @api.multi
    def action_set_draft(self):
        self.ensure_one()
        self.state = 'draft'

    @api.model
    def open_order_line(self, ids):
        Model = self.env['ir.model.data']
        POLine = self.env['purchase.order.line']
        view_id = Model.get_object_reference(
            'purchase',
            'view_purchase_line_invoice'
        )
        wa = self.browse(ids)
        lines = POLine.search([('order_id', '=', wa.order_id.id)])
        return {
            'name': "Create Invoices",
            'view_mode': 'form',
            'view_id': view_id[1],
            'view_type': 'form',
            'res_model': 'purchase.order.line_invoice',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'active_ids': lines.ids,
            }
        }


class PurchaseWorkAcceptanceLine(models.Model):
    _name = 'purchase.work.acceptance.line'
    _description = 'Purchase Work Acceptance Line'

    acceptance_id = fields.Many2one(
        'purchase.work.acceptance',
        string='Acceptance Reference',
        ondelete='cascade',
    )
    line_id = fields.Many2one(
        'purchase.order.line',
        string='Purchase Order Line',
        required=True,
        readonly=True,
    )
    inv_line_id = fields.Many2one(
        'account.invoice.line',
        string='Account Invoice Line',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        readonly=True,
    )
    name = fields.Char(
        string='Description',
        required=True,
    )
    balance_qty = fields.Float(
        string='Balance Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        readonly=True,
        required=True,
    )
    to_receive_qty = fields.Float(
        string='To Receive Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        required=True,
    )
    product_uom = fields.Many2one(
        'product.uom',
        string='UoM',
    )
