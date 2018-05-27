# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    consign_product = fields.Selection(
        [('yes', 'Consinged'),
         ('no', 'Non-Consigned')],
        string='Consign Product',
        compute='_compute_consign_product',
        store=True,
        help="If this is a consign_partner_id is specified",
    )
    consign_partner_id = fields.Many2one(
        'res.partner',
        string='Consign Partner',
        domain=[('supplier', '=', True)],
        help="If this is a consigned product from a supplier, specify here.",
    )

    @api.multi
    @api.depends('consign_partner_id')
    def _compute_consign_product(self):
        for rec in self:
            rec.consign_product = rec.consign_partner_id and 'yes' or 'no'

    @api.multi
    def write(self, vals):
        """ Consignment is change on this product, propagate to all moves """
        if 'consign_partner_id' in vals:
            Product = self.env['product.product']
            Move = self.env['stock.move']
            partner_id = vals['consign_partner_id']
            products = Product.search([('product_tmpl_id', 'in', self.ids)])
            moves = Move.search([('product_id', 'in', products.ids)])
            moves.write({'consign_partner_id': partner_id,
                         'consign_product': partner_id and 'yes' or 'no', })
        return super(ProductTemplate, self).write(vals)
