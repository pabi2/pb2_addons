# -*- coding: utf-8 -*-
from openerp import fields, models


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
    amount_min = fields.Float(
        string="Minimum",
    )
    amount_max = fields.Float(
        string="Maximum",
    )
