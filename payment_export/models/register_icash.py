# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError


class PabiRegister_iCash(models.Model):
    _name = 'pabi.register.icash'

    name = fields.Char(
        'Register number'
    )
    service_type = fields.Selection(
        [('direct', 'DIRECT'),('smart', 'SMART')],
        'Service Type'
    )
    export_date = fields.Date(
        'Register export date',
        default=fields.Date.context_today,
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('exported', 'Exported'),
         ('cancel', 'Cancelled')],
        string='Status',
        default='draft',
        readonly=True,
    )
    line_ids = fields.One2many(
        'pabi.register.icash.line',
        'register_id',
        'Supplier Account'
    )

    @api.model
    def create(self, vals):
        vals['state'] = 'draft'
        vals['name'] = self.env['ir.sequence'].next_by_code('register.icash')
        res = super(PabiRegister_iCash, self).create(vals)
        res._create_register_icash_line()
        return res

    @api.multi
    def write(self, vals):
        res = super(PabiRegister_iCash, self).write(vals)
        self.line_ids.unlink()
        self._create_register_icash_line()
        return res

    @api.multi
    def _create_register_icash_line(self):
        self.ensure_one()
        RegisterLineObj = self.env['pabi.register.icash.line']
        PartnerBankObj = self.env['res.partner.bank']
        dom = [('is_register','!=',True)]

        if self.line_ids:
            ids = self.line_ids.mapped('partner_bank_id').ids
            dom.append(('id', 'not in', ids))
        if self.service_type == 'direct':
            dom.append(('bank.abbrev', '=', 'BBL'))
        if self.service_type == 'smart':
            dom.append(('bank.abbrev', '!=', 'BBL'))

        parner_bank_search = PartnerBankObj.search(dom)

        for line in parner_bank_search:
            RegisterLineObj.create({'register_id': self.id,
                                    'partner_bank_id': line.id,
                                    'beneficiary_code': 'NSTDA_%s' % line.acc_number,
                                    'name_en': line.owner_name_en,
                                    'account_number': line.acc_number,
                                    'email': line.partner_id.email,
                                    })

    #@api.multi
    #def _create_register_icash_line(self):

    @api.multi
    def reload(self):
        self.line_ids.filtered(
            lambda l: l.partner_bank_id.is_register == True
            ).unlink()
        self.line_ids.onchange_partner_bank_id()
        self._create_register_icash_line()



class PabiRegister_iCashLine(models.Model):
    _name = 'pabi.register.icash.line'

    register_id = fields.Many2one(
        'pabi.register.icash'
    )
    partner_bank_id = fields.Many2one(
        'res.partner.bank'
    )
    beneficiary_code = fields.Char(
        'Beneficiary Code'
    )
    name_en = fields.Char(
        'Name En'
    )
    account_number = fields.Char(
        'Account Number'
    )
    email = fields.Char(
        'Email Account'
    )

    @api.onchange('partner_bank_id')
    def onchange_partner_bank_id(self):
        for rec in self:
            if rec.register_id.state == 'draft' and rec.partner_bank_id:
                rec.beneficiary_code = 'NSTDA_%s' % rec.partner_bank_id.acc_number
                rec.name_en = rec.partner_bank_id.owner_name_en
                rec.account_number = rec.partner_bank_id.acc_number
                rec.email = rec.partner_bank_id.partner_id.email

