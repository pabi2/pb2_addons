# -*- coding: utf-8 -*-
from openerp import models, fields, api

class XLSXReportStatus(models.Model):
    _name = 'xlsx.report.status'


    name = fields.Char(
        string='Name',
        required=True,
    )
    status = fields.Char(
        string='Status',
        required=True,
    )
    code = fields.Char(
        string='Code',
    )
    location = fields.Char(
        string='Location',
    )
