# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class CreateStockAdjustWizard(models.TransientModel):
    _name = 'create.stock.adjust.wizard'

    adjust_product_line_ids = fields.One2many(
        'adjust.stock.product.line',
        'wizard_id',
        string='Adjust Product Line',
    )

    @api.model
    def view_init(self, fields_list):
        invoice_id = self._context.get('active_id')
        invoice = self.env['account.invoice'].browse(invoice_id)
        if invoice.state not in ('open', 'paid'):
            raise ValidationError(
                _('Only open invoice allowed!'))

    @api.model
    def default_get(self, fields):
        res = super(CreateStockAdjustWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        invoice = self.env['account.invoice'].browse(active_id)
        res = {}
        lines = []
        for inv_line in invoice.invoice_line:
            product = inv_line.product_id
            if not inv_line.purchase_line_id or \
                    product.type != 'product' or product.asset:
                continue
            vals = {'invoice_line_id': inv_line.id,
                    'from_product_id': inv_line.product_id.id,
                    'quantity': inv_line.quantity, }
            lines.append((0, 0, vals))
        print lines
        res['adjust_product_line_ids'] = lines
        return res

    @api.multi
    def create_stock_adjust(self):
        self.ensure_one()
        if True not in self.adjust_product_line_ids.mapped('check'):
            raise ValidationError(_('No selection!'))
        for product_line in self.adjust_product_line_ids:
            if not product_line.check:
                continue
            origin_move = False
            if product_line.invoice_line_id.move_id:  # Invoice from Stock Move
                # Get stock_move directly
                origin_move = product_line.invoice_line_id.move_id
            elif product_line.invoice_line_id.purchase_line_id:
                # Get stock_move via purchase_line_id
                stock_moves = \
                    product_line.invoice_line_id.purchase_line_id.move_ids
                if stock_moves:
                    origin_move = stock_moves[0]
            if not origin_move:
                raise ValidationError(
                    _('Can not find related stock.move to adjust!'))
            elif origin_move.picking_id.state != 'done':
                raise ValidationError(
                    _('Related stock.move is not transferred yet!'))
            # Adjust it!
            # Create reverse destination move, to remove the original
            return_move = origin_move.copy({
                'product_id': product_line.from_product_id.id,
                'name': '<~ %s' % product_line.from_product_id.name,
                'price_unit': -origin_move.price_unit,
                'product_uom_qty': product_line.quantity,
            })
            return_move.action_done()
            # Create move with changed product, to be new product move
            new_prod_move = origin_move.copy({
                'product_id': product_line.to_product_id.id,  # New product
                'name': '~> %s' % product_line.to_product_id.name,
                'product_uom_qty': product_line.quantity,
            })
            new_prod_move.action_done()
            invoice = product_line.invoice_line_id.invoice_id
            invoice.write({'stock_adjusted': True})
        return True


class AdjustStockProductLine(models.TransientModel):
    _name = 'adjust.stock.product.line'

    wizard_id = fields.Many2one(
        'create.stock.adjust.wizard',
        string='Stock Adjust',
        readonly=True,
    )
    check = fields.Boolean(
        string='Select',
        default=False,
    )
    invoice_line_id = fields.Many2one(
        'account.invoice.line',
        string='Invoice Line',
        readonly=True,
    )
    from_product_id = fields.Many2one(
        'product.product',
        related='invoice_line_id.product_id',
        string='From Product',
        readonly=True,
    )
    quantity = fields.Float(
        string='Quantity',
        required=True,
    )
    to_product_id = fields.Many2one(
        'product.product',
        string='To Product',
        required=True,
        domain=[('type', '=', 'product'), ('asset', '=', False)],
    )
