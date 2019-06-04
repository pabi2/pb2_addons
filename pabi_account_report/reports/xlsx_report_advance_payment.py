# -*- coding: utf-8 -*-
from openerp import models, fields, api



class XLSXReportAdvancePaymentView(models.AbstractModel):
    _name = 'xlsx.report.advance.payment.view'
    _inherit = 'account.move.line'

    move_line_id = fields.Many2one(
        'account.move.line',
        string='Move Line',
    )
    operating_unit = fields.Many2one(
        'operating.unit',
        string='Org',
    )


class XLSXReportAdvancePayment(models.TransientModel):
    _name = 'xlsx.report.advance.payment'
    _inherit = 'report.account.common'

    filter = fields.Selection(
        readonly=True,
        default='filter_date',
    )
    date_report = fields.Date(
        string='As of Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
    )
    account_ids = fields.Many2many(
        'account.account',
        string='Accounts',
        domain=lambda self: self._get_domain_account_ids(),
    )
    results = fields.Many2many(
        'xlsx.report.advance.payment.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.model
    def _get_account_ids(self):
        ids = []
        for res in self.env.user.company_id.other_deposit_account_ids:
            if res.code != '1106010007' : ids += [res.id]
        return ids

    @api.model
    def _get_domain_account_ids(self):
        return [('id', 'in', self._get_account_ids())]

    @api.multi
    def _compute_results(self):
        """
        Solution
        1. Get from account.move.line
        2. Check account code from Other Advance Accounts in PABI Apps
           (Settings > Configuration > PABI Apps)
        3. Check invoice to advance
        4. Check reconcile is False
        """
        self.ensure_one()
        Result = self.env["account.move.line"]
        dom = [('reconcile_id', '=', False)]
               #('invoice', '!=', False),]
        if self.account_ids:
            dom += [('account_id', 'in', self.account_ids.ids)]
        elif not self.account_ids:
            dom += [('account_id', 'in', self._get_account_ids())]
            
        #self.results = Result.search(dom).sorted(key=lambda l: (l.invoice.operating_unit_id.name, l.partner_id.search_key,))
        res_ids = Result.search(dom)
        res_ids = str(tuple(res_ids.ids))
        self._cr.execute("""
            select mol.id as move_line_id, mol.name as name,
            mol.date as date, mol.date_maturity as date_maturity,
            mol.move_id as move_id, mol.partner_id as partner_id,
            mol.reconcile_id as reconcile_id, mol.currency_id as currency_id,
            mol.period_id as period_id, mol.account_id as account_id,
            mol.document as document, mol.document_id as document_id
            from account_move_line mol
            left join account_move mov on mov.id = mol.move_id
            left join res_partner part on part.id = mol.partner_id
            left join account_move_reconcile mov_rec on mov_rec.id = mol.reconcile_id
            left join account_account acc on acc.id = mol.account_id
            left join res_currency cur on cur.id = mol.currency_id
            where mol.id in """+(res_ids)+"""
            order by acc.code, part.search_key
        """)

        results = self._cr.dictfetchall()
        ReportLine = self.env['xlsx.report.advance.payment.view']
        res = []
        for line in results:
            mol = self.env["account.move.line"].browse(line['move_line_id'])
            mov = self.env["account.move"].browse(line['move_id'])
            
            line['operating_unit'] = mol.invoice.operating_unit_id.id or mol.org_id.operating_unit_id.id or False
            res += [line]   
        res = sorted(res, key=lambda k: (k['account_id'], k['operating_unit']))
        
        for line in res:
            self.results += ReportLine.new(line)
        
        return True


  