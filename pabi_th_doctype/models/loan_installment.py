# -*- coding: utf-8 -*-
from openerp import models, api


class LoanInstallment(models.Model):
    _inherit = 'loan.installment'

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            # Find doctype_id
            refer_type = 'loan_installment'
            doctype = self.env['res.doctype'].get_doctype(refer_type)
            fiscalyear_id = self.env['account.fiscalyear'].find()
            # --
            self = self.with_context(doctype_id=doctype.id,
                                     fiscalyear_id=fiscalyear_id)
            # It will try to use doctype_id first, if not available, rollback
            name = self.env['ir.sequence'].get('loan.installment')
            vals.update({'name': name})
        return super(LoanInstallment, self).create(vals)
