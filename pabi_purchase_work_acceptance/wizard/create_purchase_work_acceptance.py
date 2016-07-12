# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
import openerp.addons.decimal_precision as dp
import datetime


class CreatePurchaseWorkAcceptance(models.TransientModel):
    _name = 'create.purchase.work.acceptance'

    name = fields.Char(
        string="Acceptance No.",
    )
    acceptance_line_ids = fields.One2many(
        'create.purchase.work.acceptance.item',
        'wiz_id',
        string='Acceptance Lines',
    )
    date_scheduled_end = fields.Date(
        string="Scheduled End Date",
    )
    date_contract_start = fields.Date(
        string="Contract Start Date",
    )
    date_contract_end = fields.Date(
        string="Contract End Date",
    )
    date_receive = fields.Date(
        string="Receive Date",
    )
    order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
    )
    is_invoice_plan = fields.Boolean(
        string='Is Invoice Plan',
    )
    invoice_plan_id = fields.Many2one(
        'purchase.invoice.plan',
        string='Invoice Plan',
        domain="[('order_id', '=',order_id)]",
    )

    @api.model
    def _prepare_acceptance_plan_line(self, plan):
        items = []
        if len(plan.ref_invoice_id) == 0:
            raise UserError(_("You have to create invoices first."))
        for inv_line in plan.ref_invoice_id.invoice_line:
            vals = {
                'line_id': inv_line.purchase_line_id.id,
                'product_id': inv_line.product_id.id,
                'name': inv_line.name or inv_line.product_id.name,
                'balance_qty': inv_line.purchase_line_id.product_qty,
                'to_receive_qty': inv_line.quantity,
                'product_uom': inv_line.uos_id.id,
                'inv_line_id': inv_line.id,
            }
            items.append([0, 0, vals])
        return items

    @api.model
    def _prepare_item(self, line):
        if line.product_id.type == 'service':
            balance = line.product_qty
        else:
            balance = line.product_qty - line.received_qty
        return {
            'line_id': line.id,
            'product_id': line.product_id.id,
            'name': line.name or line.product_id.name,
            'balance_qty': balance,
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
            num_of_day = order.fine_num_days
            end_date = start_date + datetime.timedelta(days=num_of_day)
            date_scheduled_end = "{:%Y-%m-%d}".format(end_date)
            next_working_end_date = THHoliday.\
                find_next_working_day(date_scheduled_end)
        elif order.fine_condition == 'date':
            date_scheduled_end = order.date_fine
            next_working_end_date = THHoliday.\
                find_next_working_day(order.date_fine)
        return date_scheduled_end, next_working_end_date

    @api.model
    def default_get(self, fields):
        res = {}
        items = []
        Order = self.env['purchase.order']
        OrderLine = self.env['purchase.order.line']
        order_ids = self.env.context['active_ids'] or []
        assert len(order_ids) == 1, \
            'Only one order should be created.'
        order = Order.search([('id', 'in', order_ids)])
        if order.invoice_method == 'invoice_plan':
            res['is_invoice_plan'] = True
        else:
            order_lines = OrderLine.search([('order_id', 'in', order_ids)])
            for line in order_lines:
                if not hasattr(line, 'product_uom'):
                    raise UserError(
                        _("Unit of Measure is missing in some PO line."))
                items.append([0, 0, self._prepare_item(line)])
        res['order_id'] = order.id
        res['acceptance_line_ids'] = items
        date_scheduled_end, end_date = self._get_contract_end_date(order)
        res['date_scheduled_end'] = date_scheduled_end
        res['date_contract_start'] = order.date_contract_start
        res['date_contract_end'] = end_date
        today = datetime.datetime.now()
        res['date_receive'] = "{:%Y-%m-%d}".format(today)
        return res

    @api.model
    def _prepare_acceptance(self):
        lines = []
        vals = {}
        PWAcceptance = self.env['purchase.work.acceptance']
        vals.update({
            'name': self.env['ir.sequence'].get('purchase.work.acceptance'),
            'date_scheduled_end': self.date_scheduled_end,
            'date_contract_start': self.date_contract_start,
            'date_contract_end': self.date_contract_end,
            'date_receive': self.date_receive,
            'order_id': self.order_id.id,
        })
        acceptance = PWAcceptance.create(vals)
        if self.is_invoice_plan:
            items = self._prepare_acceptance_plan_line(self.invoice_plan_id)
            lines = items
        else:
            for act_line in self.acceptance_line_ids:
                line_vals = {
                    'line_id': act_line.line_id.id,
                    'name': act_line.name,
                    'product_id': act_line.product_id.id or False,
                    'balance_qty': act_line.balance_qty,
                    'to_receive_qty': act_line.to_receive_qty,
                    'product_uom': act_line.product_uom.id,
                }
                lines.append([0, 0, line_vals])
        acceptance.acceptance_line_ids = lines
        return acceptance

    @api.multi
    def action_create_acceptance(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        active_ids = self._context.get('active_ids')
        if active_ids is None:
            return act_close
        assert len(active_ids) == 1, "Only 1 Purchase Order expected"
        acceptance = self._prepare_acceptance()
        acceptance.order_id = active_ids[0]
        return act_close


class CreatePurchaseWorkAcceptanceItem(models.TransientModel):

    _name = 'create.purchase.work.acceptance.item'

    wiz_id = fields.Many2one(
        'create.purchase.work.acceptance',
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


class PurchaseInvoicePlan(models.Model):
    _inherit = 'purchase.invoice.plan'

    name = fields.Char(
        string='Invoice Plan',
    )

    @api.multi
    def name_get(self):
        result = []
        for invoice_plan in self:
            result.append(
                (invoice_plan.id,
                 "%s %s/ Installment #%s" % (
                     invoice_plan.order_line_id.name,
                     invoice_plan.order_id.name,
                     invoice_plan.installment,
                 )))
        return result
