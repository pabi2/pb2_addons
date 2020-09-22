# -*- coding: utf-8 -*-
from openerp import fields, models, api


class ResBank(models.Model):
    _inherit = 'res.bank'

    name = fields.Char(
        translate=True,
    )
    abbrev = fields.Char(
        string='Abbreviation',
        size=100,
        required=False,
    )
    code = fields.Char(
        string='Code',
        size=100,
        required=False,
    )


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    def _get_domain_bank_branch(self):
        domain = "[('bank_id', '=', bank)]"
        return domain
    
    def _domain_bank_branch(self):
        domain = []
        if self.bank:
            domain = [('bank_id', '=', self.bank.id)]
        return domain

    
    bank_branch = fields.Many2one(
        'res.bank.branch',
        #domain="[('bank_id', '=', bank)]",
        #domain=_get_domain_bank_branch,
        domain=lambda self: self._domain_bank_branch(),
        string='Bank Branch',
        required=True,
    )
    
    @api.multi
    @api.onchange('bank')
    def _onchange_bank(self):
        for rec in self:
            if rec.bank:
                rec.bank_name = rec.bank.name
                rec.bank_bic = rec.bank.bic
                rec.bank_branch = False
                
                #return {'domain': {'bank_branch': [('bank_id', '=', rec.bank.id)]}}
    

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s %s' % (rec.bank.abbrev, rec.acc_number)))
        return res


class ResBankBranch(models.Model):
    _name = 'res.bank.branch'
    _description = 'Bank Branch'

    name = fields.Char(
        string='Name',
        size=500,
        translate=True,
        required=True,
    )
    code = fields.Char(
        string='Code',
        size=100,
        required=True,
    )
    bank_id = fields.Many2one(
        'res.bank',
        sring='Bank',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
