# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
import datetime
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning as UserError


class PurchaseWorkAcceptance(models.Model):
    _name = 'purchase.work.acceptance'
    _description = 'Purchase Work Acceptance'

    _STATES = [
        ('draft', 'Draft'),
        ('evaluation', 'Evaluation'),
        ('done', 'Done'),
    ]

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
        if len(self.acceptance_line_ids) > 0 and self.date_invoice:
            for acceptance_line in self.acceptance_line_ids:
                if acceptance_line.product_id.type == 'service':
                    Invoice = self.env['account.invoice']
                    InvoiceLine = self.env['account.invoice.line']
                    # invoice plan invoice
                    invoice = Invoice.search([
                        ('id', '=', acceptance_line.inv_line_id.invoice_id.id),
                        ('state', '=', 'draft'),
                    ])
                    if len(invoice) > 0:
                        for inv in invoice:
                            self.write_to_invoice = True
                            inv.date_invoice = self.date_invoice
                            break
                    else:
                        # service invoice
                        invoice_line = InvoiceLine.search([
                            ('purchase_line_id', '=',
                             acceptance_line.line_id.id),
                        ])
                        for inv_line in invoice_line:
                            self.write_to_invoice = True
                            inv_line.invoice_id.date_invoice = \
                                self.date_invoice

    @api.model
    def _check_product_type(self):
        check_type = False
        for line in self.acceptance_line_ids:
            if not check_type:
                check_type = line.product_id.type
                continue
            if check_type != line.product_id.type:
                raise UserError(
                    _("All products must have the same type."))
        return check_type

    @api.model
    def _calculate_service_fine(self):
        total_fine = 0.0
        if not self.date_receive:
            self.date_receive = fields.date.today().strftime('%Y-%m-%d')
        received = datetime.datetime.strptime(
            self.date_receive,
            "%Y-%m-%d",
        )
        if not self.date_contract_end:
            self.date_contract_end = fields.date.today().strftime('%Y-%m-%d')
        end_date = datetime.datetime.strptime(
            self.date_contract_end,
            "%Y-%m-%d",
        )
        delta = end_date - received
        overdue_day = delta.days
        if overdue_day < 0:
            for line in self.acceptance_line_ids:
                fine_rate = self.order_id.fine_rate
                unit_price = line.line_id.price_unit
                to_receive_qty = 1
                fine_per_day = fine_rate * (to_receive_qty * unit_price)
                total_fine += -1 * overdue_day * fine_per_day
                total_fine = 100.0 if 0 < total_fine < 100.0 else total_fine
            self.total_fine = total_fine

    @api.model
    def _calculate_incoming_fine(self):
        total_fine = 0.0
        if not self.date_receive:
            self.date_receive = fields.date.today().strftime('%Y-%m-%d')
        received = datetime.datetime.strptime(
            self.date_receive or '',
            "%Y-%m-%d",
        )
        if not self.date_contract_end:
            self.date_contract_end = fields.date.today().strftime('%Y-%m-%d')
        end_date = datetime.datetime.strptime(
            self.date_contract_end,
            "%Y-%m-%d",
        )
        delta = end_date - received
        overdue_day = delta.days
        if overdue_day < 0:
            for line in self.acceptance_line_ids:
                fine_rate = self.order_id.fine_rate
                unit_price = line.line_id.price_unit
                to_receive_qty = line.to_receive_qty
                fine_per_day = fine_rate * (to_receive_qty * unit_price)
                total_fine += -1 * overdue_day * fine_per_day
                total_fine = 100.0 if 0 < total_fine < 100.0 else total_fine
            self.total_fine = total_fine

    @api.one
    @api.depends('date_receive', 'date_contract_end')
    def _compute_total_fine(self):
        product_type = self._check_product_type()
        if product_type == 'service':
            self._calculate_service_fine()
        else:
            self._calculate_incoming_fine()

    name = fields.Char(
        string="Acceptance No.",
        default=lambda self:
        self.env['ir.sequence'].get('purchase.work.acceptance'),
        readonly=True,
    )
    date_scheduled_end = fields.Date(
        string="Scheduled End Date",
        default=fields.Date.today(),
    )
    date_contract_end = fields.Date(
        string="Contract End Date",
        default=fields.Date.today(),
    )
    date_receive = fields.Date(
        string="Receive Date",
        default=fields.Date.today(),
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
    total_fine = fields.Float(
        string="Total Fine",
        compute="_compute_total_fine",
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
