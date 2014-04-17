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

class change_bed_qty(osv.osv_memory):
    _name = 'change.bed.qty'
    _description = 'Update Quantity of Beds'

    _columns = {
        'bed_type': fields.many2one('tarun.hotel.bed', 'Bed Type', required=True),
        'qty': fields.integer('Quantity'),
        
    }


    def change_bed_qty(self, cr, uid, ids, context=None):
        """
        Changes the Quantity of Product.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return:
        """
        record_id = context and context.get('active_id',False)
        assert record_id, _('Active Id not found')
        room_obj = self.pool.get('tarun.hotel.room')
        room_line_obj = self.pool.get('tarun.hotel.room.bed')
        for wiz_qty in self.browse(cr, uid, ids, context=context):
            cur_stock=0
            cur_room = room_obj.browse(cr, uid, record_id, context=context)
            if wiz_qty.bed_type.available_stock<wiz_qty.qty:
                raise osv.except_osv(_('Processing Error!'), _('Bed Type - %s has low available stock. Please add more beds of this type!') \
                                % (wiz_qty.bed_type.name))
            else:   
                if cur_room.bed_lines:             
                    for bed_line in cur_room.bed_lines:
                        if bed_line.name.id == wiz_qty.bed_type.id:
                            cur_stock=bed_line.bed_qty+wiz_qty.qty
                            room_line_obj.write(cr,uid,[bed_line.id],{'bed_qty':cur_stock},context=context)
                            return {}
                room_line_obj.create(cr,uid,{'room_id':cur_room.id,
                                             'name':wiz_qty.bed_type.id,
                                             'bed_qty':wiz_qty.qty
                                             },context=context)
            
      
        return {}

change_bed_qty()


class reduce_bed_qty(osv.osv_memory):
    _name = 'reduce.bed.qty'
    _description = 'Reduce Quantity of Beds'

    _columns = {
        'bed_type': fields.many2one('tarun.hotel.bed', 'Bed Type', required=True),
        'qty': fields.integer('Quantity'),
        
    }


    def reduce_bed_qty(self, cr, uid, ids, context=None):
        """
        Changes the Quantity of Product.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return:
        """
        record_id = context and context.get('active_id',False)
        assert record_id, _('Active Id not found')
        room_obj = self.pool.get('tarun.hotel.room')
        room_line_obj = self.pool.get('tarun.hotel.room.bed')
        for wiz_qty in self.browse(cr, uid, ids, context=context):
            cur_stock=0
            del_line = []
            cur_room = room_obj.browse(cr, uid, record_id, context=context)                     
            for bed_line in cur_room.bed_lines:
                if bed_line.name.id == wiz_qty.bed_type.id:
                    cur_stock=bed_line.bed_qty-wiz_qty.qty
                    # when bed qty is greater than 1 reduce bed qty in line
                    if cur_stock>0:
                        room_line_obj.write(cr,uid,[bed_line.id],{'bed_qty':cur_stock},context=context)
                        return {}
                    else:
                        del_line.append(bed_line.id)
                        print "delete line",del_line
                        cr.execute("""DELETE FROM tarun_hotel_room_bed WHERE id in %s""", (tuple(del_line),))
                        return {}
                else:
                    raise osv.except_osv(_('Processing Error!'), _('Bed Type - %s is not in this Room. Please select different bed type!') \
                                % (wiz_qty.bed_type.name))
        return {}


reduce_bed_qty()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

