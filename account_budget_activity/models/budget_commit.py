# -*- coding: utf-8 -*-
from openerp import fields, api, _
from openerp.exceptions import ValidationError


class CommitCommon(object):
    _CC = {  # Commit Common Dict
        'purchase.request': ('line_ids', 'purchase.request.line',
                             'purchase_request_id',
                             'purchase_request_line_id'),
        'purchase.order': ('order_line', 'purchase.order.line',
                           'purchase_id', 'purchase_line_id'),
        'hr.expense.expense': ('line_ids', 'hr.expense.line',
                               'expense_id', 'expense_line_id'),
        'sale.order': ('order_line', 'sale.order.line',
                       'sale_id', 'sale_line_id')}

    def _trans_id_domain(self):
        (obj_line, line_model, head_field, line_field) = self._CC[self._name]
        return [('source_model', '=', line_model),
                '|', ('active', '=', True), ('active', '=', False)]

    budget_commit_ids = fields.One2many(
        'account.analytic.line',  # inverse_name will be in each extension
        string='Budget Commitment',
        readonly=True,
    )
    budget_transition_ids = fields.One2many(
        'budget.transition',  # inverse_name will be in each extension
        string='Budget Transition',
        domain=_trans_id_domain,
        readonly=True,
    )
    technical_closed = fields.Boolean(
        string='Closed',
        readonly=True,
        default=False,
        copy=False,
        track_visibility='onchange',
        help="If checked, all committed budget will be released",
    )

    @api.multi
    def release_all_committed_budget(self):
        (obj_line, line_model, head_field, line_field) = self._CC[self._name]
        for rec in self:
            rec[obj_line].release_committed_budget()
            rec.budget_transition_ids.filtered('active').\
                write({'active': False})

    @api.multi
    def recreate_all_budget_commitment(self):
        """ This method is used for development only """
        (obj_line, line_model, head_field, line_field) = self._CC[self._name]
        for rec in self:
            rec.budget_commit_ids.unlink()
            rec[obj_line]._create_analytic_line(reverse=True)
            rec.budget_transition_ids.\
                filtered('active').filtered('forward').\
                return_budget_commitment([line_field])
            rec.budget_transition_ids.\
                filtered('active').filtered('backward').\
                regain_budget_commitment([line_field])

    @api.multi
    def action_technical_closed(self):
        for rec in self:
            rec.release_all_committed_budget()
            rec.write({'technical_closed': True})


class CommitLineCommon(object):
    _CLC = {
        'purchase.request.line': {
            'document_field': 'request_id',
            'journal_type': 'purchase',
            'line_field': 'purchase_request_line_id',
            'analytic_journal_field': 'pr_commitment_analytic_journal_id',
            'commit_account_field': 'pr_commitment_account_id',
            'qty_field': 'product_qty',
            'analytic_field': 'analytic_account_id',
            'product_uom': 'product_uom_id',
        },
        'purchase.order.line': {
            'document_field': 'order_id',
            'journal_type': 'purchase',
            'line_field': 'purchase_line_id',
            'analytic_journal_field': 'po_commitment_analytic_journal_id',
            'commit_account_field': 'po_commitment_account_id',
            'qty_field': 'product_qty',
            'analytic_field': 'account_analytic_id',
            'product_uom': 'product_uom',
        },
        'hr.expense.line': {
            'document_field': 'expense_id',
            'journal_type': 'purchase',
            'line_field': 'expense_line_id',
            'analytic_journal_field': 'exp_commitment_analytic_journal_id',
            'commit_account_field': 'exp_commitment_account_id',
            'qty_field': 'unit_quantity',
            'analytic_field': 'analytic_account',
            'product_uom': 'uom_id',
        },
        'sale.order.line': {
            'document_field': 'order_id',
            'journal_type': 'sale',
            'line_field': 'sale_line_id',
            'analytic_journal_field': 'so_commitment_analytic_journal_id',
            'commit_account_field': 'so_commitment_account_id',
            'qty_field': 'product_uos_qty',
            'analytic_field': 'account_analytic_id',
            'product_uom': 'product_uom',
        },
    }

    def _trans_id_domain(self):
        return [('source_model', '=', self._name),
                '|', ('active', '=', True), ('active', '=', False)]

    budget_commit_ids = fields.One2many(
        'account.analytic.line',
        string='Budget Commitment',
        readonly=True,
    )
    budget_commit_bal = fields.Float(
        string='Budget Balance',
        compute='_compute_budget_commit_bal',
    )
    budget_transition_ids = fields.One2many(
        'budget.transition',
        string='Budget Transition',
        domain=_trans_id_domain,
        readonly=True,
    )
    has_commit_amount = fields.Boolean(
        string='Commitment > 0.0',
        compute='_compute_has_commit_amount',
        store=True,
    )
    commit_amount = fields.Float(
        string='Commitment',
        compute='_compute_has_commit_amount',
        store=True,
    )

    @api.multi
    @api.depends('budget_commit_ids')
    def _compute_has_commit_amount(self):
        for rec in self:
            commit_amount = sum(rec.budget_commit_ids.mapped('amount'))
            rec.commit_amount = commit_amount
            if commit_amount:
                rec.has_commit_amount = True
            else:
                rec.has_commit_amount = False

    @api.multi
    def _write(self, vals):
        if 'has_commit_amount' in vals:
            self.mapped('budget_commit_ids').write({
                'has_commit_amount': vals['has_commit_amount']})
        return super(CommitLineCommon, self)._write(vals)

    @api.multi
    def _compute_budget_commit_bal(self):
        for rec in self:
            rec.budget_commit_bal = sum(rec.budget_commit_ids.mapped('amount'))

    @api.multi
    def release_committed_budget(self):
        params = self._CLC[self._name]
        line_field = params['line_field']
        Analytic = self.env['account.analytic.line']
        for rec in self:
            aline = Analytic.search([(line_field, '=', rec.id)],
                                    order='create_date desc', limit=1)
            if aline and rec.budget_commit_bal:
                aline.copy({'amount': -rec.budget_commit_bal})

    @api.model
    def _price_subtotal(self, line_qty):
        raise ValidationError(_('_price_subtotal not implemented!'))

    @api.multi
    def _prepare_analytic_line(self, reverse=False, currency=False):
        self.ensure_one()

        params = self._CLC[self._name]
        document_field = params['document_field']
        journal_type = params['journal_type']
        line_field = params['line_field']
        analytic_journal_field = params['analytic_journal_field']
        account_field = params['commit_account_field']
        qty_field = params['qty_field']
        analytic_field = params['analytic_field']
        product_uom = params['product_uom']

        # general_account_id = self._get_account_id_from_po_line()
        company = self.env.user.company_id
        general_journal = self.env['account.journal'].search(
            [('type', '=', journal_type), ('company_id', '=', company.id)],
            limit=1)
        if not general_journal:
            raise Warning(
                _('Define an accounting journal for %s') % journal_type)
        if not general_journal.is_budget_commit:
            return False

        analytic_journal = general_journal[analytic_journal_field]
        general_account = general_journal[account_field]

        if not analytic_journal or not general_account:
            raise ValidationError(
                _("No analytic journal for commitments defined on the "
                  "accounting journal '%s'") % general_journal.name)

        # Pre check, is eligible line
        Budget = self.env['account.budget']
        if not Budget.budget_eligible_line(analytic_journal, self):
            return False

        line_qty = False
        line_amount = False
        if 'diff_qty' in self._context:
            line_qty = self._context.get('diff_qty')
        elif 'diff_amount' in self._context:
            line_amount = self._context.get('diff_amount')
        else:
            line_qty = self[qty_field]
        if not line_qty and not line_amount:
            return False
        price_subtotal = line_amount or self._price_subtotal(line_qty)

        sign = reverse and -1 or 1
        company_currency = company.currency_id
        currency = currency or company_currency

        return {
            'name': 'name' in self and self.name or False,
            'product_id': ('product_id' in self and
                           self.product_id.id or False),
            'account_id': self[analytic_field].id,
            'unit_amount': line_qty,
            'product_uom_id': self[product_uom].id,
            'amount': currency.compute(sign * price_subtotal,
                                       company_currency),
            'general_account_id': general_account.id,
            'journal_id': analytic_journal.id,
            'ref': self[document_field].name,
            'user_id': self._uid,
            # LINE
            line_field: self.id,
            # Fiscal
            'fiscalyear_id': ('fiscalyear_id' in self and
                              self.fiscalyear_id.id or False),
        }

    @api.multi
    def _create_analytic_line(self, reverse=False):
        if self._context.get('no_create_analytic_line', False):
            return

        params = self._CLC[self._name]

        document_field = params['document_field']
        for rec in self:
            # For SO/PO only, not for quoatation
            if 'order_type' in rec[document_field] and \
                    rec[document_field].order_type == 'quotation':
                continue
            vals = rec._prepare_analytic_line(
                reverse=reverse, currency=rec[document_field].currency_id)
            if vals:
                self.env['account.analytic.line'].sudo().create(vals)
