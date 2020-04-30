# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class IRAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.multi
    def unlink(self):
        """
            issue #4519 :
            - Purchase Request :
                - All state delete by pr manager
            - PD :
                - 'Draft' state delete by pr users
                - 'Confirm/To Verify/Bid Selection/PO Created' state
                    delete by pr manager
            - Purchase Order :
                - 'Draft/Waiting to Release' state delete by pr users
                - 'PO Release/Done' state delete by pr manager
            - Purchase Billing :
                - 'Draft' state delete by pr users
                - 'Billed' state delete by pr manager

            MG3 -> Procurement Manager (Manager)
            MG2 -> Procurement (Users)
        """
        if len(self) == 1:
            res_model = self._name
            res_id = self.res_id
            user_access = self.sudo().env['pabi.security.line'].search([
                ('user_id', '=', self.env.user.id)], order='id desc', limit=1)
            # PR
            if self.res_model:
                object_model = self.env[self.res_model].browse(self.res_id)
            if self.res_model == 'purchase.request' and \
                (self.env.user.id != self.create_uid.id and
                    (user_access and not user_access.mg3)):
                raise ValidationError(_('Access Denied!'))
            # PD
            if self.res_model == 'purchase.requisition' and \
                object_model.state not in ['rejected', 'cancel'] and \
                (self.env.user.id != self.create_uid.id and
                    (user_access and not user_access.mg2)):
                raise ValidationError(_('Access Denied!'))
            # PO
            if self.res_model == 'purchase.order':
                # User
                if object_model.state in ['draft', 'confirmed'] and \
                    (self.env.user.id != self.create_uid.id and
                        (user_access and not user_access.mg2)):
                    raise ValidationError(_('Access Denied!'))
                # Manager
                elif object_model.state in ['approved', 'done'] and \
                    (self.env.user.id != self.create_uid.id and
                        (user_access and not user_access.mg3)):
                    raise ValidationError(_('Access Denied!'))
            # BL
            if self.res_model == 'purchase.billing':
                # User
                if object_model.state == 'draft' and \
                    (self.env.user.id != self.create_uid.id and
                        (user_access and not user_access.mg2)):
                    raise ValidationError(_('Access Denied!'))
                # Manager
                elif object_model.state == 'billed' and \
                    (self.env.user.id != self.create_uid.id and
                        (user_access and not user_access.mg3)):
                    raise ValidationError(_('Access Denied!'))
            if res_model and res_id and \
                    (self.env.user.id == self.create_uid.id or
                     self.env.user.has_group('base.group_erp_manager')):
                object = self.env[res_model].browse(res_id)
                if object._columns.get('state', False):
                    if 'draft' in object.state:
                        self = self.sudo()
            if self.res_model:
                object_model.message_post(body=_(
                    'Attachment file "%s" has been deleted.') % (self.name,))
        return super(IRAttachment, self).unlink()
