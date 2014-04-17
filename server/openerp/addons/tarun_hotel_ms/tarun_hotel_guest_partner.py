# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

import datetime
from lxml import etree
import math
import pytz
import re
import openerp
from openerp import SUPERUSER_ID
from openerp import pooler, tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time



class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'max_points': fields.float('Max Points', help="Maximum Points a Guest can obtain"),
    }
    
    _defaults ={
                'max_points' : 1500.00,
                }
res_company()


class tarun_hotel_guest_partner(osv.osv):
    _description = 'Guest'
    _name = "tarun.hotel.guest.partner"


    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    def _has_image(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = obj.image != False
        return result
    
    def _get_cur_points(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        prod = self.browse(cr, uid, ids, context=context)  
        res = {}
        for o in prod:
            points = 0.0
            if o.points_hist:
                for lines in o.points_hist:
                    points+=lines.qty
                    points = min(o.company_id.max_points,points)
                    self.pool.get('tarun.hotel.guest.points').write(cr,uid,[lines.id],{'up_qty':points})
            res[o.id] = points
        return res 

    _order = "name"
    _columns = {
        'guest_ref': fields.char('Guest Ref.', size=128, required=True, select=True),
        'name': fields.char('First Name', size=128, required=True, select=True),
        'last_name': fields.char('Last Name', size=128, required=True, select=True),
        'user_id': fields.many2one('res.users', 'User', help='The internal user that is in charge of communicating with this contact if any.'),
        'comment': fields.text('Notes'),        
        'city': fields.char('City', size=128),
        'state_id': fields.many2one("res.country.state", 'State'),
        'country_id': fields.many2one('res.country', 'Country'),
        'country': fields.related('country_id', type='many2one', relation='res.country', string='Country',
                                  deprecated="This field will be removed as of OpenERP 7.1, use country_id instead"),
        'email': fields.char('Email', size=240),
        'phone': fields.char('Phone', size=64),
        'fax': fields.char('Fax', size=64),
        'mobile': fields.char('Mobile', size=64),        
        # image: all image fields are base64 encoded and PIL-supported
        'image': fields.binary("Image",
            help="This field holds the image used as avatar for this contact, limited to 1024x1024px"),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized image", type="binary", multi="_get_image",
            store={
                'tarun.hotel.guest.partner': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized image of this contact. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved. "\
                 "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Small-sized image", type="binary", multi="_get_image",
            store={
                'tarun.hotel.guest.partner': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized image of this contact. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
        'has_image': fields.function(_has_image, type="boolean"),
        'company_id': fields.many2one('res.company', 'Company', select=1),
        'color': fields.integer('Color Index'),
        'gender': fields.selection([('m', 'Male'), ('f', 'Female')], 'Gender',),
        'pref': fields.selection([('veg', 'Veg'), ('nveg', 'Non-Veg')], 'Diet',),
        'dob': fields.date('Date of Birth'),
        'cin_date': fields.date('Check-in Date'),
        'age': fields.integer('Age'),
        'book_hist': fields.one2many('tarun.hotel.book.order', 'guest_id', 'Booking History', readonly=True),  
        'available': fields.boolean('Available'),      
        'points_hist': fields.one2many('tarun.hotel.guest.points', 'guest_id', 'Points'),
        'points': fields.function(_get_cur_points, string='Points', type='float', readonly=True),
    }


    def _get_default_image(self, cr, uid, is_company, context=None, colorize=False):
        img_path = openerp.modules.get_module_resource('base', 'static/src/img',
                                                       ('avatar.png'))
        with open(img_path, 'rb') as f:
            image = f.read()

        # colorize user avatars
        image = tools.image_colorize(image)

        return tools.image_resize_image_big(image.encode('base64'))

    _defaults = {
        'company_id': lambda self, cr, uid, ctx: self.pool.get('res.company')._company_default_get(cr, uid, 'tarun.hotel.guest.partner', context=ctx),
        'color': 0,
        'image': False,
        'user_id': lambda obj, cr, uid, context: uid,
	'available': True,
    }


    def onchange_state(self, cr, uid, ids, state_id, context=None):
        if state_id:
            country_id = self.pool.get('res.country.state').browse(cr, uid, state_id, context).country_id.id
            return {'value':{'country_id':country_id}}
        return {}



    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.last_name+" "+record.name+" ["+record.guest_ref+"]"
            res.append((record.id, name))
        return res



class tarun_hotel_guest_points(osv.osv):
    _name = "tarun.hotel.guest.points"
    _description = "Guest Points"


    def purchase_open(self, cr, uid, ids, context=None):
        models = self.pool.get('ir.model.data')
        view = models.get_object_reference(cr, uid, 'tarun_hotel_ms', 'tarun_hotel_purchase_form')
        view_id = view and view[1] or False
        if not context:
            context = {}
        active_id = context.get('active_id')
        inv_id = self.browse(cr, uid, ids[0]).purchase_id.id
        
        return {
            'name': ('Purchase'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_id],
            'res_model': 'tarun.hotel.purchase',
            'context': "{}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': inv_id,
        }


    _columns = {
        'guest_id': fields.many2one('tarun.hotel.guest.partner', 'Guest Name', select=True),
        'name': fields.char('Name', size=128, required=True, select=True),
        'purchase_id': fields.many2one('tarun.hotel.purchase', 'Purchase Order', select=True),
        'qty': fields.float('Points'),
        'up_qty': fields.float('Updated Points'),
        'date': fields.datetime('Date', help="Date.", required=True, select=True, readonly=True),
        'user_id': fields.many2one('res.users', 'Approved By', readonly=True),
        'state': fields.selection([
            ('draft', 'To Approve'),
            ('done', 'Approved'),
            ], 'Status', readonly=True, select=True), 
    }

    
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda obj, cr, uid, context: uid,
    }


tarun_hotel_guest_points() 



class tarun_hotel_guest_weekly_presence(osv.osv):
    _name = "tarun.hotel.guest.weekly.presence"
    _description = "Guest Weekly Presence"

     
    def button_approve(self, cr, uid, ids, context=None):
        time_now = time.strftime('%Y-%m-%d %H:%M:%S')
        for do in self.browse(cr, uid, ids, context=context):
            self.pool.get('tarun.hotel.guest.points').create(cr,uid,{'guest_id':do.guest_id.id,
                                                                     'name':do.name,
                                                                     'qty':do.qty*525.00,
                                                                     'date':time_now,
                                                                     'user_id':uid,
                                                                     },context=context)
            
        return self.write(cr,uid,ids,{'state': 'done'},context=context)

    
    def _generate_guest_attendance(self, cr, uid, ids, context=None):
        """
        @return: Dictionary of values.
        """
        guests = self.pool.get('tarun.hotel.guest.partner').search(cr,uid,[('available','=',True)])
        for guest in self.pool.get('tarun.hotel.guest.partner').browse(cr,uid,guests):
            # default format is yyyy-mm-dd
            diff = (datetime.datetime.now() - datetime.datetime.strptime(guest.cin_date,'%Y-%m-%d')).days
            date_end = datetime.datetime.now().strftime('%Y-%m-%d')
            date_end2 = datetime.datetime.now().strftime('%Y-%d-%m')[5:10]
            date_start = guest.cin_date
            name = datetime.datetime.strptime(guest.cin_date,'%Y-%m-%d').strftime('%Y-%d-%m')[5:10] + ' to ' + date_end2

            if diff>7:
                date_start2 = datetime.datetime.now() - datetime.timedelta(days=7)
                name = date_start2.strftime('%Y-%d-%m')[5:10] + ' to ' + date_end2
                date_start = date_start2.strftime('%Y-%m-%d')
                diff = 7
            if diff > 0:
                self.create(cr,uid,{'name':name,
                                    'date_start':date_start,
                                    'date_end':date_end, 
                                    'qty': diff, 
                                    'guest_id': guest.id})
        return True


    def _approve_guest_attendance(self, cr, uid, ids, context=None):
        """
        @return: Dictionary of values.
        """
        to_app = self.search(cr,uid,[('state','=','draft')],context=context)
        return self.button_approve(cr,uid,to_app,context=context)


        
    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True, readonly=True, states={'draft': [('readonly', False)]}),
        'guest_id': fields.many2one('tarun.hotel.guest.partner', 'Guest Name', select=True, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'date_start': fields.date('Date', help="Date From", required=True, select=True, readonly=True, states={'draft': [('readonly', False)]}),
        'date_end': fields.date('Date', help="Date Till", required=True, select=True, readonly=True, states={'draft': [('readonly', False)]}),
        'guest_rel_related': fields.related('guest_id', 'guest_ref', type='char', string='Guest Ref.', readonly=True, store=True),
        'qty': fields.integer('Total Days Present', readonly=True, states={'draft': [('readonly', False)]}),
        'user_id': fields.many2one('res.users', 'User', readonly=True),
        'state': fields.selection([
            ('draft', 'To Approve'),
            ('done', 'Approved'),
            ], 'Status', readonly=True, select=True), 
        
    }
    
    _defaults = {
        'state':'draft',
        'user_id': lambda obj, cr, uid, context: uid,
    }
    
    _order = 'guest_rel_related asc'

    
    def create(self, cr, uid, vals, context=None):
        if 'qty' in vals:
            if vals['qty']>7 or vals['qty']<0:
                raise osv.except_osv(_('Error!'),
                _('Present Days is always less than 7 and greater than 0'))
        return super(tarun_hotel_guest_weekly_presence, self).create(cr, uid, vals, context=context)
        
        
    
    def write(self, cr, uid,ids, vals, context=None):
        if 'qty' in vals:
            if vals['qty']>7 or vals['qty']<0:
                raise osv.except_osv(_('Error!'),
                _('Present Days is always less than 7 and greater than 0'))
        return super(tarun_hotel_guest_weekly_presence, self).write(cr, uid,ids, vals, context=context)



tarun_hotel_guest_weekly_presence() 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
