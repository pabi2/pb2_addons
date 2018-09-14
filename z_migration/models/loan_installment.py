# -*- coding: utf-8 -*-
from openerp import models, fields


class LoanInstallment(models.Model):
    _inherit = 'loan.installment'

    name = fields.Char(
        readonly=False,
        size=500,
    )
    move_id = fields.Many2one(
        'account.move',
        readonly=False,
    )


class LoanInstallmentPlan(models.Model):
    _inherit = 'loan.installment.plan'

    move_line_id = fields.Many2one(
        'account.move.line',
        readonly=False,
    )
    installment = fields.Integer(
        readonly=False,
    )
    date_start = fields.Date(
        readonly=False,
    )
