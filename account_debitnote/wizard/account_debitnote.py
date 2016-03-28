# -*- coding: utf-8 -*-
import time

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class AccountDebitNote(models.Model):
    _name = "account.debitnote"
    _description = "Invoice Debit Note"

    @api.model
    def default_journal(self):
        obj_journal = self.env['account.journal']
        inv_type = self.env.context.get('type', 'out_invoice')
        company_id = self.env.user.company_id.id
        type = (inv_type == 'out_invoice') and 'sale_debitnote' or \
               (inv_type == 'in_invoice') and 'purchase_debitnote'
        journal = obj_journal.search([('type', '=', type),
                                     ('company_id', '=', company_id)],
                                     limit=1).ids
        return journal and journal[0] or False

    date = fields.Date(
        string='Date',
        default=time.strftime('%Y-%m-%d'),
        help=''' This date will be used as the invoice date
        for debit note and period will be chosen accordingly!'''
        )
    period = fields.Many2one('account.period', 'Force period')
    journal_id = fields.Many2one(
        'account.journal',
        string='Debit Journal',
        default=default_journal,
        help=''' You can select here the journal to use
        for the debit note that will be created.
        If you leave that field empty,
        it will use the same journal as the current invoice.''')
    description = fields.Char('Reason', size=128, required=True)

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        journal_obj = self.env['account.journal']

        res = super(AccountDebitNote, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu
            )
        type = self.env.context.get('type', 'out_invoice')
        company_id = self.env.user.company_id.id
        journal_type = (type == 'out_invoice') and 'sale_debitnote' or \
                       (type == 'in_invoice') and 'purchase_debitnote'
        for field in res['fields']:
            if field == 'journal_id':
                journal_select = journal_obj._name_search(
                    '', [('type', '=', journal_type),
                         ('company_id', 'child_of', [company_id])])
                res['fields'][field]['selection'] = journal_select
        return res

    @api.model
    def compute_debitnote(self):
        """
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: the account invoice debitnote’s ID or list of IDs

        """
        inv_obj = self.env['account.invoice']

        for form in self:
            created_inv = []
            date = False
            period = False
            description = False
            company = self.env.user.company_id
            journal_id = form.journal_id.id
            for inv in inv_obj.browse(self.env.context.get('active_ids')):
                if inv.state in ['draft', 'proforma2', 'cancel']:
                    raise UserError(_(''' Cannot create debit note for
                                 draft/proforma/cancel invoice.'''))
                if form.period.id:
                    period = form.period.id
                else:
                    period = inv.period_id and inv.period_id.id or False

                if not journal_id:
                    journal_id = inv.journal_id.id

                if form.date:
                    date = form.date
                    if not form.period.id:
                        self._cr.execute(
                            """ select
                                    name
                                from
                                    ir_model_fields
                                where
                                    model = 'account.period'
                                    and name = 'company_id'
                            """
                        )
                        result_query = self._cr.fetchone()
                        if result_query:
                            self._cr.execute("""
                                select p.id
                                from
                                    account_fiscalyear y,
                                    account_period p
                                where
                                    y.id=p.fiscalyear_id and
                                    date(%s) between p.date_start AND
                                    p.date_stop and y.company_id = %s
                                limit 1""", (date, company.id,))
                        else:
                            self._cr.execute("""SELECT id
                                    from account_period where date(%s)
                                    between date_start AND  date_stop \
                                    limit 1 """, (date,))
                        res = self._cr.fetchone()
                        if res:
                            period = res[0]
                else:
                    date = inv.date_invoice
                if form.description:
                    description = form.description
                else:
                    description = inv.name

                if not period:
                    raise UserError(_('No period found on the invoice.'))

                debitnote = inv.debitnote(date,
                                          period,
                                          description,
                                          journal_id)[0]
                debitnote.write({'date_due': date,
                                'check_total': inv.check_total})
                debitnote.button_compute()

                created_inv.append(debitnote.id)

            xml_id = (inv.type == 'out_invoice') and 'action_invoice_tree1' or\
                     (inv.type == 'in_invoice') and 'action_invoice_tree2'

            result = self.env.ref('account.' + xml_id)
            result = result.read()[0]
            result['domain'] = [('id', 'in', created_inv)]
            return result

    @api.multi
    def invoice_debitnote(self):
        for invoice in self:
            return invoice.compute_debitnote()
