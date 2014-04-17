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
import time
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class change_guest_points(osv.osv_memory):
    _name = 'change.guest.points'
    _description = 'Update Guest Points'

    _columns = {
        'points': fields.float('Points'),
        
    }


    def change_guest_points(self, cr, uid, ids, context=None):
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
        guest_obj = self.pool.get('tarun.hotel.guest.partner')
        points_obj = self.pool.get('tarun.hotel.guest.points')
        for wiz in self.browse(cr, uid, ids, context=context):
            guest = guest_obj.browse(cr, uid, record_id, context=context)
            if (guest.points < wiz.points) or (guest.points > wiz.points):
                bal = wiz.points - guest.points
                time_now = time.strftime('%Y-%m-%d %H:%M:%S')
                points_obj.create(cr,uid,{
                    'guest_id':guest.id,
                    'name':'Points Updated',
                    'qty':bal,
                    'date':time_now,
                    'user_id':uid,
                        },context=context)    
            
        return {}

change_guest_points()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

