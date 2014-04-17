#  -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time

from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _
from openerp.addons.base_calendar.base_calendar import get_real_ids, base_calendar_id2real_id
from openerp.addons.base_status.base_state import base_state
#
# tarun.hotel.activity is defined here so that it may be used by modules other than crm,
# without forcing the installation of crm.
#

class tarun_hotel_activity_type(osv.Model):
    _name = 'tarun.hotel.activity.type'
    _description = 'Activity Type'
    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
    }

class tarun_hotel_activity(base_state, osv.Model):
    """ Model for Activity """
    _name = 'tarun.hotel.activity'
    _description = "Activities"
    _order = "id desc"
    _inherit = ["calendar.event", "mail.thread", "ir.needaction_mixin"]
    _columns = {
        # base_state required fields
        'create_date': fields.datetime('Creation Date', readonly=True),
        'write_date': fields.datetime('Write Date', readonly=True),
        'date_open': fields.datetime('Confirmed', readonly=True),
        'date_closed': fields.datetime('Closed', readonly=True),
        'partner_ids': fields.many2many('res.partner', 'tarun_hotel_activity_partner_rel', 'meeting_id', 'partner_id',
            string='Attendees', states={'done': [('readonly', True)]}),
        'state': fields.selection(
                    [('draft', 'Unconfirmed'), ('open', 'Confirmed'), ('done', 'Done')],
                    string='Status', size=16, readonly=True, track_visibility='onchange'),
        'activity_type': fields.selection(
                    [('WA', 'Waged Activity'), ('OA', 'Other Activity'),('DIS', 'Distribution'), ('MEAL', 'Meals')],
                    string='Activity Type', size=16, required=True, states={'done': [('readonly', True)]}),
        'activity_group': fields.many2one('tarun.hotel.activity.type', 'Activity Group', states={'done': [('readonly', True)]}, select=True),
        # Meeting fields
        'name': fields.char('Activity Name', size=128, required=True, states={'done': [('readonly', True)]}),
        'attendee_ids': fields.many2many('calendar.attendee', 'meeting_attendee_rel',\
                            'event_id', 'attendee_id', 'Attendees', states={'done': [('readonly', True)]}),
        
        'max_people': fields.integer('Max People'),
        # this will be made as function field and will be used for closing the activity with condition to check if state is draft 
        # or else will modify write action not to modify anything with close or if date is getting modified check for dates and mark as done
        # 
        'current_count': fields.integer('Current Count'),
        'activity_line': fields.one2many('tarun.hotel.activity.line', 'activity_id', 'Activity Lines', readonly=True, states={'draft': [('readonly', False)], 'open': [('readonly', False)]}),
    }
    _defaults = {
        'state': 'open',
    }

    def message_get_subscription_data(self, cr, uid, ids, context=None):
        res = {}
        for virtual_id in ids:
            real_id = base_calendar_id2real_id(virtual_id)
            result = super(tarun_hotel_activity, self).message_get_subscription_data(cr, uid, [real_id], context=context)
            res[virtual_id] = result[real_id]
        return res

    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default['attendee_ids'] = False
        return super(tarun_hotel_activity, self).copy(cr, uid, id, default, context)

    def onchange_partner_ids(self, cr, uid, ids, value, context=None):
        """ The basic purpose of this method is to check that destination partners
            effectively have email addresses. Otherwise a warning is thrown.
            :param value: value format: [[6, 0, [3, 4]]]
        """
        res = {'value': {}}
        if not value or not value[0] or not value[0][0] == 6:
            return
        res.update(self.check_partners_email(cr, uid, value[0][2], context=context))
        return res

    def check_partners_email(self, cr, uid, partner_ids, context=None):
        """ Verify that selected partner_ids have an email_address defined.
            Otherwise throw a warning. """
        partner_wo_email_lst = []
        for partner in self.pool.get('res.partner').browse(cr, uid, partner_ids, context=context):
            if not partner.email:
                partner_wo_email_lst.append(partner)
        if not partner_wo_email_lst:
            return {}
        warning_msg = _('The following contacts have no email address :')
        for partner in partner_wo_email_lst:
            warning_msg += '\n- %s' % (partner.name)
        return {'warning': {
                    'title': _('Email addresses not found'),
                    'message': warning_msg,
                    }
                }
    # ----------------------------------------
    # OpenChatter
    # ----------------------------------------

    # shows events of the day for this user
    def _needaction_domain_get(self, cr, uid, context=None):
        return [('date', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT + ' 23:59:59')), ('date_deadline', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT + ' 23:59:59')), ('user_id', '=', uid)]

    def message_post(self, cr, uid, thread_id, body='', subject=None, type='notification',
                        subtype=None, parent_id=False, attachments=None, context=None, **kwargs):
        if isinstance(thread_id, str):
            thread_id = get_real_ids(thread_id)
        return super(tarun_hotel_activity, self).message_post(cr, uid, thread_id, body=body, subject=subject, type=type, subtype=subtype, parent_id=parent_id, attachments=attachments, context=context, **kwargs)



class tarun_hotel_activity_line(osv.osv):


    _name = 'tarun.hotel.activity.line'
    _description = 'Hotel Activity Line'
    _columns = {
        'activity_id': fields.many2one('tarun.hotel.activity', 'Activity Reference', required=True, ondelete='cascade', select=True, readonly=True, states={'draft':[('readonly',False)]}),
        'name': fields.text('Description'),
        'guest_id': fields.many2one('tarun.hotel.guest.partner', 'Guest Name'),
        'state': fields.selection([('cancel', 'Cancelled'),('draft', 'Draft'),('confirmed', 'Confirmed'),('exception', 'Exception'),('done', 'Done')], 'Status',readonly=True),
        'type':fields.related('activity_id', 'activity_type', type='char', store=True, string='Type',readonly=True),
        'group_id':fields.related('activity_id', 'activity_group', type='many2one', relation='tarun.hotel.activity.type', store=True, string='Activity Group',readonly=True),
        'user_id':fields.related('activity_id', 'user_id', type='many2one', relation='res.users', store=True, string='User',readonly=True),
        'date':fields.related('activity_id', 'date', type='datetime', store=True, string='Date',readonly=True),
        'duration':fields.related('activity_id', 'duration', type='float', store=True, string='Duration',readonly=True),
    }

    _defaults = {
        'state': 'draft',
    }









class mail_message(osv.osv):
    _inherit = "mail.message"

    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        '''
        convert the search on real ids in the case it was asked on virtual ids, then call super()
        '''
        for index in range(len(args)):
            if args[index][0] == "res_id" and isinstance(args[index][2], str):
                args[index][2] = get_real_ids(args[index][2])
        return super(mail_message, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

    def _find_allowed_model_wise(self, cr, uid, doc_model, doc_dict, context=None):
        if doc_model == 'tarun.hotel.activity':
            for virtual_id in self.pool.get(doc_model).get_recurrent_ids(cr, uid, doc_dict.keys(), [], context=context):
                doc_dict.setdefault(virtual_id, doc_dict[get_real_ids(virtual_id)])
        return super(mail_message, self)._find_allowed_model_wise(cr, uid, doc_model, doc_dict, context=context)

class ir_attachment(osv.osv):
    _inherit = "ir.attachment"

    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        '''
        convert the search on real ids in the case it was asked on virtual ids, then call super()
        '''
        for index in range(len(args)):
            if args[index][0] == "res_id" and isinstance(args[index][2], str):
                args[index][2] = get_real_ids(args[index][2])
        return super(ir_attachment, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

    def write(self, cr, uid, ids, vals, context=None):
        '''
        when posting an attachment (new or not), convert the virtual ids in real ids.
        '''
        if isinstance(vals.get('res_id'), str):
            vals['res_id'] = get_real_ids(vals.get('res_id'))
        return super(ir_attachment, self).write(cr, uid, ids, vals, context=context)

class invite_wizard(osv.osv_memory):
    _inherit = 'mail.wizard.invite'

    def default_get(self, cr, uid, fields, context=None):
        '''
        in case someone clicked on 'invite others' wizard in the followers widget, transform virtual ids in real ids
        '''
        result = super(invite_wizard, self).default_get(cr, uid, fields, context=context)
        if 'res_id' in result:
            result['res_id'] = get_real_ids(result['res_id'])
        return result
