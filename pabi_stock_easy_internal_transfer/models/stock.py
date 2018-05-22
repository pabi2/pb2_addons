# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_partner_loc = fields.Boolean(
        string='Is Partner Location',
        compute='_compute_is_partner_loc',
        readonly=True,
    )

    @api.model
    def default_get(self, fields):
        res = super(StockPicking, self).default_get(fields)
        ou = self.env['res.users'].operating_unit_default_get(self._uid)
        # Find quick picking type with warehouse_id in same ou
        picking_type = self.env['stock.picking.type'].search([
            ('quick_view', '=', True),
            ('warehouse_id.operating_unit_id', 'in', ou.ids)], limit=1)
        res['picking_type_id'] = picking_type and picking_type[0].id or False
        return res

    @api.multi
    @api.depends('force_location_dest_id', 'force_location_id')
    def _compute_is_partner_loc(self):
        for r in self:
            if r.force_location_dest_id.usage in ('customer', 'supplier') or \
                    r.force_location_id.usage in ('customer', 'supplier'):
                r.is_partner_loc = True
            else:
                r.is_partner_loc = False

    @api.multi
    def action_confirm(self):
        """ For internal, we allow real time product, coz there is no account
        move. But for in/out, product must be periodic to avoid account move
        """
        for rec in self:
            if not (rec.force_location_id.usage == 'internal' and
                    rec.force_location_dest_id.usage == 'internal'):
                if 'real_time' in \
                        rec.move_lines.mapped('product_id.valuation'):
                    raise ValidationError(
                        _('For non-internal tranfer, only products with \n'
                          'inventory valuation = periodic are allowed'))
            if rec.force_location_id == rec.force_location_dest_id:
                raise ValidationError(
                    _('Source and destination should not be the same'))
        return super(StockPicking, self).action_confirm()


class StockMove(models.Model):
    _inherit = 'stock.move'

    consign_product = fields.Selection(
        [('yes', 'Consinged'),
         ('no', 'Non-Consigned')],
        string='Consign Product',
        readonly=True,
        help="If this is a consign_partner_id is specified",
    )
    consign_partner_id = fields.Many2one(
        'res.partner',
        string='Consign Partner',
        readonly=True,
        help="If this is a consigned product from a supplier, specify here.",
    )

    @api.multi
    def location_id_change(self, location_id, consign_partner_id):
        """ Overwrite, to show only 1) non-asset 2) consign_partner_id """
        # quant = self.env['stock.quant'].search([
        #     ('location_id', '=', location_id),
        #     ('qty', '>=', 1.0)])
        # product = quant.mapped("product_id")
        print consign_partner_id
        domain = [('asset', '=', False)]
        if consign_partner_id:
            domain += [('consign_partner_id', '=', consign_partner_id)]
        products = self.env['product.product'].search(domain)
        return {'domain': {'product_id': [('id', 'in', products.ids)]}}
