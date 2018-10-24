# -*- coding: utf-8 -*-
from datetime import datetime
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
from openerp.tools import float_round as round
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class PurchaseCreateInvoicePlanInstallment(models.TransientModel):
    _inherit = 'purchase.create.invoice.plan.installment'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
    )
    invoice_mode = fields.Selection(
        [
            ('change_price', 'As 1 Job (change price)'),
            ('change_quantity', 'As Units (change quantity)'),
        ],
        default='change_price',
    )

    @api.onchange('percent')
    def _onchange_percent(self):
        if not self.plan_id.by_fiscalyear or\
                self.is_advance_installment or self.is_deposit_installment:
            return super(PurchaseCreateInvoicePlanInstallment, self).\
                _onchange_percent()
        obj_precision = self.env['decimal.precision']
        prec = obj_precision.precision_get('Account')
        line_by_fiscalyear = self.plan_id._get_total_by_fy()
        order_amount = line_by_fiscalyear[self.fiscalyear_id.id]
        self.amount = round(order_amount * self.percent / 100, prec)

    @api.onchange('amount')
    def _onchange_amount(self):
        if not self.plan_id.by_fiscalyear or self.is_advance_installment\
                or self.is_deposit_installment:
            return super(PurchaseCreateInvoicePlanInstallment,
                         self)._onchange_amount()
        obj_precision = self.env['decimal.precision']
        prec = obj_precision.precision_get('Account')
        line_by_fiscalyear = self.plan_id._get_total_by_fy()
        order_amount = line_by_fiscalyear[self.fiscalyear_id.id]
        if not order_amount:
            raise Warning(_('Order amount equal to 0.0!'))
        new_val = self.amount / order_amount * 100
        if round(new_val, prec) != round(self.percent, prec):
            self.percent = new_val


class PurchaseCreateInvoicePlan(models.TransientModel):
    _inherit = 'purchase.create.invoice.plan'
    _description = 'Create Purchase Invoice Plan'

    @api.model
    def _get_total_by_fy(self):
        order = self.po_id
        if self._context.get('active_id', False):
            purchase_id = self._context['active_id']
            order = self.env['purchase.order'].browse(purchase_id)
        line_by_fiscalyear = {}
        for line in order.order_line:
            line_fy = line.fiscalyear_id
            if line_fy:
                if line_fy.id not in line_by_fiscalyear:
                    line_by_fiscalyear[line_fy.id] = line.price_subtotal
                else:
                    line_by_fiscalyear[line_fy.id] += line.price_subtotal
        return line_by_fiscalyear

    @api.model
    def _get_interval_type(self):
        order = self.env['purchase.order'].\
            browse(self._context.get('active_id'))
        selection_list = [('day', 'Day'),
                          ('month', 'Month')]
        if order.by_fiscalyear:
            return selection_list
        else:
            selection_list.append(('year', 'Year'))
            return selection_list

    @api.model
    def _default_order(self):
        return self.env['purchase.order'].\
            browse(self._context.get('active_id'))

    @api.model
    def _default_by_fiscalyear(self):
        order = self.env['purchase.order'].\
            browse(self._context.get('active_id'))
        if order.by_fiscalyear:
            if any([not l.fiscalyear_id for l in order.order_line]):
                raise ValidationError(
                    _('Please set fiscal year on product line'))
        return order.by_fiscalyear

    by_fiscalyear = fields.Boolean(
        string='By Fiscal Year',
        readonly=True,
        default=_default_by_fiscalyear,
    )
    interval_type = fields.Selection(
        _get_interval_type,
    )
    po_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        default=_default_order,
    )
    advance_rounding = fields.Boolean(
        string="Advance Rounding",
        default=True,
        help="When advance is deducted from each invoice with some decimal "
        "points, it will rounded and keep those residual to the last invoice "
        "advance deduction."
    )

    @api.model
    def _get_po_line_fy(self, po):
        """It will return list of fiscal years on po lines of po"""
        fy_list = []
        for line in po.order_line:
            if line.fiscalyear_id:
                if line.fiscalyear_id.id not in fy_list:
                    fy_list.append(line.fiscalyear_id.id)
        return fy_list

    @api.model
    def _validate_installment_date_range(self):
        fy_list = self._get_po_line_fy(self.po_id)
        fy_list = sorted(fy_list)

        first_fy_id = False
        last_fy_id = False
        if fy_list:
            if len(fy_list) == 1:
                first_fy_id = fy_list[0]
                last_fy_id = fy_list[0]
            else:
                first_fy_id = fy_list[0]
                last_fy_id = fy_list[-1]
        if first_fy_id and last_fy_id:
            first_fy = self.env['account.fiscalyear'].browse(first_fy_id)
            last_fy = self.env['account.fiscalyear'].browse(last_fy_id)

            if self.installment_date > last_fy.date_stop or\
                    self.installment_date < first_fy.date_start:
                raise ValidationError(_('Installment date out of range!'))

    @api.one
    @api.onchange('installment_date',
                  'interval_type',
                  'interval',
                  'installment_amount')
    def _onchange_installment_config(self):
        if self.interval < 0:
            raise ValidationError('Negative interval not allowed!')
        return super(PurchaseCreateInvoicePlan,
                     self)._onchange_installment_config()

    @api.model
    def _compute_installment_details(self):
        obj_precision = self.env['decimal.precision']
        prec = obj_precision.precision_get('Account')
        if not self.by_fiscalyear:
            return super(PurchaseCreateInvoicePlan, self).\
                _compute_installment_details()
        # order = self.env['purchase.order'].browse(self._context['active_id'])
        # order._check_invoice_mode()
        fiscalyear_dict = {}
        for f in self.env['account.fiscalyear'].search_read([],
                                                            ['name', 'id']):
            fiscalyear_dict[f['id']] = f['name']

        line_by_fiscalyear = self._get_total_by_fy()
        # line_by_fiscalyear = dict(sorted(line_by_fiscalyear.iteritems()))
        line_by_fiscalyear = \
            OrderedDict(sorted(line_by_fiscalyear.iteritems()))

        line_of_fy = {}
        count = 0
        installment_date = datetime.strptime(self.installment_date, "%Y-%m-%d")
        installment_day = installment_date.day
        for i in self.installment_ids:
            if i.is_advance_installment or i.is_deposit_installment:
                i.date_invoice = self.installment_date
                continue
            interval = self.interval

            if count == 0:
                interval = 0

            if self.interval_type == 'month':
                installment_date =\
                    installment_date + relativedelta(months=+interval)
            elif self.interval_type == 'year':
                installment_date =\
                    installment_date + relativedelta(years=+interval)

            period_obj = self.env['account.period']
            period_ids = period_obj.find(dt=installment_date)
            fy_id = period_ids[0].fiscalyear_id
            i.fiscalyear_id = fy_id
            # Check Fiscal year in invoice plan must not over fiscal year in
            # purchase order line (By POD)
            if i.fiscalyear_id.id not in line_by_fiscalyear.keys():
                raise ValidationError(
                    _('The number of installment and interval \
                       that you must yield invoice plan that \
                       cover all fiscal years.'))
            # --
            if i.fiscalyear_id.id not in line_of_fy:
                line_of_fy[i.fiscalyear_id.id] = 1
            else:
                line_of_fy[i.fiscalyear_id.id] += 1
            i.date_invoice = installment_date
            count += 1

        new_line_dict = {}
        installment_no = 1
        if line_of_fy:
            for l in line_by_fiscalyear:
                if len(line_by_fiscalyear) == self.num_installment:
                    number_of_lines = 1
                else:
                    if l not in line_of_fy.keys():
                        raise ValidationError(
                            _('The number of installment and interval \
                               that you must yield invoice plan that \
                               cover all fiscal years.'))
                    number_of_lines = line_of_fy[l]
                remaining_amt = line_by_fiscalyear[l]
                line_cnt = number_of_lines
                while line_cnt > 0:
                    if self.env.context.get('from_installment_amount', False):
                        installment_amt = self.installment_amount
                    else:
                        if l in line_of_fy.keys():
                            installment_amt = (line_by_fiscalyear[l] /
                                               line_of_fy[l])
                        else:
                            installment_amt = self.installment_amount
                    if line_cnt == 1 or\
                            installment_no == self.num_installment or\
                            remaining_amt < self.installment_amount:
                        installment_amt = remaining_amt
                    if installment_amt < 0:
                        installment_amt = 0
                    remaining_amt -= installment_amt
                    new_line_dict[installment_no] =\
                        (fiscalyear_dict[l], installment_amt, l)
                    installment_no += 1
                    line_cnt -= 1
        for i in self.installment_ids:
            if i.is_advance_installment or i.is_deposit_installment:
                continue
            if i.installment in new_line_dict:
                f_amount = line_by_fiscalyear[new_line_dict[i.installment][2]]

                if i.fiscalyear_id.id != new_line_dict[i.installment][2]:
                    i.fiscalyear_id = new_line_dict[i.installment][2]

                    fy_start_date = datetime.strptime(
                        i.fiscalyear_id.date_start, "%Y-%m-%d")
                    date_str = str(fy_start_date.month) + '/' + \
                        str(installment_day) + '/' + str(fy_start_date.year)
                    i.date_invoice = datetime.strptime(date_str, '%m/%d/%Y')

                i.amount = new_line_dict[i.installment][1]
                new_val = i.amount / f_amount * 100
                if round(new_val, prec) != round(i.percent, prec):
                    i.percent = new_val

    @api.multi
    def do_create_purchase_invoice_plan(self):
        self.ensure_one()
        order = self.env['purchase.order'].browse(self._context['active_id'])
        if not self.by_fiscalyear:
            order.advance_rounding = self.advance_rounding
            return super(PurchaseCreateInvoicePlan,
                         self).do_create_purchase_invoice_plan()
        self._validate_installment_date_range()
        self._validate_total_amount()
        self._check_installment_amount()
        self.env['purchase.invoice.plan']._validate_installment_date(
            self.installment_ids)
        # order = self.env['purchase.order'].browse(self._context['active_id'])
        # order._check_invoice_mode()
        order.invoice_plan_ids.unlink()
        lines = []

        for install in self.installment_ids:
            if install.installment == 0:
                self._check_deposit_account()
                if install.is_advance_installment:
                    line_data = self._prepare_advance_line(order, install)
                    lines.append(line_data)
                if install.is_deposit_installment:
                    line_data = self._prepare_deposit_line(order, install)
                    lines.append(line_data)
            elif install.installment > 0:
                for order_line in order.order_line:
                    if order_line.fiscalyear_id == install.fiscalyear_id:
                        line_data = self._prepare_installment_line(order,
                                                                   order_line,
                                                                   install)
                        lines.append(line_data)
        order.invoice_plan_ids = lines
        order.use_advance = self.use_advance
        order.use_deposit = self.use_deposit
        order.advance_rounding = self.advance_rounding
        order.invoice_mode = self.invoice_mode

    @api.model
    def _prepare_installment_line(self, order, order_line, install):
        result = super(PurchaseCreateInvoicePlan, self).\
            _prepare_installment_line(order, order_line, install)
        if not self.by_fiscalyear:
            return result
        result.update({'fiscalyear_id': install.fiscalyear_id.id})
        return result

    @api.model
    def _prepare_advance_deposit_line(self, order, install, advance, deposit):
        result = super(PurchaseCreateInvoicePlan, self).\
            _prepare_advance_deposit_line(order, install, advance, deposit)
        if not self.by_fiscalyear:
            return result
        result.update({'fiscalyear_id': install.fiscalyear_id.id})
        return result

    @api.model
    def _check_deposit_account(self):
        """ Overwrite, do not check anything """
        pass
        # company = self.env.user.company_id
        # account_id = company.account_deposit_supplier.id
        # if not account_id:
        #     raise except_orm(
        #         _('Configuration Error!'),
        #         _('There is no deposit customer account '
        #           'defined as global property.')
        #     )
