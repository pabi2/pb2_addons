# -*- coding: utf-8 -*-
from openerp import models, fields, api


class QueueJob(models.Model):
    _inherit = 'queue.job'

    process_id = fields.Many2one(
        'pabi.process',
        string='Process',
        readonly=True,
    )
    res_ids = fields.Char(
        string='Result IDs',
        readonly=True,
        size=500,
        help="String representative of id list of related records",
    )
    res_model = fields.Char(
        string='Result Model',
        readonly=True,
        size=500,
        help="Model of the related record",
    )

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s | %s' % (rec.name, rec.state.upper())))
        return result


class PabiProcess(models.Model):
    _name = 'pabi.process'
    _description = 'Process name for job running inside pabi_utils'

    name = fields.Char(
        string='Process Name',
        required=True,
    )
