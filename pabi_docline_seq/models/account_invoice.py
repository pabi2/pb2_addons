# -*- coding: utf-8 -*-
from openerp import fields, models, api, SUPERUSER_ID


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def init(self, cr):
        """ On module update, recompute all documents """
        cr.execute("""
            select distinct invoice_id
            from account_invoice ai
            join account_invoice_line ail on ail.invoice_id = ai.id
            where ail.docline_seq = 0
        """)
        invoice_ids = [x[0] for x in cr.fetchall()]
        for invoice_id in invoice_ids:
            self._compute_docline_seq(cr, SUPERUSER_ID, invoice_id)

    @api.model
    def _compute_docline_seq(self, invoice_id):
        """ Recompute docline sequence by invoice_id """
        self._cr.execute("""
            update account_invoice_line ail
            set docline_seq = new_seq
            from (select id, docline_seq,
                  row_number() over(order by (sequence, id)) as new_seq
                  from account_invoice_line where invoice_id = %s) seq
            where seq.id = ail.id""", (invoice_id, ))
        return True

    @api.multi
    @api.constrains('invoice_line')
    def _check_docline_seq(self):
        for invoice in self:
            self._compute_docline_seq(invoice.id)
        return True


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    docline_seq = fields.Integer(
        string='#',
        readonly=True,
        help="Sequence auto generated after document is confirmed",
    )
