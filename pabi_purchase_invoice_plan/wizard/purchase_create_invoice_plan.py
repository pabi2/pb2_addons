# -*- coding: utf-8 -*-
from datetime import datetime

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError

class PurchaseCreateInvoicePlanInstallment(models.TransientModel):
    _inherit = 'purchase.create.invoice.plan.installment'
    
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
    )
    
class PurchaseCreateInvoicePlan(models.TransientModel):
    _inherit = 'purchase.create.invoice.plan'
    _description = 'Create Purchase Invoice Plan'


    @api.model
    def _default_by_fiscalyear(self):
        order = self.env['purchase.order'].\
            browse(self._context.get('active_id'))
        if order.by_fiscalyear:
            if any([not l.fiscalyear_id for l in order.order_line]):
                raise UserError(_('Please set fiscal year on product line'))
        return order.by_fiscalyear

    by_fiscalyear = fields.Boolean(
        string='By Fiscal Year',
        readonly=True,
        default=_default_by_fiscalyear,
    )

    @api.model
    def _compute_installment_details(self):
        obj_precision = self.env['decimal.precision']
        prec = obj_precision.precision_get('Account')
        if not self.by_fiscalyear:
            return super(PurchaseCreateInvoicePlan, self).\
                    _compute_installment_details()
        order = self.env['purchase.order'].browse(self._context['active_id'])
        self._check_invoice_mode(order)
        fiscalyear_dict = {}

        for f in self.env['account.fiscalyear'].search_read([],['name', 'id']):
            fiscalyear_dict[f['id']] = f['name']

        line_by_fiscalyear = {}
        for line in order.order_line:
            if line.fiscalyear_id:
                if line.fiscalyear_id.id not in line_by_fiscalyear:
                    line_by_fiscalyear[line.fiscalyear_id.id] = line.price_subtotal
                else:
                    line_by_fiscalyear[line.fiscalyear_id.id] += line.price_subtotal
        line_by_fiscalyear = dict(sorted(line_by_fiscalyear.iteritems()))
        print "line_by_fiscalyear:::::::::::::",line_by_fiscalyear
        new_line_dict = {}
        installment_no = 1
        for l in line_by_fiscalyear:
            line_total = line_by_fiscalyear[l]
            line_percentage = (100 * line_total) / order.amount_total
            number_of_lines = (line_percentage * self.num_installment) / 100
            number_of_lines = round(number_of_lines)
            remaining_amt = line_by_fiscalyear[l]
            line_cnt = number_of_lines
            
            while line_cnt > 0:
                installment_amt = self.installment_amount
                if line_cnt == 1 or installment_no == self.num_installment or\
                        remaining_amt < self.installment_amount:
                    installment_amt = remaining_amt
                if installment_amt < 0:
                    installment_amt = 0
                remaining_amt -= self.installment_amount
                new_line_dict[installment_no] =\
                    (fiscalyear_dict[l], installment_amt, l)
                installment_no += 1
                line_cnt -= 1
        print "new_line_dict:::::::::::",new_line_dict
        for i in self.installment_ids:
            if i.is_advance_installment or i.is_deposit_installment:
                continue
            if i.installment in new_line_dict:
                f_amount = line_by_fiscalyear[new_line_dict[i.installment][2]]
                i.fiscalyear_id = new_line_dict[i.installment][2]
                i.amount = new_line_dict[i.installment][1]
                new_val = i.amount / f_amount * 100
                if round(new_val, prec) != round(i.percent, prec):
                    i.percent = new_val
                fy = new_line_dict[i.installment][0]
                i.date_invoice = datetime.strptime('01/01/' + fy, '%m/%d/%Y')

    @api.one
    def do_create_purchase_invoice_plan(self):
        if not self.by_fiscalyear:
            return super(PurchaseCreateInvoicePlan, self).do_create_purchase_invoice_plan()
        self._validate_total_amount()
        self._check_installment_amount()
        self.env['purchase.invoice.plan']._validate_installment_date(
            self.installment_ids)
        order = self.env['purchase.order'].browse(self._context['active_id'])
        self._check_invoice_mode(order)
        order.invoice_plan_ids.unlink()
        lines = []
        obj_precision = self.env['decimal.precision']
        prec = obj_precision.precision_get('Account')
        for install in self.installment_ids:
            if install.installment == 0:
                self._check_deposit_account()
                base_amount = order.amount_untaxed
                if install.is_advance_installment:
                    lines.append({
                        'order_id': order.id,
                        'order_line_id': False,
                        'installment': 0,
                        'description': install.description,
                        'is_advance_installment': True,
                        'date_invoice': install.date_invoice,
                        'deposit_percent': install.percent,
                        'deposit_amount': round(install.percent/100 *
                                                base_amount, prec)
                    })
                if install.is_deposit_installment:
                    lines.append({
                        'order_id': order.id,
                        'order_line_id': False,
                        'installment': 0,
                        'description': install.description,
                        'is_deposit_installment': True,
                        'date_invoice': install.date_invoice,
                        'deposit_percent': install.percent,
                        'deposit_amount': round(install.percent/100 *
                                                base_amount, prec)
                    })
            elif install.installment > 0:
                for order_line in order.order_line:
                    print "install fiscalyear........",install.fiscalyear_id.code
                    print "order_line::::::::::",order_line, order_line.fiscalyear_id.code
                    if order_line.fiscalyear_id == install.fiscalyear_id:
                        subtotal = order_line.price_subtotal
                        lines.append({
                            'order_id': order.id,
                            'order_line_id': order_line.id,
                            'description': order_line.name,
                            'installment': install.installment,
                            'date_invoice': install.date_invoice,
                            'invoice_percent': install.percent,
                            'invoice_amount': round(install.percent/100 *
                                                    subtotal, prec),
                            'fiscalyear_id': install.fiscalyear_id.id,
                        })
        print "lines:::::::::::::::::::::::::",lines
        order.invoice_plan_ids = lines
        order.use_advance = self.use_advance
        order.use_deposit = self.use_deposit
        order.invoice_mode = self.invoice_mode


