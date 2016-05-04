# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
import openerp.addons.decimal_precision as dp
import datetime


class PrintPurchaseWorkAcceptance(models.TransientModel):

    _name = 'print.purchase.work.acceptance'

    name = fields.Char(
        string="Acceptance No.",
        required=True,
    )
    acceptance_line = fields.One2many(
        'print.purchase.work.acceptance.item',
        'wiz_id',
        string='Acceptance Lines',
    )
    date_scheduled_end = fields.Date(
        string="Scheduled End Date",
    )
    date_contract_end = fields.Date(
        string="Contract End Date",
    )
    date_received = fields.Date(
        string="Receive Date",
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
        default=0,
    )
    total_fine = fields.Float(
        string="Total Fine",
        default=0.0,
        compute='_compute_total_fine',
        store=True,
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
        domain=[
            ('state', '=', 'draft'),
        ],
    )
    picking_id = fields.Many2one(
        'stock.picking',
        string='Incoming',
        domain=[
            ('picking_type_id.code', '=', 'incoming'), ('state', '=', 'done')
        ],
    )

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

    # @api.one
    # @api.depends('date_received')
    # def _prepare_invoice(self):
    #     inv_list = []
    #     AcctInvoice = self.env['account.invoice']
    #     AcctInvoiceLine = self.env['account.invoice.line']
    #     for accptline in self.acceptance_line:
    #         inv_line = AcctInvoiceLine.search([
    #             ('purchase_line_id.id', '=', accptline.line_id.id),
    #         ])
    #         inv_list.append(inv_line.invoice_id.id)
    #     AcctInv = AcctInvoice.search([
    #         ('id', 'in', inv_list),
    #         ('state', 'in', ['draft']),
    #     ])
    #     if len(AcctInv) > 0:
    #         self.invoice_id = AcctInv._ids

    @api.model
    def _check_product_type(self):
        check_type = False
        for line in self.acceptance_line:
            if not check_type:
                check_type = line.product_id.type
            if check_type != line.product_id.type:
                raise UserError(
                    _("All products must have the same type."))
        return check_type

    @api.model
    def _calculate_service_fine(self):
        total_fine = 0.0
        received = datetime.datetime.strptime(
            self.date_received,
            "%Y-%m-%d",
        )
        end_date = datetime.datetime.strptime(
            self.date_contract_end,
            "%Y-%m-%d",
        )
        delta = end_date - received
        overdue_day = delta.days
        if overdue_day < 0:
            for line in self.acceptance_line:
                fine_rate = line.line_id.order_id.fine_rate
                unit_price = line.line_id.price_unit
                to_receive_qty = 1
                fine_per_day = fine_rate * (to_receive_qty * unit_price)
                total_fine += -1 * overdue_day * fine_per_day
            self.total_fine = total_fine

    @api.model
    def _calculate_incoming_fine(self):
        total_fine = 0.0
        received = datetime.datetime.strptime(
            self.date_received,
            "%Y-%m-%d",
        )
        end_date = datetime.datetime.strptime(
            self.date_contract_end,
            "%Y-%m-%d",
        )
        delta = end_date - received
        overdue_day = delta.days
        if overdue_day < 0:
            for line in self.acceptance_line:
                fine_rate = line.line_id.order_id.fine_rate
                unit_price = line.line_id.price_unit
                to_receive_qty = 1
                fine_per_day = fine_rate * (to_receive_qty * unit_price)
                total_fine += -1 * overdue_day * fine_per_day
            self.total_fine = total_fine

    @api.one
    @api.depends('date_received', 'date_contract_end')
    def _compute_total_fine(self):
        product_type = self._check_product_type()
        if product_type == 'service':
            self._calculate_service_fine()
        else:
            self._calculate_incoming_fine()

    @api.model
    def _prepare_item(self, line):
        return {
            'line_id': line.id,
            'product_id': line.product_id.id,
            'name': line.name or line.product_id.name,
            'balance_qty': line.product_qty - line.received_qty,
            'to_receive_qty': 0.0,
            'product_uom': line.product_uom.id,
        }

    @api.model
    def _get_contract_end_date(self, order):
        THHoliday = self.env['thai.holiday']
        start_date = datetime.datetime.strptime(
            order.date_contract_start,
            "%Y-%m-%d",
        )
        if order.fine_condition == 'day':
            num_of_day = order.fine_by_num_of_days
            end_date = start_date + datetime.timedelta(days=num_of_day)
            date_scheduled_end = "{:%Y-%m-%d}".format(end_date)
            next_working_end_date = THHoliday.\
                find_next_working_day(date_scheduled_end)
        elif order.fine_condition == 'date':
            date_scheduled_end = order.fine_by_date
            next_working_end_date = THHoliday.\
                find_next_working_day(order.fine_by_date)
        return date_scheduled_end, next_working_end_date

    @api.model
    def default_get(self, fields):
        res = {}
        Order = self.env['purchase.order']
        OrderLine = self.env['purchase.order.line']
        order_ids = self.env.context['active_ids'] or []
        assert len(order_ids) == 1, \
            'Only one order should be printed.'
        items = []
        order_lines = OrderLine.search([('order_id', 'in', order_ids)])
        for line in order_lines:
            if not hasattr(line, 'product_uom'):
                raise UserError(
                    _("Unit of Measure is missing in some PO line."))
            items.append([0, 0, self._prepare_item(line)])
        res['acceptance_line'] = items
        order = Order.search([('id', 'in', order_ids)])
        date_scheduled_end, end_date = self._get_contract_end_date(order)
        res['date_scheduled_end'] = date_scheduled_end
        res['date_contract_end'] = end_date
        today = datetime.datetime.now()
        res['date_received'] = "{:%Y-%m-%d}".format(today)
        return res

    @api.model
    def _prepare_acceptance(self):
        lines = []
        vals = {}
        PWAcceptance = self.env['purchase.work.acceptance']
        if self.is_manual_fine:
            total = self.manual_fine
        else:
            total = self.total_fine
        vals.update({
            'name': self.name,
            'date_scheduled_end': self.date_scheduled_end,
            'date_contract_end': self.date_contract_end,
            'date_received': self.date_received,
            'is_manual_fine': self.is_manual_fine,
            'manual_fine': self.manual_fine,
            'manual_days': self.manual_days,
            'invoice_id': self.invoice_id.id,
            'picking_id': self.picking_id.id,
            'total_fine': total,
        })
        acceptance = PWAcceptance.create(vals)
        for act_line in self.acceptance_line:
            line_vals = {
                'name': act_line.name,
                'product_id': act_line.product_id.id or False,
                'balance_qty': act_line.balance_qty,
                'to_receive_qty': act_line.to_receive_qty,
                'product_uom': act_line.product_uom.id,
            }
            lines.append([0, 0, line_vals])
        acceptance.acceptance_line = lines
        return acceptance

    @api.multi
    def action_print(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        active_ids = self._context.get('active_ids')
        if active_ids is None:
            return act_close
        assert len(active_ids) == 1, "Only 1 Purchase Order expected"
        acceptance = self._prepare_acceptance()
        acceptance.order_id = active_ids[0]
        return act_close


class PrintPurchaseWorkAcceptanceItem(models.TransientModel):

    _name = 'print.purchase.work.acceptance.item'

    wiz_id = fields.Many2one(
        'print.purchase.work.acceptance',
        string='Acceptance Reference',
        ondelete='cascade',
    )
    line_id = fields.Many2one(
        'purchase.order.line',
        string='Purchase Order Line',
        required=True,
        readonly=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        readonly=True,
    )
    name = fields.Char(
        string='Description',
        required=True,
        readonly=True,
    )
    balance_qty = fields.Float(
        string='Balance Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        required=True,
        readonly=True,
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
