# -*- coding: utf-8 -*-
import os
from openerp import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta as rdelta
from openerp.exceptions import ValidationError, except_orm


class PurchaseContract(models.Model):
    _name = 'purchase.contract'
    _description = 'PO Contract'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = \
        'operating_unit_id, fiscalyear_id desc, running desc, poc_rev desc'

    name = fields.Char(
        string='PO Name',
        size=1000,
        requried=True,
        track_visibility='onchange',
    )
    display_code = fields.Char(
        string='Contract No.',
        compute='_compute_display_code',
        store=True,
    )
    requisition_id = fields.Many2one(
        'purchase.requisition',
        ondelete='set null',
        string='PD Reference',
        default=lambda self: self._default_requisition_id(),
    )
    is_verify = fields.Boolean(
        string='Verify',
        default=False
    )
    is_central_purchase = fields.Boolean(
        string="Central Purchase",
        compute='_compute_requisition_related',
    )
    poc_code = fields.Char(
        string='Contract Code.',
        size=1000,
        readonly=True
    )
    poc_rev = fields.Integer(
        string='Reversion',
        default=0,
        readonly=True
    )
    create_emp_id = fields.Many2one(
        'hr.employee',
        ondelete='set null',
        string='Creator',
        default=lambda self: self.env.user.employee_id,
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        # default=lambda self: self.env['res.users'].
        # operating_unit_default_get(self._uid),
        related='create_uid.default_operating_unit_id',
        store=True,
        readonly=True,
    )
    contract_type_id = fields.Many2one(
        'purchase.contract.type',
        ondelete='set null',
        string='Contract Type',
        track_visibility='onchange',
        required=True
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        readonly=True
    )
    running = fields.Integer(
        string='YearRunning'
    )
    supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        domain=[('customer', '=', True)],
        track_visibility='onchange',
    )
    action_date = fields.Date(
        string='Action Date',
        required=True,
        track_visibility='onchange'
    )
    start_date = fields.Date(
        string='Start Date',
        required=True,
        track_visibility='onchange'
    )
    end_date = fields.Date(
        string="End Date",
        required=True,
        track_visibility='onchange'
    )
    duration_start2end = fields.Char(
        string='Duration',
        compute='_compute_duration_start2end',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        compute='_compute_requisition_related',
    )
    num_of_period = fields.Integer(
        string='Period',
        required=True,
        track_visibility='onchange',
        default=0,
    )
    purchase_type_id = fields.Many2one(
        'purchase.type',
        string='Type',
        compute='_compute_requisition_related',
    )
    purchase_method_id = fields.Many2one(
        'purchase.method',
        ondelete='set null',
        string='Purchase Method',
        compute='_compute_requisition_related',
    )
    collateral_performance_amt = fields.Float(
        string='Collateral performance amount',
        track_visibility='onchange',
    )
    contract_amt = fields.Float(
        string='Contract amount',
        track_visibility='onchange',
    )
    collateral_agreement_amt = fields.Float(
        string='Collateral agreement amount',
        track_visibility='onchange',
    )
    advance_amt = fields.Float(
        string='Pay in advance',
    )
    collateral_type_id = fields.Many2one(
        'purchase.contract.collateral',
        string='Collateral type',
        ondelete="set null",
    )
    check_final_date = fields.Date(
        string='Final inspection period date',
    )
    contractual_fines = fields.Float(
        string='Contractual fines',
    )
    warranty = fields.Integer(
        string='Warranty',
    )
    warranty_type = fields.Selection(
        [('day', 'Day'),
         ('month', 'Month'),
         ('year', 'Year')],
        string='Warranty type'
    )
    fine_rate = fields.Char(
        string='Fine Rate',
        compute='_compute_fine_rate',
    )
    collateral_no = fields.Char(
        string='Collateral No.',
        size=100,
    )
    contractual_amt = fields.Float(
        string='Contractual Amount',
    )
    collateral_due_date = fields.Date(
        string='Collateral Due date',
    )
    collateral_remand_date = fields.Date(
        string='Collateral Remand date',
    )
    collateral_remand_real_date = fields.Date(
        string='Collateral Remand date (Real)',
    )
    collateral_received_date = fields.Date(
        string='Collateral Received date',
    )
    bank = fields.Char(
        string='Bank',
        size=100,
    )
    branch = fields.Char(
        string='Branch',
        size=100,
    )
    account = fields.Char(
        string='Account',
        size=100,
    )
    collateral_date = fields.Date(
        string='Collateral Date',
    )
    description = fields.Text(
        string='Description',
        size=1000,
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('generate', 'Generated'),
         ('send', 'Sending'),
         ('close', 'Closed'),
         ('cancel_generate', 'Cancel Generated'),
         ('terminate', 'Terminated'),
         ('delete', 'Delete'), ],
        string='Status',
        default='draft',
    )
    write_emp_id = fields.Many2one(
        'hr.employee',
        string='Updated By Emp',
        related='write_uid.employee_id',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    send_uid = fields.Many2one(
        'hr.employee',
        string='Sent By'
    )
    send_date = fields.Date(
        string='Sent Date',
    )
    close_uid = fields.Many2one(
        'hr.employee',
        string='Closed By',
    )
    close_date = fields.Date(
        sring='Closed Date',
    )
    verify_uid = fields.Many2one(
        'hr.employee',
        string='Verified By',
    )
    verify_date = fields.Date(
        'Verify Date',
    )
    cancel_uid = fields.Many2one(
        'hr.employee',
        string='Cancel By',
    )
    cancel_date = fields.Date(
        string='Cancel Date',
    )
    terminate_uid = fields.Many2one(
        'hr.employee',
        string='Terminated By',
    )
    terminate_date = fields.Date(
        string='Terminated Date',
    )
    reflow_uid = fields.Many2one(
        'hr.employee',
        string='Reflow By',
    )
    reflow_date = fields.Date(
        string='Reflow Date',
    )
    reversion_uid = fields.Many2one(
        'hr.employee',
        string='Reversion By',
    )
    reversion_date = fields.Date(
        string='Reversion Date',
    )
    _sql_constraints = [
        ('code_uniq', 'UNIQUE(display_code)',
         'The contract no must be unique!'),
    ]

    @api.model
    def _default_requisition_id(self):
        active_model = self._context.get('active_model', False)
        if active_model and active_model == 'purchase.requisition':
            return self._context.get('active_id', False)
        return False

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        self.name = self.requisition_id.objective
        quotes = self.requisition_id.purchase_ids.\
            filtered(lambda l: l.state == 'done')
        self.supplier_id = quotes and quotes[0].partner_id or False
        self.contract_amt = self.requisition_id.total_budget_value

    @api.multi
    def _compute_requisition_related(self):
        for rec in self:
            if not rec.requisition_id:
                continue
            rec.is_central_purchase = rec.requisition_id.is_central_purchase
            rec.currency_id = rec.requisition_id.currency_id
            rec.purchase_type_id = rec.requisition_id.purchase_type_id
            rec.purchase_method_id = rec.requisition_id.purchase_method_id

    @api.multi
    @api.depends('requisition_id')
    def _compute_fine_rate(self):
        for rec in self:
            quotes = rec.requisition_id.purchase_ids.\
                filtered(lambda l: l.state == 'done')
            po = quotes and quotes[0] or False
            if po:
                if po.fine_condition == 'day':
                    rec.fine_rate = '%s / %s / %s' % \
                        (po.fine_rate, po.fine_condition, po.fine_num_days)
                elif po.fine_condition == 'date':
                    date_fine = datetime.strptime(
                        po.date_fine, '%Y-%m-%d').strftime('%m/%d/%y')
                    rec.fine_rate = '%s / %s / %s' % \
                        (po.fine_rate, po.fine_condition, date_fine)
                else:
                    rec.fine_rate = False
            else:
                rec.fine_rate = False

    @api.model
    def create(self, vals):
        # Get 2 Digits Org
        self._context.get('active_model')
        if self._context.get('active_model') == 'purchase.requisition':
            requisition_id = self._context.get('active_id', False)
            req = self.env['purchase.requisition'].browse(requisition_id)
            if req.state != 'open':
                raise ValidationError(
                    _("Contract can be created only during 'Bid Selection'"))
        format_code = ''
        operating_unit = self.env.user.default_operating_unit_id
        if not operating_unit:
            raise ValidationError(
                _('You cannot create PO contract without Operating Unit!'))
        if not vals.get('action_date', False):
            raise ValidationError(_('No Action Date!'))
        Fiscal = self.env['account.fiscalyear']
        fiscal_id = Fiscal.find(vals['action_date'])
        fiscalyear = Fiscal.browse(fiscal_id)
        rev_no = vals.get('poc_rev', 0)
        # New Contract (CENTRAL-2016-322-R1)
        running = 0
        if rev_no == 0:
            running = self.sudo().search_count([
                ('operating_unit_id', '=', operating_unit.id),
                ('fiscalyear_id', '=', fiscalyear.id),
                ('poc_rev', '=', 0)]) + 1
        else:  # Reversion (CO-51-2016-322-R1)
            running = vals.get('running', 0)
        org_str = operating_unit.org_id.code or \
            operating_unit.org_id.name_short or 'N/A'
        format_code = '%s-%s-%s' % (org_str, fiscalyear.name, str(running))
        vals.update({'poc_rev': rev_no,
                     'poc_code': format_code,
                     'fiscalyear_id': fiscalyear.id,
                     'running': running,
                     'state': 'generate'})
        po_contract = super(PurchaseContract, self).create(vals)
        return po_contract

    @api.multi
    def name_get(self):
        res = []
        for po in self:
            if po.poc_code and po.poc_rev == 0:
                res.append((po.id, "%s" % po.poc_code))
            elif po.poc_code and po.poc_rev > 0:
                res.append((po.id, "%s-R%s" % (po.poc_code, str(po.poc_rev))))
        return res

    @api.multi
    def action_button_verify_doc(self):
        return self.write({
            'is_verify': True,
            'verify_uid': self.env.user.employee_id.id,
            'verify_date': fields.Date.context_today(self), })

    @api.multi
    def action_button_send_doc(self):
        for rec in self:
            doc_count = self.env['ir.attachment'].search_count(
                [('res_model', '=', 'purchase.contract'),
                 ('res_id', '=', rec.id)])
            if doc_count > 0:
                rec.write({
                    'send_uid': self.env.user.employee_id.id,
                    'send_date': fields.Date.context_today(self),
                    'state': rec.verify_date and 'close' or 'send'
                })
            else:
                raise ValidationError(_("Please attach contract"))
        return True

    @api.multi
    def action_button_close(self):
        for rec in self:
            if rec.collateral_remand_date and rec.collateral_received_date:
                rec.write({
                    'close_uid': self.env.user.employee_id.id,
                    'close_date': fields.Date.context_today(self),
                    'state': 'close'
                })
            else:
                raise ValidationError(
                    _("Please enter Collateral's Received and Remand Date"))
        return True

    @api.multi
    def action_button_reflow(self):
        self.write({'reflow_uid': self.env.user.employee_id.id,
                    'reflow_date': fields.Date.context_today(self),
                    'state': 'generate'})
        return True

    @api.multi
    def action_button_reversion(self):
        self.ensure_one()
        count_po_gen = self.sudo().search_count(
            [('poc_code', '=', self.poc_code), ('state', '=', 'generate')])
        if count_po_gen == 0:  # No pending stateu "Generate", can reversion
            count_po_rev = self.sudo().search_count(
                [('poc_code', '=', self.poc_code)])
            next_rev = count_po_rev
            poc = self.copy({'poc_rev': next_rev,
                             'state': 'generate',
                             'active': True,
                             })
            docs = self.env['ir.attachment'].search(
                [('res_model', '=', 'purchase.contract'),
                 ('res_id', '=', self.id)])
            for doc in docs:
                revname = '_R%s' % self.poc_rev
                tempname = doc.name.replace(revname, '')
                filename, file_extension = os.path.splitext(tempname)
                name = '%s_R%s%s' % (filename, next_rev, file_extension)
                doc.copy({'res_id': poc.id, 'name': name})
            self.write({'reflow_uid': self.env.user.employee_id.id,
                        'send_doc_date': fields.Date.context_today(self),
                        'active': False})
            form = self.env.ref(
                'pabi_purchase_contract.purchase_contract_form_view', False)
            return {'name': _('PO Contract'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': form.id,
                    'res_model': 'purchase.contract',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': poc.id, }
        else:
            raise except_orm(
                _('Can not to be Reversion'),
                _('The contract no. %s, not all documents are sent') %
                (self.poc_code,))

    @api.multi
    def action_button_delete_reversion(self):
        self.ensure_one()
        po_code = self.poc_code
        self.unlink()
        po = self.search(
            [('poc_code', '=', po_code)], order='poc_rev desc', limit=1)
        form = self.env.ref(
            'pabi_purchase_contract.purchase_contract_form_view', False)
        return {'name': _('PO Contract'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': form.id,
                'res_model': 'purchase.contract',
                'domain': [],
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': po.id}

    @api.multi
    @api.depends('poc_code', 'poc_rev')
    def _compute_display_code(self):
        for rec in self:
            name = False
            if rec.poc_code and rec.poc_rev == 0:
                name = ("%s" % (rec.poc_code or ''))
            elif rec.poc_code and rec.poc_rev > 0:
                name = ("%s-R%s" %
                        (rec.poc_code or '', str(rec.poc_rev) or ''))
            rec.display_code = name

    @api.multi
    @api.depends('start_date', 'end_date')
    def _compute_duration_start2end(self):
        for rec in self:
            start2end = '0 Day'
            if rec.start_date and rec.end_date:
                if rec.start_date <= rec.end_date:
                    start_date = datetime.strptime(rec.start_date, '%Y-%m-%d')
                    end_date = datetime.strptime(rec.end_date, '%Y-%m-%d')
                    start = start_date.date()
                    end = end_date.date()
                    if end < start:
                        rec.duration_start2end = start2end
                        return
                    enddate = end + timedelta(days=1)
                    rd = rdelta(enddate, start)
                    start2end = _('%s Year %s Month %s Day') % \
                        (str(rd.years), str(rd.months), str(rd.days))
                else:
                    start2end = _("** Wrong Date **")
            rec.duration_start2end = start2end


class PurchaseContractCollateral(models.Model):
    _name = 'purchase.contract.collateral'
    _description = 'PO Contract Collateral'

    name = fields.Char(
        string='Name',
        size=500,
    )


class PurchaseContractType(models.Model):
    _name = 'purchase.contract.type'
    _description = 'PO Contract Type'

    name = fields.Char(
        string='Name',
        size=500,
    )
