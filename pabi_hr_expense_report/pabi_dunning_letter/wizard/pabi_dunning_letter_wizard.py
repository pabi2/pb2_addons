# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class PABIDunnintLetterWizard(models.TransientModel):
    _name = 'pabi.dunning.letter.wizard'

    date_print = fields.Date(
        string='Print Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
    )
    due_days = fields.Selection(
        [('10', '10 days to due date'),
         ('5', '5 days to due date'),
         ('0', 'On due date'),
         ('-1', 'Pass due date')],
        string='Due (based on print date)',
        required=True,
    )
    print_pdf = fields.Boolean(
        string='Print as PDF',
        default=True,
    )
    send_email = fields.Boolean(
        string='Send Email',
        default=True,
    )
    dunning_list_ids = fields.One2many(
        'dunning.list',
        'wizard_id',
        string='List of Dunning',
    )
    # Temporary Fields todo remove
    group_email = fields.Char(
        string="Group Email",
        default="acf-adv@nstda.or.th",
    )

    @api.onchange('due_days')
    def _onchange_due_days(self):
        self.dunning_list_ids = []
        Line = self.env['dunning.list']
        Expense = self.env['hr.expense.expense']
        today = datetime.strptime(self.date_print,
                                  '%Y-%m-%d').date()
        date_due = today + relativedelta(days=int(self.due_days))
        date_due = date_due.strftime('%Y-%m-%d')
        operator = self.due_days == '-1' and '<=' or '='
        expenses = Expense.search([('state', '=', 'paid'),
                                   ('date_due', operator, date_due),
                                   ('amount_to_clearing', '>', 0.0)])
        for expense in expenses:
            new_line = Line.new()
            new_line.expense_id = expense
            new_line.select = True

            # Set Email-to on lines
            if self.due_days == '10':
                new_line.to_employee_ids = [(6, 0, [new_line.employee_id.id])]
                new_line.cc_employee_ids = [(6, 0, [])]
            elif self.due_days == '5':
                new_line.to_employee_ids = [(6, 0, [])]
                new_line.cc_employee_ids = [(6, 0, [new_line.employee_id.id])]
            else:
                new_line.to_employee_ids = [(6, 0, [])]
                new_line.cc_employee_ids = [(6, 0, [new_line.employee_id.id])]

            self.dunning_list_ids += new_line

    @api.multi
    def run_report(self):
        if not self.send_email and not self.print_pdf:
            return {}

        data = {'parameters': {}}
        report_name = 'pabi_dunning_letter'
        # For ORM, we search for ids, and only pass ids to parser and jasper
        exp_ids = [x.select and x.expense_id.id for x in self.dunning_list_ids]
        exp_ids = list(set(exp_ids))  # remove all False
        if False in exp_ids:
            exp_ids.remove(False)
        if not exp_ids:
            raise UserError(_('No dunning letter to print/email!'))

        # Send dunning letter by email to each of selected employees
        if self.send_email:
            self._send_dunning_letter_by_mail()

        if not self.print_pdf:
            return {}
        data['parameters']['ids'] = exp_ids
        data['parameters']['due_days'] = self.due_days
        data['parameters']['date_print'] = self.date_print
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
            'context': {'lang': 'th_TH'}
        }
        return res

    @api.model
    def _send_dunning_letter_by_mail(self):
        if not self.dunning_list_ids:
            return True
        template = False
        try:
            template = self.env.ref(
                'pabi_hr_expense_report.email_template_edi_10_days_to_due')
        except:
            pass
        if not self.group_email:
            raise UserError(
                _('Please enter valid email address for group email!'))
        if template:
            for line in self.dunning_list_ids:
                ctx = self.env.context.copy()
                ctx.update({
                    'due_days': self.due_days,
                    'date_print': self.date_print,
                    'email_attachment': True,
                })
                if line.expense_id and line.select:
                    to_email = False
                    cc_email = self.group_email
                    for to_line in line.to_employee_ids:
                        if to_line.work_email:
                            if not to_email:
                                to_email = to_line.work_email
                            else:
                                to_email = to_email + ',' + to_line.work_email

                    for cc_line in line.cc_employee_ids:
                        if cc_line.work_email:
                            cc_email = cc_email + ',' + cc_line.work_email
                    template.email_to = to_email
                    template.email_cc = cc_email
                    template.with_context(ctx).send_mail(line.expense_id.id)
        return True


class DunningList(models.TransientModel):
    _name = 'dunning.list'

    wizard_id = fields.Many2one(
        'pabi.dunning.letter.wizard',
        string='Wizard',
        readonly=True,
    )
    select = fields.Boolean(
        string='Select',
        default=True,
    )
    expense_id = fields.Many2one(
        'hr.expense.expense',
        string='Employee Advance',
    )
    employee_id = fields.Many2one(
        'hr.employee',
        related='expense_id.employee_id',
        string='Employee',
        readonly=True,
    )
    date_due = fields.Date(
        string='Date Due',
        related='expense_id.date_due',
        readonly=True,
    )
    amount_to_clearing = fields.Float(
        string='Amount Remaining',
        related='expense_id.amount_to_clearing',
        readonly=True,
    )
    description = fields.Char(
        string='Description',
        related='expense_id.name',
        readonly=True,
    )
    to_employee_ids = fields.Many2many(
        'hr.employee',
        string="TO",
    )
    cc_employee_ids = fields.Many2many(
        'hr.employee',
        string="CC",
    )
