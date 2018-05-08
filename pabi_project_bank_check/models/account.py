# -*- coding: utf-8 -*-
from openerp import models, api, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    project_ids = fields.Many2many(
        'res.project',
        'project_journal_rel',
        'project_id', 'journal_id',
        string='Used only on project',
        help="This bank account can be used only for selected project.\n"
        "Supplier payment to this project, only this bank account will show/"
    )
    bank_mandate_emp_id = fields.Many2one(
        'hr.employee',
        string='Project bank mandate',
        help="Information about bank madate for this account, if any."
    )

    @api.onchange('project_ids')
    def _onchange_project_ids(self):
        self.bank_mandate_emp_id = False

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        use_project_journal = self._context.get('use_project_journal', False)
        project_journal_ids = self._context.get('project_journal_ids', False)
        if use_project_journal:
            if ['project_ids', '=', False] in args:
                args.remove(['project_ids', '=', False])
            journal_ids = project_journal_ids and \
                project_journal_ids[0] and project_journal_ids[0][2] or []
            if journal_ids:
                domain = [('id', 'in', journal_ids)]
                args += domain
        return super(AccountJournal, self).name_search(name=name,
                                                       args=args,
                                                       operator=operator,
                                                       limit=limit)
