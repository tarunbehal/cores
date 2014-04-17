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
import time
import openerp.addons.decimal_precision as dp
from lxml import etree

class tarun_cout_guest(osv.osv_memory):
    _name = 'tarun.cout.guest'
    _description = 'Checkout Guest'



    _columns = {
        'sure': fields.boolean('Are you Sure?', help="If checked, means Carrier is reserved to process this Delivery Order."),
    }


    def cout_guest(self, cr, uid, ids, context=None):
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
            time_now = time.strftime('%Y-%m-%d %H:%M:%S')
            date_now = time.strftime('%Y-%m-%d')
            book_obj.write(cr,uid,[cur_order.id],{'state':'cout','check_out_date': time_now,'check_out_date_view': date_now}) 
            if cur_order.guest_id:
                self.pool.get('tarun.hotel.guest.partner').write(cr,uid,cur_order.guest_id.id,{'available':False},context=context)  
        return {}

tarun_cout_guest()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

