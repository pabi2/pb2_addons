# -*- coding: utf-8 -*-
from openerp import models, fields, api
import time
import logging

_logger = logging.getLogger(__name__)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.model
    def create(self, vals):
        """
        pabi_direct_sql.analytic_create = True
        ======================================
        This should be the top most method which will not call any super(),
        as such, it must include all of the following logic here!!!
        - All logic of [account.analytic.line].create()
        - 4 ORM fileds, _prepare_orm_defaults
        - Defaults, _prepare_defaults
        - Related fields, _prepare_related_values
        - Compute fields (with store=True)
        - Constraints (that update fields)
        """
        key = 'pabi_direct_sql.analytic_create'
        config_obj = self.env['ir.config_parameter']
        if str(config_obj.get_param(key)).lower() == 'true':
            begin = time.time()
            _logger.info("------- Direct SQL, create analytic line -------")
            # Main preparation
            self._prepare_orm_create(vals)
            self._prepare_orm_defaults(vals)
            self._prepare_defaults(vals)
            self._prepare_related_values(vals)
            # Computed fields functions
            self._prepare_compute_quarter(vals)
            # Special constraints methods
            self._prepare_check_compute_fiscalyear_id(vals)
            self._prepare_compute_document(vals)
            # Do SQL Insert
            _logger.info("vals: %s", str(vals))
            keys = [key for key, value in vals.items() if value]
            values = [value for key, value in vals.items() if value]
            sql = "insert into %s (%s) values (%s) returning id" % (
                self._table, ', '.join(keys),
                ', '.join(['%s' for x in range(len(keys))])
            )
            self._cr.execute(sql, tuple(values))
            analytic_line = self.sudo().browse(self._cr.fetchone()[0])
            diff = time.time() - begin
            _logger.info("analytic_line: %s, %s", str(analytic_line), diff)
            return analytic_line
        else:
            return super(AccountAnalyticLine, self).create(vals)

    @api.model
    def _prepare_orm_create(self, vals):
        # From account_budget_activity.models.analytic.create()
        if vals.get('account_id', False):
            Analytic = self.env['account.analytic.account'].sudo()
            analytic = Analytic.browse(vals['account_id'])
            if not analytic:
                analytic = Analytic.create_matched_analytic(self)
            if analytic:
                domain = Analytic.get_analytic_search_domain(analytic)
                vals.update(dict((x[0], x[2]) for x in domain))
        # Prepare period_id for reporting purposes
        date = vals.get('date', fields.Date.context_today(self))
        if date:
            periods = self.env['account.period'].find(date)
            period = periods and periods[0] or False
            vals.update({'period_id': period.id})

    @api.model
    def _prepare_orm_defaults(self, vals):
        today = vals.get('write_date', fields.Date.context_today(self))
        vals['write_uid'] = vals.get('write_uid', self.env.user.id)
        vals['write_date'] = vals.get('write_date', today)
        vals['create_uid'] = vals.get('create_uid', self.env.user.id)
        vals['create_date'] = vals.get('write_date', today)

    @api.model
    def _prepare_defaults(self, vals):
        vals['charge_type'] = vals.get('charge_type', 'external')
        vals['date'] = vals.get('date', fields.Date.context_today(self))
        vals['amount'] = vals.get('amount', 0.0)
        company = self.env['res.company'].\
            _company_default_get('account.analytic.line')
        vals['company_id'] = vals.get('company_id', company)
        vals['has_commit_amount'] = vals.get('has_commit_amount', False)

    @api.model
    def _prepare_related_values(self, vals):
        """ <related field>: (<source field>, <target field>, <table name>)
        """
        related = {
            # From account.account_analytic_line.py
            'currency_id': ('move_id', 'currency_id', 'account_move_line'),
            'amount_currency': ('move_id', 'amount_currency',
                                'account_move_line'),
            # From account_budget_activity.models.analytic.py
            'purchase_request_id': ('purchase_request_line_id', 'request_id',
                                    'purchase_request_line'),
            'purchase_id': ('purchase_line_id', 'order_id',
                            'purchase_order_line'),
            'sale_id': ('sale_line_id', 'order_id', 'sale_order_line'),
            'expense_id': ('expense_line_id', 'expense_id', 'hr_expense_line'),

        }
        for k, v in related.items():
            if vals.get(v[0]):
                sql = 'select %s from %s where id = %s' % (v[1], v[2], '%s')
                self._cr.execute(sql, (vals[v[0]], ))
                vals[k] = self._cr.fetchone()[0]

    @api.model
    def _prepare_check_compute_fiscalyear_id(self, vals):
        # From account_budget_activity.models.analytic.py
        # MUST be exact same logic as _check_compute_fiscalyear_id() !!
        Fiscal = self.env['account.fiscalyear'].sudo()
        fiscalyear_id = Fiscal.find(vals['date'])  # date of analytic.line
        if not vals.get('fiscalyear_id'):  # No fiscal assigned, use rec.date
            vals['fiscalyear_id'] = fiscalyear_id
            vals['monitor_fy_id'] = fiscalyear_id
        else:  # Has fiscalyear_id but year prior to analytic date
            fiscal = Fiscal.browse(fiscalyear_id)
            rec_fiscal = Fiscal.browse(vals['fiscalyear_id'])
            if fiscal.date_start > rec_fiscal.date_start:
                vals['monitor_fy_id'] = fiscal.id
            else:
                vals['monitor_fy_id'] = rec_fiscal.id

    @api.model
    def _prepare_compute_quarter(self, vals):
        # From account_budget_activity.models.analytic.py
        # MUST be exact same logic as _compute_quarter() !!
        Period = self.env['account.period'].sudo()
        period = Period.browse(vals['period_id'])
        periods = Period.search([
            ('fiscalyear_id', '=', period.fiscalyear_id.id),
            ('special', '=', False)], order="date_start").ids
        period_index = periods.index(period.id)
        if period_index in (0, 1, 2):
            vals['quarter'] = 'Q1'
        elif period_index in (3, 4, 5):
            vals['quarter'] = 'Q2'
        elif period_index in (6, 7, 8):
            vals['quarter'] = 'Q3'
        elif period_index in (9, 10, 11):
            vals['quarter'] = 'Q4'

    @api.model
    def _prepare_compute_document(self, vals):
        # From pabi_account_move_document_ref.models.account_analytic_line.py
        # MUST be exact same logic as _compute_document()
        if vals.get('move_id'):  # move_id is account_move_line
            Move = self.env['account.move'].sudo()
            move = Move.browse(vals['move_id'])
            document = move.document_id
            if document:
                if document._name in ('stock.picking',
                                      'account.bank.receipt'):
                    vals['document'] = document.name
                elif document._name == 'account.invoice':
                    vals['document'] = document.internal_number
                else:
                    vals['document'] = document.number
            vals['document_line'] = vals['name']
            vals['document_id'] = document.id
            vals['doctype'] = move.doctype
        if vals.get('expense_id'):
            ExpenseLine = self.env['hr.expense.line'].sudo()
            expense_line = ExpenseLine.browse(vals['expense_line_id'])
            vals['document'] = expense_line.expense_id.number
            vals['document_line'] = expense_line.name
            vals['document_id'] = \
                '%s,%s' % ('hr.expense.expense', expense_line.expense_id.id)
            vals['doctype'] = 'employee_expense'
        elif vals.get('purchase_request_id'):
            RequestLine = self.env['purchase.request.line'].sudo()
            request_line = RequestLine.browse(vals['purchase_request_line_id'])
            vals['document'] = request_line.request_id.name
            vals['document_line'] = request_line.name
            vals['document_id'] = \
                '%s,%s' % ('purchase.request', request_line.request_id.id)
            vals['doctype'] = 'purchase_request'
        elif vals.get('purchase_id'):
            POLine = self.env['purchase.order.line'].sudo()
            purchase_line = POLine.browse(vals['purchase_line_id'])
            vals['document'] = purchase_line.order_id.name
            vals['document_line'] = purchase_line.name
            vals['document_id'] = \
                '%s,%s' % ('purchase.order', purchase_line.order_id.id)
            vals['doctype'] = 'purchase_order'
        elif vals.get('sale_id'):
            SOLine = self.env['sale.order.line'].sudo()
            sale_line = SOLine.browse(vals['sale_line_id'])
            vals['document'] = sale_line.order_id.name
            vals['document_line'] = sale_line.name
            vals['document_id'] = \
                '%s,%s' % ('sale.order', sale_line.order_id.id)
            vals['doctype'] = 'sale_order'
