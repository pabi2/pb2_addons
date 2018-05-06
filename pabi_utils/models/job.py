# -*- coding: utf-8 -*-
from openerp import models, fields


class QueueJob(models.Model):
    _inherit = 'queue.job'

    process = fields.Selection(
        [('Excel Report', 'Excel Report'),
         ('Import Excel', 'Import Excel'), ],
        string='Process',
        readonly=True,
    )
    res_ids = fields.Char(
        string='Result IDs',
        readonly=True,
        help="String representative of id list of related records",
    )
    res_model = fields.Char(
        string='Result Model',
        readonly=True,
        help="Model of the related record",
    )
