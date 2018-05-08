# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class PabiActionAssetCompute(models.TransientModel):
    """ PABI Action for Compute Asset Depreciation """
    _name = 'pabi.action.asset.compute'
    _inherit = 'pabi.action'

    # Criteria
    calendar_period_id = fields.Many2one(
        'account.period.calendar',
        string='Period',
        domain=[('state', '=', 'draft')],
        required=True,
    )
    categ_ids = fields.Many2many(
        'product.category',
        string='Category',
        domain=lambda self: self._get_categ_domain()
    )
    profile_ids = fields.Many2many(
        'account.asset.profile',
        string='Profile',
    )

    @api.multi
    def check_affected_asset(self):
        self.ensure_one()
        AssetLine = self.env['account.asset.line']
        assets = self._search_asset(self.calendar_period_id.id,
                                    self.categ_ids.ids,
                                    self.profile_ids.ids)
        # Assume 1 depre line for 1 asset always
        num_asset = AssetLine.search_count(
            [('asset_id', 'in', assets.ids),
             ('type', '=', 'depreciate'),
             ('init_entry', '=', False),
             ('line_date', '<=', self.calendar_period_id.date_stop),
             ('line_date', '>=', self.calendar_period_id.date_start),
             ('move_check', '=', False)])
        raise UserError(
            _('%s assets will be computed in this operation') % num_asset)

    @api.model
    def _get_categ_domain(self):
        asset_journal = self.env.ref('pabi_asset_management.journal_asset')
        return [('property_stock_journal', '=', asset_journal.id),
                ('type', '=', 'normal')]

    @api.onchange('categ_ids')
    def _onchange_categ_ids(self):
        self.profile_ids = []

    @api.model
    def _search_asset(self, period_id, categ_ids, profile_ids):
        # Search for
        domain = []
        if categ_ids:
            domain += [('profile_id.product_categ_id', 'in', categ_ids)]
        if profile_ids:
            domain += [('profile_id', 'in', profile_ids)]
        # Start computing
        assets = self.env['account.asset'].search(
            [('state', '=', 'open'), ('type', '=', 'normal')] + domain)
        return assets

    @api.multi
    def asset_compute(self, period_id, categ_ids, profile_ids):
        period = self.env['account.period'].browse(period_id)
        assets = self._search_asset(period_id, categ_ids, profile_ids)
        created_move_ids, error_log = \
            assets._compute_entries(period, check_triggers=True)
        # Return
        records = self.env['account.move'].browse(created_move_ids)
        if not error_log:
            error_log = _('Computed depreciation for %s assets') % len(records)
        result_msg = error_log
        return (records, result_msg)

    @api.multi
    def pabi_action(self):
        self.ensure_one()
        # Prepare job information
        process_xml_id = 'pabi_async_process.asset_compute'
        job_desc = _('Compute Asset Depreciation for %s by %s' %
                     (self.calendar_period_id.display_name,
                      self.env.user.display_name))
        func_name = 'asset_compute'
        # Prepare kwargs, the params for method action_generate
        kwargs = {'period_id': self.calendar_period_id.id,
                  'categ_ids': self.categ_ids.ids,
                  'profile_ids': self.profile_ids.ids, }
        # Call the function
        res = super(PabiActionAssetCompute, self).\
            pabi_action(process_xml_id, job_desc, func_name, **kwargs)
        return res
