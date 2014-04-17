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
import math

class schedule_cleanup(osv.osv_memory):
    _name = 'schedule.cleanup'
    _description = 'Schedule Cleanup'

    _columns = {
        'hotel_id': fields.many2one('asilia.hotel','Hotel'),
    }


    def start_schedule(self, cr, uid, ids, context=None):
        """
        Changes the Quantity of Product.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return:
        """
        for wiz in self.browse(cr, uid, ids, context=context):
            wos = self.pool.get('asilia.hotel.work.order').search(cr,uid,[('hotel_id.id','=',wiz.hotel_id.id),('user_id','=',False)],context=context)
            time1 = 0.0
            wo_list = []
            for wo in self.pool.get('asilia.hotel.work.order').browse(cr,uid,wos,context=context):
                wo_list.append(wo.id)
                time1+=wo.time
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        inv_ids =[]
        result = mod_obj.get_object_reference(cr, uid, 'asilia_hsk', 'action_asilia_hotel_sched_clean_form')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        test_id = self.pool.get('asilia.hotel.sched.clean').create(cr,uid,{'name':wiz.hotel_id.id,
                                      'date':time.strftime('%Y-%m-%d %H:%M:%S'),
                                      'room_clean':len(wo_list),
                                      'need_clean':int(math.ceil(time1/8.00)),
                                      'cleaner':int(math.ceil(time1/8.00)),
                                      'tot_time':time1,})
        print 't66',test_id, wo_list
        for wo1 in wo_list:
            self.pool.get('asilia.hotel.work.order').write(cr,1,wo1,{'sched_id':test_id})
        inv_ids.append(test_id)
        res = mod_obj.get_object_reference(cr, uid, 'asilia_hsk', 'asilia_hotel_sched_clean_form')
        result['views'] = [(res and res[1] or False, 'form')]
        result['res_id'] = inv_ids and inv_ids[0] or False
        result['target'] = 'inline'
        return result

schedule_cleanup()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

