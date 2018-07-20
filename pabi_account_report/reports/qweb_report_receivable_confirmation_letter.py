# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.addons.l10n_th_amount_text.amount_to_text_th \
    import amount_to_text_th


class ReceivableConfirmationLetterDetail(models.TransientModel):
    _name = 'receivable.confirmation.letter.detail'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    balance = fields.Float(
        string='Balance',
    )
    parent_accounts = fields.Char(
        string='Parent Accounts',
    )
    balance_text_th = fields.Char(
        string='Balance (TH)',
    )
    wizard_id = fields.Many2one(
        'qweb.report.receivable.confirmation.letter',
        string='Receivable Confirmation Letter Wizard',
    )


class QwebReportReceivableConfirmationLetter(models.TransientModel):
    _name = 'qweb.report.receivable.confirmation.letter'
    _inherit = 'report.account.common'

    filter = fields.Selection(
        readonly=True,
        default='filter_date',
    )
    date_report = fields.Date(
        string='Report Date',
        required=True,
        default=lambda self: fields.Date.context_today(self),
    )
    account_ids = fields.Many2many(
        'account.account',
        'receivable_confirmation_letter_account_rel',
        'report_id', 'account_id',
        string='Accounts',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        'receivable_confirmation_letter_partner_rel',
        'report_id', 'partner_id',
        string='Partners',
    )
    trading_account_receivable = fields.Char(
        string='Trading A/C Receivable',
        readonly=True,
    )
    other_account_receivable = fields.Char(
        string='Other A/C Receivable',
        readonly=True,
    )
    results = fields.One2many(
        'receivable.confirmation.letter.detail',
        'wizard_id',
        string='Results',
    )

    @api.multi
    def _get_execute_datas(self):
        account_ids = self.account_ids.ids
        partner_ids = self.partner_ids.ids
        date_report = self.date_report
        condition = "a.type = 'receivable'"
        if account_ids:
            account_ids += [0]
            condition += " AND a.id IN %s" % (str(tuple(account_ids)))
        if partner_ids:
            partner_ids += [0]
            condition += " AND l.partner_id IN %s" % (str(tuple(partner_ids)))
        if date_report:
            condition += " AND l.date_created <= '%s' \
                          AND (l.reconcile_id IS NULL OR \
                          l.date_reconciled > '%s')" \
                          % (date_report, date_report)
        self._cr.execute("""
            SELECT l.partner_id, pa.code, l.credit, l.debit
            FROM account_move_line l
            LEFT JOIN account_account a ON l.account_id = a.id
            LEFT JOIN account_account pa ON a.parent_id = pa.id
            WHERE %s""" % (condition, ))
        return self._cr.fetchall()

    @api.multi
    def _prepare_confirmation_letter_detail(self, datas):
        lines = []
        for partner_id in list(set(map(lambda l: l[0], datas))):
            sub_data = filter(lambda l: l[0] == partner_id, datas)
            pr_accounts = ",".join(list(set(map(lambda l: l[1], sub_data))))
            credit = sum(map(lambda l: l[2], sub_data))
            debit = sum(map(lambda l: l[3], sub_data))
            balance = debit - credit
            balance_text_th = \
                (balance < 0 and 'ลบ' or '') + \
                amount_to_text_th(abs(balance), 'THB')
            lines.append((0, 0, {
                'partner_id': partner_id,
                'balance': balance,
                'parent_accounts': pr_accounts,
                'balance_text_th': balance_text_th
            }))
        return lines

    @api.multi
    def _create_receivable_confirmation_letter_detail(self):
        # Get exceute datas
        datas = self._get_execute_datas()

        # Prepare receivable confirmation letter detail
        lines = self._prepare_confirmation_letter_detail(datas)

        # Write data
        self.write({'results': lines})
        return True

    @api.multi
    def run_report(self):
        # Create Receivable Confirmation Letter Detail
        self._create_receivable_confirmation_letter_detail()

        # --
        report_name = 'pabi_account_report' + \
                      '.report_receivable_confirmation_letter'
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': {
                'ids': self.results.ids,
                'model': 'receivable.confirmation.letter.detail',
                'form': self.read()[0],
                'context': self._context.copy()
            }
        }
