# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_picking_cancel(self):
        for rec in self:
            if rec.state != 'done':
                raise ValidationError(_('Picking not in done state!'))
            # Check all invoices cancelled
            for invoice in rec.ref_invoice_ids:
                if invoice.state != 'cancel':
                    raise ValidationError(
                        _('To cancel this transfer, '
                          'all invoices must be cancelled'))
            # Check all asset removed
            assets = self.env['account.asset'].search([('picking_id', '=',
                                                        rec.id)])
            for asset in assets:
                if asset.state != 'removed':
                    raise ValidationError(
                        _('To cancel this transfer, '
                          'all assets must be removed'))
            for stock_move in rec.move_lines:
                reverse_move = stock_move.copy({
                    'name': '<~ %s' % stock_move.name,
                    'location_id': stock_move.location_dest_id.id,
                    'location_dest_id': stock_move.location_id.id,
                    'asset_value': False,
                })
                reverse_move.with_context(
                    force_valuation_amount=stock_move.price_unit,
                    force_no_asset_profile=True  # Do not create asset
                ).action_done()
        self._cr.execute("""
            update stock_picking set state = 'cancel' where id in %s
        """, (tuple(self.ids), ))
        return True
