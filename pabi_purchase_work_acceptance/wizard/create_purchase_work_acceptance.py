# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
import openerp.addons.decimal_precision as dp
import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools.float_utils import float_compare


class CreatePurchaseWorkAcceptance(models.TransientModel):
    _name = 'create.purchase.work.acceptance'

    @api.model
    def _get_invoice_plan(self):
        res = []
        Plan = self.env['purchase.invoice.plan']
        if 'active_id' in self._context:
            plans = Plan.search(
                [
                    ('order_id', '=', self._context['active_id']),
                    ('ref_invoice_id.state', '=', 'draft'),
                ],
                order='installment'
            )
            installments = list(set(plans.mapped('installment')))
            if 0 in installments:
                installments.pop(0)
            for i in installments:
                ip = plans.filtered(lambda l: l.installment == i)
                amount = sum(ip.mapped('deposit_amount')) + \
                    sum(ip.mapped('invoice_amount'))
                descriptions = ip.mapped('description')
                name = '#%s - %s, %s' % \
                    (i, ', '.join(descriptions), '{:,.2f}'.format(amount))
                res.append((i, name))
        return res

    name = fields.Char(
        string="Acceptance No.",
        size=500,
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
    select_invoice_plan = fields.Selection(
        _get_invoice_plan,
        string='Select the Invoice Plan',
        select=True,
    )

    @api.multi
    def _prepare_acceptance_plan_line(self, plan_installment):
        self.ensure_one()
        Plan = self.env['purchase.invoice.plan']
        items = []
        plans = Plan.search(
            [
                ('order_id', '=', self._context['active_id']),
                ('ref_invoice_id.state', '=', 'draft'),
                ('installment', '=', plan_installment),
            ],
        )
        for plan in plans:
            if len(plan.ref_invoice_id) == 0:
                raise ValidationError(_("You have to create invoices first."))
            for inv_line in plan.ref_invoice_id.invoice_line:
                if not inv_line.product_id.id:
                    continue
                taxes = [(4, tax.id) for tax in inv_line.invoice_line_tax_id]
                vals = {
                    'line_id': inv_line.purchase_line_id.id,
                    'product_id': inv_line.product_id.id,
                    'name': inv_line.name or inv_line.product_id.name,
                    'balance_qty': inv_line.purchase_line_id.product_qty,
                    'to_receive_qty': inv_line.quantity,
                    'product_uom': inv_line.uos_id.id,
                    'inv_line_id': inv_line.id,
                    'tax_ids': taxes,
                    'price_unit': inv_line.price_unit,
                }
                items.append([0, 0, vals])
            break
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
    def is_acceptance_done(self, order):
        #  immediate payment
        # if order.payment_term_id.id == 1 or order.payment_term_id.name == \
        #         'Cash on Delivery':
        #     return True
        OrderLine = self.env['purchase.order.line']
        completed_line = 0
        order_lines = OrderLine.search([
            ('order_id', '=', order.id),
        ])
        for order_line in order_lines:
            if float_compare(order_line.invoiced_qty,
                             order_line.product_qty, 2) >= 0:
                completed_line += 1
        if completed_line == len(order_lines) and \
                order.invoice_method == 'picking':
            raise ValidationError(
                _("""Can't create new work acceptance.
                This order's shipments may be completed.
                """)
            )

    @api.model
    def _get_contract_end_date(self, order):
        THHoliday = self.env['thai.holiday']
        if not order.date_contract_start:
            raise ValidationError(_('No contract start date!'))
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
        if order.fine_condition == 'month':
            num_months = order.fine_num_months
            end_date = start_date + relativedelta(months=+num_months)
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
            self.is_acceptance_done(order)
            order_lines = OrderLine.search([('order_id', 'in', order_ids)])
            for line in order_lines:
                if not hasattr(line, 'product_uom'):
                    raise ValidationError(
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
            'date_scheduled_end': self.date_contract_end,
            'date_contract_start': self.date_contract_start,
            'date_contract_end': self.date_contract_end,
            'date_receive': self.date_receive,
            'order_id': self.order_id.id,
            'supplier_invoice': '-',
            'date_invoice': self.date_receive,
            'total_fine': 0,
            'installment': self.select_invoice_plan,
        })
        acceptance = PWAcceptance.create(vals)
        if self.is_invoice_plan:
            items = \
                self._prepare_acceptance_plan_line(self.select_invoice_plan)
            lines = items
        else:
            for act_line in self.acceptance_line_ids:
                taxes = [(4, tax.id) for tax in act_line.line_id.taxes_id]
                line_vals = {
                    'line_id': act_line.line_id.id,
                    'name': act_line.name,
                    'product_id': act_line.product_id.id or False,
                    'balance_qty': act_line.balance_qty,
                    'to_receive_qty': act_line.to_receive_qty,
                    'product_uom': act_line.product_uom.id,
                    'tax_ids': taxes,
                    'price_unit': act_line.line_id.price_unit,
                }
                lines.append([0, 0, line_vals])
        acceptance.write({'acceptance_line_ids': lines})
        acceptance._compute_total_fine()
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
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'purchase.work.acceptance',
            'target': 'current',
            'context': self._context,
            'res_id': acceptance.id,
            'domain': [('order_id', '=', active_ids[0])],
        }


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
        size=500,
    )
    balance_qty = fields.Float(
        string='Balance Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'),
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
        size=500,
    )

    @api.multi
    def name_get(self):
        result = []
        for invoice_plan in self:
            result.append(
                (invoice_plan.id,
                 "%s %s/ Installment #%s" % (
                     invoice_plan.order_id.name,
                     invoice_plan.order_line_id.name,
                     invoice_plan.installment,
                 )))
        return result
