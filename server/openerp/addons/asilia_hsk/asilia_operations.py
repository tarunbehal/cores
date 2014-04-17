from openerp.osv import fields, osv
import time
from datetime import datetime
from datetime import timedelta  
from openerp.tools.translate import _




class asilia_hotel_work_order(osv.osv):
    _name = "asilia.hotel.work.order"
    _description = "Work Order"

    def _generate_order(self, cr, uid, ids=False, context=None):
        rooms = self.pool.get('asilia.hotel.room').search(cr,1,[],context=context)
        time = 0.0
        room_list = []
        for room in self.pool.get('asilia.hotel.room').browse(cr,1,rooms,context=context):
            if room.alert:
                room_list.append(room.id)
                # time will be in mins
                time+=room.time+room.type_id.time
        print time, room_list
        tarun = great
        return self.fetch_mail(cr, uid, ids, context=context)

    
    def button_start(self, cr, uid, ids, context=None):
        
        for do in self.browse(cr, uid, ids, context=context):
            time_now = time.strftime('%Y-%m-%d %H:%M:%S')
            # validation for checking all checklist lines
            # write last action date
            # creating work order for manager
            return self.write(cr,uid,ids,{'state': 'start','check_out_date': time_now,},context=context)
        
    
    def button_finish(self, cr, uid, ids, context=None):
        
        for do in self.browse(cr, uid, ids, context=context):
            time_now = time.strftime('%Y-%m-%d %H:%M:%S')
            # validation for checking all checklist lines
            # write last action date
            # creating work order for manager
            return self.write(cr,uid,ids,{'state': 'finish','check_out_date': time_now,},context=context)
    
    def button_done(self, cr, uid, ids, context=None):
        
        for do in self.browse(cr, uid, ids, context=context):
            time_now = time.strftime('%Y-%m-%d %H:%M:%S')
            # validation for checking all checklist lines
            # write last action date
            # creating work order for manager
            return self.write(cr,uid,ids,{'state': 'done','check_out_date': time_now,},context=context)
            
    _columns = {
        'name': fields.char('Name', size=128, select=True),
        'date_sched': fields.datetime('Scheduled Date', help="Scheduled Date.", select=True, readonly=True),
        'date_start': fields.datetime('Date Start', help="Scheduled Date.", select=True, readonly=True),
        'date_end': fields.datetime('Date Done', help="Schedule Time.", readonly=True, select=True),        
        'time': fields.float('Cleaning Time', readonly=True, states={'draft': [('readonly', False)]}),          
        'user_id': fields.many2one('res.users', 'User', select=True, readonly=True, states={'draft': [('readonly', False)]}),
        'hotel_id':fields.related('room_id','hotel_id',type='many2one',relation='asilia.hotel',string='Hotel',readonly=True),
        'manager': fields.boolean('Manager', help="If unchecked,",readonly=True),   
        'state': fields.selection([
            ('draft', 'Draft'),
            ('start', 'Start'),
            ('finish', 'Finished'),
            ('done', 'Approved'),
            ], 'Status', readonly=True, select=True),    
        'room_id': fields.many2one('asilia.hotel.room', 'Room Number', required=True, select=True, readonly=True, states={'draft': [('readonly', False)]}),
        'description': fields.text('Description'),    
 
        
        
    }
    
    
    _defaults = {
                 'date_sched': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
                 'time':20.0,
                 'manager':False,
                 'state':'draft',
                 }

asilia_hotel_work_order() 


class asilia_hotel_work_order_lines_cln(osv.osv):
    _name = "asilia.hotel.work.order.lines.cln"
    _description = "Work Order Lines Cleaner"

    def button_done(self, cr, uid, ids, context=None):
        
        for do in self.browse(cr, uid, ids, context=context):
            return self.write(cr,uid,ids,{'state': 'done',},context=context)
       
    _columns = {
        'inv_id': fields.many2one('asilia.hotel.work.order', 'INV'),
        'name': fields.char('Name', size=128, select=True),        
        'state': fields.selection([
            ('draft', 'Draft'),
            ('done', 'Done'),
            ], 'Status', readonly=True, select=True),   
    }

    _defaults = {
                 'state':'draft',
                 }

asilia_hotel_work_order_lines_cln() 

class asilia_hotel_work_order_lines_man(osv.osv):
    _name = "asilia.hotel.work.order.lines.man"
    _description = "Work Order Lines Manager"

    def button_done(self, cr, uid, ids, context=None):
        
        for do in self.browse(cr, uid, ids, context=context):
            return self.write(cr,uid,ids,{'state': 'done',},context=context)


    def button_cancel(self, cr, uid, ids, context=None):
        
        for do in self.browse(cr, uid, ids, context=context):
            return self.write(cr,uid,ids,{'state': 'cancel',},context=context)
       
    _columns = {
        'inv_id': fields.many2one('asilia.hotel.work.order', 'INV'),
        'name': fields.char('Name', size=128, select=True),        
        'state': fields.selection([
            ('draft', 'Draft'),
            ('done', 'Done'),
            ('cancel', 'Not Approved'),
            ], 'Status', readonly=True, select=True),   
    }

    _defaults = {
                 'state':'draft',
                 }

asilia_hotel_work_order_lines_man() 

