# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountAnalyticJournal(models.Model):
    _inherit = 'account.analytic.journal'

    budget_commit_type = fields.Selection(
        [('so_commit', 'SO Commitment'),
         ('pr_commit', 'PR Commitment'),
         ('po_commit', 'PO Commitment'),
         ('exp_commit', 'Expense Commitment'),
         ('actual', 'Actual'),
         ],
        string='Budget Commit Type',
    )
    budget_method = fields.Selection(
        [('revenue', 'Revenue'),
         ('expense', 'Expense')],
        string='Budget Method',
    )

    def init(self, cr):
        # update budget_commit_type for account.exp, as it was noupdate=True
        cr.execute("""
            update account_analytic_journal
            set budget_commit_type = 'actual'
            where id in (select res_id from ir_model_data
                where module = 'account'
                and name in ('exp', 'analytic_journal_sale'))
        """)
        # Update budget_method = Reveue
        cr.execute("""
            update account_analytic_journal
            set budget_method = 'revenue'
            where id = (select res_id from ir_model_data
                where module = 'account'
                and name = 'analytic_journal_sale')
        """)
        # Update budget_method = Expense
        cr.execute("""
            update account_analytic_journal
            set budget_method = 'expense'
            where id = (select res_id from ir_model_data
                where module = 'account'
                and name = 'exp')
        """)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    # We don't need, as it can be found from analytic.account.journal
    # budget_method = fields.Selection(
    #     [('revenue', 'Revenue'),
    #      ('expense', 'Expense')],
    #     string='Budget Method',
    #     required=True,
    # )
    charge_type = fields.Selection(  # Prepare for pabi_internal_charge
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
        required=True,
        default='external',
        help="Specify whether the move line is for Internal Charge or "
        "External Charge. Only expense internal charge to be set as internal",
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        readonly=True,
        index=True,
    )
    monitor_fy_id = fields.Many2one(
        'account.fiscalyear',
        string='Monitoring FY',
        readonly=True,
        index=True,
        help="Special fiscal year column, used to carry forward "
        "commitment from past year to current budget year.\n"
        "At beginning of new fiscal year, an action to carry over commitment "
        "can be triggered."
    )
    has_commit_amount = fields.Boolean(
        string='Commitment > 0.0',
        default=False,
        readonly=True,
        help="True if parent document (PR/PO/EX/SO) as uncleared commitment"
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
    )
    # Don't need as we move to new module
    # doc_id = fields.Reference(
    #     [('purchase.request', 'Purchase Request'),
    #      ('purchase.order', 'Purchase Order'),
    #      ('hr.expense.expense', 'Expense'),
    #      ('account.invoice', 'Invoice')],
    #     string='Doc Ref',
    #     readonly=True,
    # )
    # doc_ref = fields.Char(
    #     string='Doc Ref',
    #     readonly=True,
    # )
    # ---------- PR ---------------
    purchase_request_id = fields.Many2one(
        'purchase.request',
        string='Purchase Request',
        related='purchase_request_line_id.request_id',
        store=True,
        help="PR Commitment",
    )
    purchase_request_line_id = fields.Many2one(
        'purchase.request.line',
        string='Purchase Request Line',
        ondelete='cascade',
        readonly=True,
        help="PR Commitment",
    )
    # ---------- PO ---------------
    purchase_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        related='purchase_line_id.order_id',
        store=True,
        help="PO Commitment",
    )
    purchase_line_id = fields.Many2one(
        'purchase.order.line',
        string='Purchase Order Line',
        ondelete='cascade',
        readonly=True,
        help="PO Commitment",
    )
    # ---------- SO ---------------
    sale_id = fields.Many2one(
        'sale.order',
        string='Sales Order',
        related='sale_line_id.order_id',
        store=True,
        help="SO Commitment",
    )
    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Sales Order Line',
        ondelete='cascade',
        readonly=True,
        help="SO Commitment",
    )
    # ---------- Expense ---------------
    expense_id = fields.Many2one(
        'hr.expense.expense',
        string='Expense',
        related='expense_line_id.expense_id',
        store=True,
        help="Expense Commitment",
    )
    expense_line_id = fields.Many2one(
        'hr.expense.line',
        string='Expense Line',
        ondelete='cascade',
        readonly=True,
        help="Expense Commitment",
    )
    # ----------------------------------
    period_id = fields.Many2one(
        'account.period',
        string="Period",
    )
    quarter = fields.Selection(
        [('Q1', 'Q1'),
         ('Q2', 'Q2'),
         ('Q3', 'Q3'),
         ('Q4', 'Q4'),
         ],
        string="Quarter",
        compute="_compute_quarter",
        store=True,
    )

    @api.depends('period_id')
    def _compute_quarter(self):
        for line in self:
            period = line.period_id
            periods = self.env['account.period'].search(
                [('fiscalyear_id', '=', period.fiscalyear_id.id),
                 ('special', '=', False)],
                order="date_start").ids
            period_index = periods.index(period.id)
            if period_index in (0, 1, 2):
                line.quarter = 'Q1'
            elif period_index in (3, 4, 5):
                line.quarter = 'Q2'
            elif period_index in (6, 7, 8):
                line.quarter = 'Q3'
            elif period_index in (9, 10, 11):
                line.quarter = 'Q4'

    @api.multi
    @api.constrains('date', 'fiscalyear_id')
    def _check_compute_fiscalyear_id(self):
        FiscalYear = self.env['account.fiscalyear']
        for rec in self:
            fiscalyear_id = FiscalYear.find(rec.date)  # date of analytic.line
            if not rec.fiscalyear_id:  # No fiscal assigned, use rec.date
                rec._write({'fiscalyear_id': fiscalyear_id,
                            'monitor_fy_id': fiscalyear_id, })
            else:  # Has fiscalyear_id but year prior to analytic date
                fiscal = FiscalYear.browse(fiscalyear_id)
                if fiscal.date_start > rec.fiscalyear_id.date_start:
                    rec._write({'monitor_fy_id': fiscal.id, })
                else:
                    rec._write({'monitor_fy_id': rec.fiscalyear_id.id, })

    @api.multi
    def _check_analytic_asset_line(self):
        MOVE = self.env['account.move']#
        ASSET_line = self.env['account.asset.line']
        #moves = MOVE.browse(self.move_id and self.move_id.id)
        if self.move_id:
            depreciation_lines = ASSET_line.search([('move_id','=',self.move_id.id),('asset_id','!=',False)])
            if depreciation_lines:
                self.section_id = depreciation_lines[0].asset_id.owner_section_id and\
                                    depreciation_lines[0].asset_id.owner_section_id.id or False
                self.project_id = depreciation_lines[0].asset_id.owner_project_id and\
                                    depreciation_lines[0].asset_id.owner_project_id.id or False
                self.invest_asset_id = depreciation_lines[0].asset_id.owner_invest_asset_id and\
                                        depreciation_lines[0].asset_id.owner_invest_asset_id.id or False
                self.invest_construction_phase_id = depreciation_lines[0].asset_id.owner_invest_construction_phase_id and\
                                                        depreciation_lines[0].asset_id.owner_invest_construction_phase_id.id or False
                chartfield_id = self.section_id or\
                                self.project_id or\
                                self.invest_asset_id or\
                                self.invest_construction_phase_id or False
                self.costcenter_id = chartfield_id and\
                                        chartfield_id.costcenter_id and\
                                        chartfield_id.costcenter_id.id or False

    @api.model
    def create(self, vals):
        _logger.info("------- create analytic line -------")
        """ Add posting dimension """
        if vals.get('account_id', False):
            Analytic = self.env['account.analytic.account']
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
        _logger.info("vals: %s", str(vals))
        analytic_line = super(AccountAnalyticLine, self).create(vals)
        _logger.info("analytic_line: %s", str(analytic_line))
        analytic_line._check_analytic_asset_line()
        return analytic_line

    @api.multi
    def write(self, vals):
        for rec in self:
            # Prepare period_id for reporting purposes
            if vals.get('date', rec.date):
                date = vals.get('date', rec.date)
                periods = self.env['account.period'].find(date)
                period = periods and periods[0] or False
                vals.update({'period_id': period.id})
            # --
        return super(AccountAnalyticLine, self).write(vals)


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    # ************************ Start ********************************
    # Following code was used initially. But I want to experiment
    # not using it. In PABI2, we may not need them.
    # type = fields.Selection(
    #     [('view', 'Analytic View'),
    #      ('normal', 'Analytic Account'),
    #      ('pr_product', 'PR Product'),
    #      ('product', 'Product'),
    #      ('activity', 'Activity'),
    #      ('contract', 'Contract or Project'),
    #      ('template', 'Template of Contract')]
    # )
    # ************************** End ********************************
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        ondelete='restrict',
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        ondelete='restrict',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        ondelete='restrict',
    )

    @api.model
    def update_dict_by_analytic(self, update_dict):
        """ Given analytic_id, return dict with udpated dimension """
        for d in self._analytic_dimensions():
            update_dict.update({d: self[d].id})

    @api.model
    def _analytic_dimensions(self):
        dimensions = [
            'product_id',
            'activity_id',
            'activity_group_id',
        ]
        return dimensions

    @api.multi
    def _check_analytic_asset_line(self, vals):
        MOVE = self.env['account.move']
        ASSET = self.env['account.asset']
        ASSET_line = self.env['account.asset.line']
        asset_id = False
        # moves = MOVE.browse(self.move_id and self.move_id.id)
        if 'asset_id' in vals:
            asset_id = ASSET.browse(vals['asset_id'])
        if self.line_ids and self.line_ids.sorted()[0].move_id \
                and self.line_ids.sorted()[0].move_id.move_id:
            asset_id = ASSET_line.search([
                ('move_id', '=', self.line_ids.sorted()[0].move_id.move_id.id),
                ('asset_id', '!=', False)
            ], limit=1).asset_id
        # if not self.line_ids:
        #     asset_id = ASSET.search([
        #         ('account_analytic_id', '=', self.id),
        #         ('active', '=', True)
        #     ], limit=1)

        if asset_id:
            if asset_id.owner_section_id:
                self.write({
                            'section_id': asset_id.owner_section_id.id,
                            'project_id': False,
                            'invest_asset_id': False,
                            'invest_construction_phase_id': False,
                            'costcenter_id':
                            asset_id.owner_section_id.costcenter_id.id,
                    })
            elif asset_id.owner_project_id:
                self.write({
                            'section_id': False,
                            'project_id': asset_id.owner_project_id.id,
                            'invest_asset_id': False,
                            'invest_construction_phase_id': False,
                            'costcenter_id': asset_id.owner_project_id.costcenter_id.id,
                    })
            elif asset_id.owner_invest_asset_id:
                self.write({
                            'section_id': False,
                            'project_id': False,
                            'invest_asset_id': asset_id.owner_invest_asset_id.id,
                            'invest_construction_phase_id': False,
                            'costcenter_id': asset_id.owner_invest_asset_id.costcenter_id.id,
                    })
            elif asset_id.owner_invest_construction_phase_id:
                self.write({
                            'section_id': False,
                            'project_id': False,
                            'invest_asset_id': False,
                            'invest_construction_phase_id': asset_id.owner_invest_construction_phase_id.id,
                            'costcenter_id': asset_id.owner_invest_construction_phase_id.costcenter_id.id,
                    })

    @api.model
    def get_analytic_search_domain(self, rec):
        dimensions = self._analytic_dimensions()
        #rec._check_analytic_asset_line()
        domain = []
        for dimension in dimensions:
            if dimension in rec._fields:
                domain.append((dimension, '=', rec[dimension].id))
        return domain

    @api.model
    def get_matched_analytic(self, rec):
        domain = self.get_analytic_search_domain(rec)
        # ************************ Start ********************************
        # Following code was used initially. But I want to experiment
        # not using it. In PABI2, we may not need them.
        #
        # if rec._name == 'account.model.line':  # From Recurring Models
        #     domain.append(('type', '=', 'normal'))
        # if rec.product_id:
        #     domain.append(('type', '=', 'product'))
        # elif rec.activity_id:
        #     domain.append(('type', '=', 'activity'))
        # else:  # Last possible type, from Purchase Request
        #     domain.append(('type', '=', 'pr_product'))
        #
        domain.append(('type', '=', 'normal'))
        # ************************ Start ********************************
        analytics = self.env['account.analytic.account'].search(domain)
        if analytics:
            return analytics[0]
        return False

    @api.model
    def _invalid_domain(self, domain):
        # If all domain valus is false, it is invalid
        res = list(set([x[2] is False for x in domain]))
        if len(res) == 1 and res[0] is True:
            return True
        return False

    @api.model
    def create_matched_analytic(self, rec):
        # Not allow product and activity at the same time.
        if ('product_id' in rec._fields) and ('activity_id' in rec._fields):
            if rec.product_id and rec.activity_id:
                raise ValidationError(_('Select both Product and '
                                        'Activity is prohibited'))
        # Only create analytic if not exists yet
        Analytic = self.env['account.analytic.account'].sudo()
        domain = self.get_analytic_search_domain(rec)
        # If not a valid domain, return False (domain with no values)
        if self._invalid_domain(domain):
            return False
        # ************************ Start ********************************
        # Following code was used initially. But I want to experiment
        # not using it. In PABI2, we may not need them.
        #
        # if rec._name == 'account.model.line':  # from Recurring Entry
        #     domain.append(('type', '=', 'normal'))
        # elif rec.product_id:
        #     domain.append(('type', '=', 'product'))
        # elif rec.activity_id:
        #     domain.append(('type', '=', 'activity'))
        # else:
        #     domain.append(('type', '=', 'pr_product'))
        domain.append(('type', '=', 'normal'))  # remove this line if use above
        #
        # *************************** End *******************************
        analytics = Analytic.search(domain)
        if not analytics:
            vals = dict((x[0], x[2]) for x in domain)
            vals['name'] = (rec.product_id.name or
                            rec.activity_id.name or
                            ('name' in rec and rec.name) or
                            ('product_name' in rec and rec.product_name) or
                            ('note' in rec and rec.note) or
                            False)
            if not vals['name']:
                raise ValidationError(
                    _('No valid name for creating Analytic Account'))
            # ************************ Start ********************************
            # Following code was used initially. But I want to experiment
            # not using it. In PABI2, we may not need them.
            #
            # vals['type'] = \
            #     ((rec._name == 'account.model.line' and 'normal') or
            #      (rec.product_id and 'product') or
            #      (rec.activity_id and 'activity') or
            #      'pr_product')
            #
            vals['type'] = 'normal'
            if ('doctype' in rec._fields) and \
                (rec.doctype == 'adjustment' and \
                rec._name == 'account.move.line'):

                vals.update({'move_id':rec.move_id.id}) #update move_id to find doctype in analytic
            #
            # *************************** End *******************************
            _logger.info("vals...: %s", str(vals))
            return Analytic.create(vals)
        else:
            _logger.info("exist analytic: %s", str(analytics[0]))
            return analytics[0]
