# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time
from datetime import datetime
from datetime import timedelta  

class tarun_customer_selection(osv.osv_memory):
    _name = 'tarun.customer.selection'
    _description = 'Input for Report'

    _columns = {
        'user_id': fields.many2one('res.users', 'User', readonly=True),        
        'guest_id': fields.many2one('tarun.hotel.guest.partner', 'Guest Billing', select=True),
        'b_code': fields.char('Scan', size=128, required=True, select=True),
    }

    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
    }



    def code_change(self, cr, uid, ids, code, context=None):
        if not code:
            return {'value': {'b_code': False, 'guest_id': False}}
        else:
            part = self.pool.get('tarun.hotel.guest.partner').search(cr,uid,[('guest_ref','=',code)])
            if not part:
                warning_msg = _('Guest Code or Guest Ref not Found. Please Scan again or type-in manually.!!!')
                return {'warning': {
                    'title': _('Warning'),
                    'message': warning_msg,
                    'value': {'b_code': False, 'guest_id': False},
                    }
                }
            return {'value': {'b_code': code,  'guest_id': part[0]}}

    
    
    def confirm_cashier_window(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return:
        """
        dict = {}
        for wiz_qty in self.browse(cr, uid, ids, context=context):
            if not wiz_qty.guest_id:                
                if not wiz_qty.b_code:
                    raise osv.except_osv(_('Warning!'), _('Guest Code or Guest Ref not Found. Please Scan again or type-in manually.!!!'))
                else:
                    part = self.pool.get('tarun.hotel.guest.partner').search(cr,uid,[('guest_ref','=',wiz_qty.b_code)])
                    if not part:
                        raise osv.except_osv(_('Warning!'), _('Guest Code or Guest Ref not Found. Please Scan again or type-in manually.!!!'))
                    p_id = part[0]
            elif not wiz_qty.b_code and  not wiz_qty.guest_id:
                raise osv.except_osv(_('Warning!'), _('Guest Code or Guest Ref not Found. Please Scan again or type-in manually.!!!'))
            else:
                p_id = wiz_qty.guest_id.id
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        inv_ids =[]
        result = mod_obj.get_object_reference(cr, uid, 'tarun_hotel_ms', 'action_tarun_hotel_purchase_form')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        test_id = self.pool.get('tarun.hotel.purchase').create(cr,uid,{'name':'/','date':time.strftime('%Y-%m-%d %H:%M:%S'),'user_id':uid,'guest_id':p_id,'state':'draft'})
        inv_ids.append(test_id)
        res = mod_obj.get_object_reference(cr, uid, 'tarun_hotel_ms', 'tarun_hotel_purchase_form')
        result['views'] = [(res and res[1] or False, 'form')]
        result['res_id'] = inv_ids and inv_ids[0] or False
        result['target'] = 'inline'
        return result




tarun_customer_selection()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

