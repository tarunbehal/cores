from openerp.osv import fields, osv
import time
from datetime import datetime
from datetime import timedelta  
from openerp.tools.translate import _


class res_users(osv.osv):
    _inherit = 'res.users'
    _columns = {
        'default_hotel_id': fields.many2one('asilia.hotel','Hotel'),
        'cleaner': fields.boolean('Cleaner'),   
    }

res_users()


class asilia_hotel(osv.osv):
    _name = "asilia.hotel"
    _description = "Hotel"

      
    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True),
             
       
    }

    
asilia_hotel() 


class asilia_room_chklist(osv.osv):
    _name = "asilia.room.chklist"
    _description = "Room Checklist"

      
    _columns = {
        'name': fields.char('Name', size=600, required=True, select=True),
    }

    
asilia_room_chklist() 

class asilia_hotel_room(osv.osv):
    _name = "asilia.hotel.room"
    _description = "Room"


    def _get_availability(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        if not ids:
            tarun = great
        rooms = self.browse(cr, uid, ids, context=context) 
        order_obj = self.pool.get('asilia.hotel.book.order')      
        res = {}
        for room in rooms:
            avail = True 
            order_lines = order_obj.search(cr,uid,[('room_id.id','=',room.id)], context=context)
            for lines in order_obj.browse(cr,uid,order_lines,context=context):
                time_now = time.strftime('%Y-%m-%d %H:%M:%S')
                if lines.state=="cin" and lines.check_in_date<time_now:
                    avail = False
            res[room.id] = avail
        return res  
    

    def _get_alert(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        rooms = self.browse(cr, uid, ids, context=context)    
        res = {}
        for room in rooms:
            if not room.last_action_date:
                alert = True 
            else:
                if room.schedule == '12hrs':
                    schd = 0.5
                elif room.schedule == 'daily':
                    schd = 1
                elif room.schedule == 'weekly':
                    schd = 7
                elif room.schedule == 'monthly':
                    schd = 30
                do1 = datetime.strptime(room.last_action_date,'%Y-%m-%d %H:%M:%S')
                do1 = do1+timedelta(days=schd)
                time_now = datetime.now()
                if time_now<do1:
                    alert = False
                else:
                    alert = True
            res[room.id] = alert
        return res  
    
    def _get_hotel_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        h_id = self.pool.get('res.users').read(cr, uid, uid,['default_hotel_id'], context=context)['default_hotel_id']
        return h_id and h_id[0] or False


    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.type_id.name+" "+record.name
            res.append((record.id, name))
        return res
      
    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True),
        'type_id': fields.many2one('asilia.hotel.room.type', 'Place Type', required=True, select=True),
        'available': fields.function(_get_availability, string='Available', type='boolean'),
        'alert': fields.function(_get_alert, string='Alert', type='boolean'),
        'time': fields.float('Additional Time(if any)'),  
        'exp_time': fields.float('Expiry Time(in hrs)', required=True),  
        'hotel_id':fields.related('type_id','hotel_id',type='many2one',relation='asilia.hotel',string='Hotel',readonly=True),
        'last_action_date': fields.datetime('Last action Date', help="This date will suggest when was the last time a cleaning order was scheduled.", readonly=True, select=True),     
        'schedule': fields.selection([
            ('12hrs', '12 Hours'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ], 'Cleaning Schedule', required=True, select=True),   
        'company_id': fields.many2one('res.company', 'Company', select=1),
        'clean_chk': fields.many2many('asilia.room.chklist', 'cleaner_chk_rel', 'room_id', 'chk_id', 'Cleaner Checklist', help="This will be used as Cleaner Checklist"),
        'hsk_chk': fields.many2many('asilia.room.chklist', 'hsk_chk_rel', 'room_id', 'chk_id', 'HSK Checklist', help="This will be used as supervisor Checklist"),
                    
       
    }
    
    _defaults = {
                 'time':0.0,
                 'hotel_id':_get_hotel_id,
                 'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'asilia.hotel.room', context=c),
                 }

    
asilia_hotel_room() 


class asilia_hotel_room_type(osv.osv):
    _name = "asilia.hotel.room.type"
    _description = "Room Type"

    
    def _get_hotel_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        h_id = self.pool.get('res.users').read(cr, uid, uid,['default_hotel_id'], context=context)['default_hotel_id']
        return h_id and h_id[0] or False
            
    _columns = {
        'name': fields.char('Type', size=128, required=True, select=True),
        'time': fields.float('Cleaning Time'),          
        'hotel_id': fields.many2one('asilia.hotel','Hotel',required=True,select=1),
        'company_id': fields.many2one('res.company', 'Company', select=1),
    }
    
    
    _defaults = {
                 'time':20.0,
                 'hotel_id':_get_hotel_id,
                 'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'asilia.hotel.room.type', context=c),
                 }

asilia_hotel_room_type() 




class asilia_hotel_book_order(osv.osv):
    _name = "asilia.hotel.book.order"
    _description = "Book Order"

    def button_check_out(self, cr, uid, ids, context=None):
        
        for do in self.browse(cr, uid, ids, context=context):
            time_now = time.strftime('%Y-%m-%d %H:%M:%S')
            return self.write(cr,uid,ids,{'state': 'cout','check_out_date': time_now,},context=context)
    
    def button_check_in(self, cr, uid, ids, context=None):
        
        for do in self.browse(cr, uid, ids, context=context):
            time_now = time.strftime('%Y-%m-%d %H:%M:%S')
            return self.write(cr,uid,ids,{'state': 'cin','check_in_date': time_now,},context=context)
        
        
    _columns = {
        'name': fields.char('Book Ref.', size=128, required=True, readonly=True),
        'first_name': fields.char('First Name', size=128, required=True, select=True, readonly=True, states={'cin': [('readonly', False)]}),
        'last_name': fields.char('Last Name', size=128, required=True, select=True, readonly=True, states={'cin': [('readonly', False)]}),
        'check_in_date': fields.datetime('Check - In', help="Check-in Time.", required=True, select=True, readonly=True, states={'cin': [('readonly', False)]}),
        'check_out_date': fields.datetime('Check - Out', help="Check-out Time.", readonly=True, select=True),
        'user_id': fields.many2one('res.users', 'User', select=True, readonly=True, states={'cin': [('readonly', False)]}),
        'company_id': fields.many2one('res.company', 'Company', select=1),
        'hotel_id':fields.related('room_id','hotel_id',type='many2one',relation='asilia.hotel',string='Hotel',readonly=True),    
        'stay_type': fields.selection([
            ('ov', 'Overnachting'),
            ('ki', 'Wissel'),
            ('wk', 'Kleine Wissel'),
            ], 'Type', required=True, select=True, states={'cin': [('readonly', False)]}),    
        'state': fields.selection([
            ('cin', 'Check IN'),
            ('cout', 'Check OUT'),
            ], 'Status', readonly=True, select=True),    
        'room_id': fields.many2one('asilia.hotel.room', 'Room Number', required=True, select=True, readonly=True, states={'cin': [('readonly', False)]}),

    }
    
    _defaults = {
        'check_in_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': 'cin',
        'user_id': lambda obj, cr, uid, context: uid,
        'name': lambda obj, cr, uid, context: '/',
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'asilia.hotel.book.order', context=c),
    }

    
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'asilia.hotel.book.order') or '/'
            
        return super(asilia_hotel_book_order, self).create(cr, uid, vals, context=context)
    
    def onchange_name(self, cr, uid, ids, last_name=False, first_name=False, context=None):
        room_obj = self.pool.get('asilia.hotel.room')
        room_ids = room_obj.search(cr,uid,[('type_id.name','=','Rooms')],context=context)
        dom = [room.id for room in room_obj.browse(cr,uid,room_ids,context=context) if room.available]
        set_dm = "[('id','in',["+','.join(map(str, dom))+"])]"  
        return {'domain':{'room_id':set_dm},'value':{'room_id':None}}





asilia_hotel_book_order() 


class asilia_hotel_work_order(osv.osv):
    _name = "asilia.hotel.work.order"
    _description = "Work Order"

    def _generate_order(self, cr, uid, ids=False, context=None):
        rooms = self.pool.get('asilia.hotel.room').search(cr,1,[],context=context)
        time_now = time.strftime('%Y-%m-%d %H:%M:%S')
        print "in cron generate"
        for room in self.pool.get('asilia.hotel.room').browse(cr,1,rooms):
            if room.alert:
                self.pool.get('asilia.hotel.work.order').create(cr,uid,{'name':'Cleaning Order','room_id':room.id})
                self.pool.get('asilia.hotel.room').write(cr,1,room.id,{'last_action_date':time_now})
        return True


    def _close_order(self, cr, uid, ids=False, context=None):
        wos = self.search(cr,1,[('state','=','finish')],context=context)
        for wo in self.browse(cr, uid, wos, context=context):
            do1 = datetime.strptime(wo.date_end,'%Y-%m-%d %H:%M:%S')
            do1 = do1 + timedelta(days=wo.room_id.exp_time/24.00)
            if do1>datetime.now():
                for lines in wo.man_lines:
                    self.pool.get('asilia.hotel.work.order.lines.man').button_done(cr, 1, lines.id, context=context)
                self.write(cr,1,wo.id,{'state': 'done'},context=context)
        return True
    
    
    def button_issue(self, cr, uid, ids, context=None):
        
        for do in self.browse(cr, uid, ids, context=context):
            if not do.user_id:
                raise osv.except_osv(_('Warning!'), _("Please assign user!!"))
            return self.write(cr,uid,ids,{'state': 'issue'},context=context)
    
    def button_start(self, cr, uid, ids, context=None):
        
        for do in self.browse(cr, uid, ids, context=context):
            time_now = time.strftime('%Y-%m-%d %H:%M:%S')
            for lines in do.room_id.clean_chk:
                self.pool.get('asilia.hotel.work.order.lines.cln').create(cr,uid,{'name':lines.name,'inv_id':do.id})
            return self.write(cr,uid,ids,{'state': 'start','date_start':time_now},context=context)
        
    
    def button_finish(self, cr, uid, ids, context=None):
        
        for do in self.browse(cr, uid, ids, context=context):
            time_now = time.strftime('%Y-%m-%d %H:%M:%S')
            for lines in do.cln_lines:
                if lines.state!='done':
                    raise osv.except_osv(_('Warning!'), _("Please mark all checklist items done to proceed!!"))
            for lines in do.room_id.hsk_chk:
                self.pool.get('asilia.hotel.work.order.lines.man').create(cr,uid,{'name':lines.name,'inv_id':do.id})
            
            return self.write(cr,uid,ids,{'state': 'finish','date_end':time_now,'manager':True},context=context)
    
    def button_done(self, cr, uid, ids, context=None):        
        for do in self.browse(cr, uid, ids, context=context):
            flag=True
            for lines in do.man_lines:
                if lines.state=='draft':
                    raise osv.except_osv(_('Warning!'), _("Please update all checklist items to proceed!!"))
                elif lines.state=='cancel':
                    flag=False
            if flag:
                return self.write(cr,uid,ids,{'state': 'done'},context=context)
            else:
                return self.write(cr,uid,ids,{'state': 'na'},context=context)

    def button_na(self, cr, uid, ids, context=None):
        
        for do in self.browse(cr, uid, ids, context=context):
            return self.write(cr,uid,ids,{'state': 'na'},context=context)
        
    def _get_total_time(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        occ = self.browse(cr, uid, ids, context=context)    
        res ={}
        for wo in occ:
            tot = 0.0
            tot = wo.room_id.time + wo.room_id.type_id.time
            res[wo.id] = tot
        return res  
            
    _columns = {
        'name': fields.char('Name', size=128, select=True),
        'date_sched': fields.datetime('Scheduled Date', help="Scheduled Date.", select=True, readonly=True),
        'date_start': fields.datetime('Date Start', help="Scheduled Date.", select=True, readonly=True),
        'date_end': fields.datetime('Date Done', help="Schedule Time.", readonly=True, select=True), 
        'time': fields.function(_get_total_time, string='Cleaning Time', type='float'),       
        'user_id': fields.many2one('res.users', 'User', select=True),
        'hotel_id':fields.related('room_id','hotel_id',type='many2one',relation='asilia.hotel',string='Hotel',readonly=True),
        'manager': fields.boolean('Manager', help="If unchecked,",readonly=True),   
        'state': fields.selection([
            ('draft', 'Draft'),
            ('issue', 'Issue'),
            ('start', 'Start'),
            ('finish', 'Finished'),
            ('na', 'Not Approved'),
            ('done', 'Approved'),
            ], 'Status', readonly=True, select=True),    
        'room_id': fields.many2one('asilia.hotel.room', 'Room Number', required=True, select=True),
        'description': fields.text('Description'),    
        'cln_lines': fields.one2many('asilia.hotel.work.order.lines.cln','inv_id', 'Cleaner Checklist'),
        'man_lines': fields.one2many('asilia.hotel.work.order.lines.man','inv_id', 'Manager Checklist'),
        'sched_id': fields.many2one('asilia.hotel.sched.clean', 'Scheduled by'),
        'company_id': fields.many2one('res.company', 'Company', select=1),
 
        
        
    }
    
    
    _defaults = {
                 'state':'draft',
                 'date_sched': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
                 'manager':False,
                 'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'asilia.hotel.work.order', context=c),
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


#cleaning orders scheduling and assignment

class asilia_hotel_sched_clean(osv.osv):
    _name = "asilia.hotel.sched.clean"
    _description = "Schedule Cleaning Order"


    def button_done(self, cr, uid, ids, context=None):
        
        for co in self.browse(cr, uid, ids, context=context):
            if len(co.selected_cleaners)!=co.cleaner:
                raise osv.except_osv(_('Warning!'), _('Cleaners selected is %d but Total Cleaners is %d. Total Cleaners must be equal to Selected Cleaners!')%(len(co.selected_cleaners),co.cleaner))
            cleaners = [a.id for a in co.selected_cleaners]
            wols = [a.id for a in co.work_lines]
            index = 0
            for wo in wols:
                self.pool.get('asilia.hotel.work.order').write(cr,uid,wo,{'user_id':cleaners[index%len(cleaners)]})                
                index+=1
        self.pool.get('asilia.hotel.work.order').button_issue(cr, uid, wols, context=context)
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'asilia_hsk', 'action_asilia_hotel_work_order1')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        result['domain'] = "[('id','in',["+','.join(map(str, wols))+"])]"
        return result

        
    _columns = {       
        'name':fields.many2one('asilia.hotel', 'Hotel', readonly=True),
        'room_clean': fields.integer('Total Rooms'),       
        'need_clean': fields.integer('Needed Cleaner'),      
        'cleaner': fields.integer('Total Cleaners'),     
        'tot_time': fields.float('Total Time'),
        'date': fields.datetime('Date', help="Date.", required=True, select=True, readonly=True),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('done', 'Done'),
            ('cancel', 'Cancel'),
            ], 'Status', readonly=True, select=True),    
        'user_id': fields.many2one('res.users', 'User', readonly=True),
        'work_lines': fields.one2many('asilia.hotel.work.order','sched_id', 'Work Orders', readonly=True),
        'selected_cleaners': fields.many2many('res.users', 'asilia_cleaner_sched_rel', 'sched_id', 'cleaner_id', 'Cleaners'),
        
    }

    
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
    }


asilia_hotel_sched_clean() 

