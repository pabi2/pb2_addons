# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, Warning as UserError


class HRExpense(models.Model):
    _inherit = "hr.expense.expense"

    pay_to = fields.Selection(
        selection_add=[('internal', 'Internal Charge')],
    )
    internal_section_id = fields.Many2one(
        'res.section',
        string='Internal Section',
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        compute='_compute_activity_group_id',
        readonly=True,
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        domain=[('budget_method', '=', 'revenue')],
    )

    @api.one
    @api.constrains('pay_to')
    def _check_pay_to_internal_charge(self):
        if self.pay_to == 'internal':
            if self.is_employee_advance or self.is_advance_clearing:
                raise ValidationError(_('Only Expense can be Interal Charge!'))

    @api.multi
    @api.depends('activity_id')
    def _compute_activity_group_id(self):
        for rec in self:
            rec.activity_group_id = rec.activity_id.activity_group_ids and \
                rec.activity_id.activity_group_ids[0] or False

    @api.model
    def _is_create_invoice(self):
        if self.pay_to == 'internal':  # Do not create invoice for IC
            return False
        return True

    @api.model
    def _is_valid_for_invoice(self):
        res = super(HRExpense, self)._is_valid_for_invoice()
        if self.pay_to == 'internal':  # Do not create invoice for IC
            raise ValidationError(
                _('For internal charge, it is not allowed to create invoice'))
        return res

    @api.multi
    def create_internal_charge_move(self):
        for expense in self:  # If IC
            if expense.pay_to != 'internal':
                raise ValidationError(
                    _('For internal charge only!'))

            Move = self.env['account.move']
            employee = expense.employee_id
            company_currency = expense.company_id.currency_id.id
            diff_curr_p = expense.currency_id.id != company_currency
            # create the move that will contain the accounting entries
            move = Move.create(self.account_move_get(expense.id))
            # one account.move.line per expense line (+taxes..)
            eml = self.move_line_get(expense.id)
            # create one more move line,
            # a counterline for the total on payable account
            total, total_currency, eml = \
                self.compute_expense_totals(expense,
                                            company_currency,
                                            expense.name, eml)
            acc = expense.activity_id.account_id.id
            eml.append({
                'type': 'dest',
                'name': '/',
                'price': total,
                'account_id': acc,
                'date_maturity': expense.date_confirm,
                'amount_currency': diff_curr_p and total_currency or False,
                'currency_id': diff_curr_p and expense.currency_id.id or False,
                'ref': expense.name
            })
            # convert eml into an osv-valid format
            lines = map(lambda x:
                        (0, 0,
                         self.line_get_convert(x, employee.address_home_id,
                                               expense.date_confirm)), eml)
            journal = move.journal

            if journal.entry_posted:
                move.button_validate()
            move.write({'line_id': lines})
            expense.account_move_id = move
        return True

    # @api.model
    # def move_line_get(self, expense_id):
    #     res = []
    #     tax_obj = self.env['account.tax']
    #     cur_obj = self.env['res.currency']
    #     exp = self.browse(expense_id)
    #     company_currency = exp.company_id.currency_id.id
    #
    #     for line in exp.line_ids:
    #         mres = self.move_line_get_item(line)
    #         if not mres:
    #             continue
    #         res.append(mres)
    #
    #         # Calculate tax according to default tax on product
    #         taxes = []
    #         # Taken from product_id_onchange in account.invoice
    #         if line.product_id:
    #             fposition_id = False
    #             fpos_obj = self.env['account.fiscal.position']
    #             fpos = fposition_id and fpos_obj.browse(cr, uid, fposition_id, context=context) or False
    #             product = line.product_id
    #             taxes = product.supplier_taxes_id
    #             #If taxes are not related to the product, maybe they are in the account
    #             if not taxes:
    #                 a = product.property_account_expense.id #Why is not there a check here?
    #                 if not a:
    #                     a = product.categ_id.property_account_expense_categ.id
    #                 a = fpos_obj.map_account(cr, uid, fpos, a)
    #                 taxes = a and self.env['account.account').browse(cr, uid, a, context=context).tax_ids or False
    #         if not taxes:
    #             continue
    #         tax_l = []
    #         base_tax_amount = line.total_amount
    #         #Calculating tax on the line and creating move?
    #         for tax in tax_obj.compute_all(cr, uid, taxes,
    #                 line.unit_amount ,
    #                 line.unit_quantity, line.product_id,
    #                 exp.user_id.partner_id)['taxes']:
    #             tax_code_id = tax['base_code_id']
    #             if not tax_code_id:
    #                 continue
    #             res[-1]['tax_code_id'] = tax_code_id
    #             ##
    #             is_price_include = tax_obj.read(cr,uid,tax['id'],['price_include'],context)['price_include']
    #             if is_price_include:
    #                 ## We need to deduce the price for the tax
    #                 res[-1]['price'] = res[-1]['price'] - tax['amount']
    #                 # tax amount countains base amount without the tax
    #                 base_tax_amount = (base_tax_amount - tax['amount']) * tax['base_sign']
    #             else:
    #                 base_tax_amount = base_tax_amount * tax['base_sign']
    #
    #             assoc_tax = {
    #                          'type':'tax',
    #                          'name':tax['name'],
    #                          'price_unit': tax['price_unit'],
    #                          'quantity': 1,
    #                          'price': tax['amount'] or 0.0,
    #                          'account_id': tax['account_collected_id'] or mres['account_id'],
    #                          'tax_code_id': tax['tax_code_id'],
    #                          'tax_amount': tax['amount'] * tax['base_sign'],
    #                          }
    #             tax_l.append(assoc_tax)
    #
    #         res[-1]['tax_amount'] = cur_obj.compute(cr, uid, exp.currency_id.id, company_currency, base_tax_amount, context={'date': exp.date_confirm})
    #         res += tax_l
    #     return res
    #
    # @api.model
    # def move_line_get_item(self, line):
    #     company = line.expense_id.company_id
    #     property_obj = self.env['ir.property')
    #     if line.product_id:
    #         acc = line.product_id.property_account_expense
    #         if not acc:
    #             acc = line.product_id.categ_id.property_account_expense_categ
    #         if not acc:
    #             raise osv.except_osv(_('Error!'), _('No purchase account found for the product %s (or for his category), please configure one.') % (line.product_id.name))
    #     else:
    #         acc = property_obj.get(cr, uid, 'property_account_expense_categ', 'product.category', context={'force_company': company.id})
    #         if not acc:
    #             raise osv.except_osv(_('Error!'), _('Please configure Default Expense account for Product purchase: `property_account_expense_categ`.'))
    #     return {
    #         'type':'src',
    #         'name': line.name.split('\n')[0][:64],
    #         'price_unit':line.unit_amount,
    #         'quantity':line.unit_quantity,
    #         'price':line.total_amount,
    #         'account_id':acc.id,
    #         'product_id':line.product_id.id,
    #         'uos_id':line.uom_id.id,
    #         'account_analytic_id':line.analytic_account.id,
    #     }
    #
    # @api.v7
    # def compute_expense_totals(self, cr, uid, exp, company_currency, ref, account_move_lines, context=None):
    #     '''
    #     internal method used for computation of total amount of an expense in the company currency and
    #     in the expense currency, given the account_move_lines that will be created. It also do some small
    #     transformations at these account_move_lines (for multi-currency purposes)
    #
    #     :param account_move_lines: list of dict
    #     :rtype: tuple of 3 elements (a, b ,c)
    #         a: total in company currency
    #         b: total in hr.expense currency
    #         c: account_move_lines potentially modified
    #     '''
    #     cur_obj = self.env['res.currency']
    #     context = dict(context or {}, date=exp.date_confirm or time.strftime('%Y-%m-%d'))
    #     total = 0.0
    #     total_currency = 0.0
    #     for i in account_move_lines:
    #         if exp.currency_id.id != company_currency:
    #             i['currency_id'] = exp.currency_id.id
    #             i['amount_currency'] = i['price']
    #             i['price'] = cur_obj.compute(cr, uid, exp.currency_id.id,
    #                     company_currency, i['price'],
    #                     context=context)
    #         else:
    #             i['amount_currency'] = False
    #             i['currency_id'] = False
    #         total -= i['price']
    #         total_currency -= i['amount_currency'] or i['price']
    #     return total, total_currency, account_move_lines
