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
from lxml import etree

class tarun_transfer_guest(osv.osv_memory):
    _name = 'tarun.transfer.guest'
    _description = 'Transfer Guest'



    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        rooms = self.pool.get('tarun.hotel.room').search(cr,uid,[],context=context)
        dm_room = []
        
        res = super(tarun_transfer_guest,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        if context.get('active_id', False):
            order = self.pool.get('tarun.hotel.book.order').browse(cr, uid,context['active_id'], context=context)
            doc = etree.XML(res['arch'])
            for room in self.pool.get('tarun.hotel.room').browse(cr,uid,rooms,context=context):
                if order.gender=="f" and order.guest_type.name=="Single":                    
                    if (room.available and not room.male_available) or (room.total_occupancy==0 and room.total_spaces>0):
                        dm_room.append(room.id)
                elif order.gender=="m" and order.guest_type.name=="Single":
                    if room.available and room.male_available:
                        dm_room.append(room.id)
                elif order.guest_type.name == "Family":
                    if (room.available and room.total_occupancy==0) or (room.family_available and room.occupancy_rate<100.00):
                        dm_room.append(room.id)    
                else:
                    if room.available and room.total_occupancy==0 and room.total_spaces>0:
                        dm_room.append(room.id)
           
            for node in doc.xpath("//field[@name='room_id']"):
                node.set('domain', "[('id','in',["+','.join(map(str, dm_room))+"])]")
            res['arch'] = etree.tostring(doc)
        return res

    _columns = {
        'room_id': fields.many2one('tarun.hotel.room', 'Room Number', required=True),
        
    }


    def transfer_guest(self, cr, uid, ids, context=None):
        """
        Changes the Quantity of Product.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return:
        """
        #record_id is booking order
        record_id = context and context.get('active_id',False)
        assert record_id, _('Active Id not found')
        book_obj = self.pool.get('tarun.hotel.book.order')
        for wiz_qty in self.browse(cr, uid, ids, context=context):
            cur_order = book_obj.browse(cr, uid, record_id, context=context)
            if wiz_qty.room_id.total_spaces-wiz_qty.room_id.total_occupancy<1:
                raise osv.except_osv(_('Processing Error!'), _('Room - %s has no available spaces. Select different room to transfer!') \
                                % (wiz_qty.room_id.name))
            else:   
                book_obj.write(cr,uid,[cur_order.id],{'room_id':wiz_qty.room_id.id})            
      
        return {}

tarun_transfer_guest()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

