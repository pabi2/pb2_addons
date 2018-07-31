# -*- coding: utf-8 -*-
from openerp import fields, models, api


class WkfConfigDocType(models.Model):
    _name = 'wkf.config.doctype'
    _description = 'Work Flow Document Type Configuration'

    name = fields.Char(
        string='Name',
        required=True,
    )
    description = fields.Text(
        string='Description',
    )
    module = fields.Selection([
        ('purchase', "Purchase & Inventory"),
        ('purchase_pd', "Purchase PD"),
        ('account', "Accounting & Finance"), ],
        string='Module',
        required=True,
    )


class WkfCmdApprovalLevel(models.Model):
    _name = 'wkf.cmd.level'
    _description = 'Level'

    sequence = fields.Integer(
        string='Sequence',
    )
    name = fields.Char(
        string='Name',
        required=True,
    )
    description = fields.Text(
        string='Description',
    )


class WkfCmdApprovalAmount(models.Model):
    _name = 'wkf.cmd.approval.amount'
    _description = 'Basis Approval Amount'

    org_id = fields.Many2one(
        'res.org',
        string='Org',
        required=True,
    )
    doctype_id = fields.Many2one(
        'wkf.config.doctype',
        string='Document Type',
        required=True,
    )
    level = fields.Many2one(
        'wkf.cmd.level',
        string='Level',
        required=True,
    )
    amount_max = fields.Float(
        string='Maximum',
    )
    amount_max_emotion = fields.Float(
        string='Maximum Emotion',
        compute='_compute_amount_max_emotion',
        store=True,
        help="This is an internally used field by Alfresco "
        "Amount = 0.01 signify always in approval workflow."
    )

    @api.multi
    @api.depends('org_id.level_emotion')
    def _compute_amount_max_emotion(self):
        for rec in self:
            if rec.org_id.level_emotion:
                if rec.level.sequence < rec.org_id.level_emotion.sequence:
                    rec.amount_max_emotion = 0.01  # Alfresco read this value
                else:
                    rec.amount_max_emotion = rec.amount_max
            else:
                rec.amount_max_emotion = rec.amount_max
