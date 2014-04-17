from openerp.osv import fields, osv
import time
from datetime import datetime
from datetime import timedelta  
from openerp.tools.translate import _





class tarun_hotel_occ(osv.osv):
    _name = "tarun.hotel.occ"
    _description = "Room Occupancy"

    
    def _get_total_spaces(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        occ = self.browse(cr, uid, ids, context=context)  
        room_obj = self.pool.get('tarun.hotel.room')
        room_ids = room_obj.search(cr,uid,[],context=context)
        rooms = room_obj.browse(cr, uid, room_ids, context=context)       
        res = {}
        for o in occ:
            total_space = 0
            for room in rooms: 
                if room.bed_lines:
                    for line in room.bed_lines:               
                        total_space+=(line.bed_qty * line.name.value)
            res[o.id] = total_space
        return res 
         
    def _get_total_baby_spaces(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        
        occ = self.browse(cr, uid, ids, context=context)  
        room_obj = self.pool.get('tarun.hotel.room')
        room_ids = room_obj.search(cr,uid,[],context=context)
        rooms = room_obj.browse(cr, uid, room_ids, context=context)       
        res = {}
        for o in occ:
            total_space = 0
            for room in rooms: 
                if room.bed_lines:
                    for line in room.bed_lines:               
                        if line.name.value==0:
                            total_space+=line.bed_qty
            res[o.id] = total_space
        return res 

    
    def _get_total_occupancy(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        occ = self.browse(cr, uid, ids, context=context)  
        room_obj = self.pool.get('tarun.hotel.room')
        room_ids = room_obj.search(cr,uid,[],context=context)
        rooms = room_obj.browse(cr, uid, room_ids, context=context) 
        order_obj = self.pool.get('tarun.hotel.book.order')      
        res = {}
        for o in occ:
            count = 0
            for room in rooms: 
                order_lines = order_obj.search(cr,uid,[('room_id.id','=',room.id)], context=context)
                for lines in order_obj.browse(cr,uid,order_lines,context=context):
                    time_now = time.strftime('%Y-%m-%d %H:%M:%S')
                    if lines.state=="cin" and lines.check_in_date<time_now:
                        count+=1    
            res[o.id] = count
        return res  

    def _get_total_occupancy_rate(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        occ = self.browse(cr, uid, ids, context=context)  
        room_obj = self.pool.get('tarun.hotel.room')
        room_ids = room_obj.search(cr,uid,[],context=context)
        rooms = room_obj.browse(cr, uid, room_ids, context=context) 
        order_obj = self.pool.get('tarun.hotel.book.order')  
        res ={}
        for occup in occ:
            tot = 0.0
            tot_occ = 0.0
            rate = 0.0
            for room in rooms: 
                order_lines = order_obj.search(cr,uid,[('room_id.id','=',room.id)], context=context)
                for lines in order_obj.browse(cr,uid,order_lines,context=context):
                    time_now = time.strftime('%Y-%m-%d %H:%M:%S')
                    if lines.state=="cin" and lines.check_in_date<time_now:
                        tot_occ+=1    
                if room.bed_lines:
                    for line in room.bed_lines:               
                        tot+=(line.bed_qty * line.name.value)
                
            rate = (tot_occ/tot)*100.00
            res[occup.id] = rate
        return res  
    
    
    
    def _get_total_occupancy_lost(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        occ = self.browse(cr, uid, ids, context=context)  
        room_obj = self.pool.get('tarun.hotel.room')
        room_ids = room_obj.search(cr,uid,[],context=context)
        rooms = room_obj.browse(cr, uid, room_ids, context=context) 
        res ={}
        for occup in occ:
            tot = 0.0
            tot_occ = 0.0
            rate = 0.0
            for room in rooms: 
                if not room.available:
                    tot_occ += room.total_spaces - room.total_occupancy  
                    
                if room.bed_lines:
                    for line in room.bed_lines:               
                        tot+=(line.bed_qty * line.name.value)
                
            rate = (tot_occ/tot)*100.00
            res[occup.id] = rate
        return res  
    

      
    _columns = {
        'name': fields.char('Name', size=128, select=True),
        'total_spaces': fields.function(_get_total_spaces, string='Total Capacity', type='integer'),
        'total_baby_spaces': fields.function(_get_total_baby_spaces, string='Baby Beds', type='integer'),
        'total_occupancy': fields.function(_get_total_occupancy, string='Total Occupancy', type='integer'),
        'occupancy_rate': fields.function(_get_total_occupancy_rate, string='Occupancy Rate (%)', type='float'),
        'occupancy_lost': fields.function(_get_total_occupancy_lost, string='Occupancy Loss Rate (%)', type='float'),
       
    }



    
tarun_hotel_occ() 





class tarun_hotel_room(osv.osv):
    _name = "tarun.hotel.room"
    _description = "Room"

    
    def _get_total_spaces(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        rooms = self.browse(cr, uid, ids, context=context)       
        res = {}
        for room in rooms: 
            total_space = 0 
            if room.bed_lines:
                for line in room.bed_lines:               
                    total_space+=(line.bed_qty * line.name.value)
            res[room.id] = total_space
        return res 
         
    def _get_total_baby_spaces(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        rooms = self.browse(cr, uid, ids, context=context)       
        res = {}
        for room in rooms: 
            total_space = 0 
            if room.bed_lines:
                for line in room.bed_lines:
                    if line.name.value==0:
                        total_space+=line.bed_qty
            res[room.id] = total_space
        return res  
    
    def _get_total_occupancy(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        rooms = self.browse(cr, uid, ids, context=context) 
        order_obj = self.pool.get('tarun.hotel.book.order')      
        res = {}
        for room in rooms: 
            count = 0
            order_lines = order_obj.search(cr,uid,[('room_id.id','=',room.id)], context=context)
            for lines in order_obj.browse(cr,uid,order_lines,context=context):
                time_now = time.strftime('%Y-%m-%d %H:%M:%S')
                if lines.state=="cin" and lines.check_in_date<time_now:
                    count+=1    
            res[room.id] = count
        return res  

    def _get_total_occupancy_rate(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        rooms = self.browse(cr, uid, ids, context=context)       
        res = {}
        for room in rooms: 
            rate = 0.0
            try:
                rate = float(room.total_occupancy)/float(room.total_spaces)*100.00
            except:
                rate = 0.0
            res[room.id] = rate
        return res  
    
    def _get_availability(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        rooms = self.browse(cr, uid, ids, context=context) 
        order_obj = self.pool.get('tarun.hotel.book.order')      
        res = {}
        for room in rooms:
            avail = True          
            total_space = 0 
            occ_space = 0           
            if room.bed_lines:
                for bed_line in room.bed_lines:               
                    total_space+=(bed_line.bed_qty * bed_line.name.value)
            order_lines = order_obj.search(cr,uid,[('room_id.id','=',room.id)], context=context)
            for lines in order_obj.browse(cr,uid,order_lines,context=context):
                time_now = time.strftime('%Y-%m-%d %H:%M:%S')
                # date less than current time
                if lines.state=="cin" and lines.check_in_date<time_now:
                    if lines.guest_type.name in ["Family","Sick"]:
                        avail = False
                        break
                    else:
                        occ_space+=1
            if total_space-occ_space<1:
                avail=False
                            
            res[room.id] = avail
        return res  
    
    def _get_male_availability(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        rooms = self.browse(cr, uid, ids, context=context) 
        order_obj = self.pool.get('tarun.hotel.book.order')      
        res = {}
        for room in rooms:
            avail = True          
            total_space = 0 
            occ_space = 0           
            if room.bed_lines:
                for bed_line in room.bed_lines:               
                    total_space+=(bed_line.bed_qty * bed_line.name.value)
            order_lines = order_obj.search(cr,uid,[('room_id.id','=',room.id)], context=context)
            for lines in order_obj.browse(cr,uid,order_lines,context=context):
                time_now = time.strftime('%Y-%m-%d %H:%M:%S')
                # date less than current time
                if lines.state=="cin" and lines.check_in_date<time_now:
                    if lines.guest_type.name in ["Family","Sick","Single"] and lines.gender=="f":
                        avail = False
                        break
                    else:
                        occ_space+=1
            if total_space-occ_space<1:
                avail=False
                            
            res[room.id] = avail
        return res  
    
    
    def _get_family_availability(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        rooms = self.browse(cr, uid, ids, context=context) 
        order_obj = self.pool.get('tarun.hotel.book.order')      
        res = {}
        for room in rooms:
            avail = False          
            total_space = 0 
            occ_space = 0           
            if room.bed_lines:
                for bed_line in room.bed_lines:               
                    total_space+=(bed_line.bed_qty * bed_line.name.value)
                    
                    
            order_lines = order_obj.search(cr,uid,[('room_id.id','=',room.id)], context=context)
            for lines in order_obj.browse(cr,uid,order_lines,context=context):
                time_now = time.strftime('%Y-%m-%d %H:%M:%S')
                # date less than current time
                if lines.state=="cin" and lines.check_in_date<time_now:
                    if lines.guest_type.name in ["Family"]:
                        avail = True
                        occ_space+=1
            if total_space-occ_space<1:
                avail=False
                            
            res[room.id] = avail
        return res  

    def _compute_lines(self, cr, uid, ids, name, args, context=None):
        result = {}
        order_obj=self.pool.get('tarun.hotel.book.order')
        for room in self.browse(cr, uid, ids, context=context):
            orders = []
            orders = order_obj.search(cr,uid, [['state', '=', 'cin'], ['room_id_view', 'ilike', room.name]], context=context)
            result[room.id] = orders
        return result

    
      
    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True),
        'type_id': fields.many2one('tarun.hotel.room.type', 'Room Type', required=True, select=True),
        'total_spaces': fields.function(_get_total_spaces, string='Total Capacity', type='integer'),
        'total_baby_spaces': fields.function(_get_total_baby_spaces, string='Baby Beds', type='integer'),
        'bed_lines': fields.one2many('tarun.hotel.room.bed', 'room_id', 'Beds'),
        'total_occupancy': fields.function(_get_total_occupancy, string='Total Occupancy', type='integer'),
        'occupancy_rate': fields.function(_get_total_occupancy_rate, string='Occupancy Rate', type='float'),
        'available': fields.function(_get_availability, string='Available', type='boolean', help="A Room will be show Available if it has no Sick or Family Type Guest and has space available"),
        'male_available': fields.function(_get_male_availability, string='Male Check', type='boolean'),
        'family_available': fields.function(_get_family_availability, string='Family Check', type='boolean'),
        'cur_order' : fields.function(_compute_lines, relation='tarun.hotel.book.order', type="many2many", string='Current Reservations'),
       
       
    }

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            av_space=0
            av_space = record.total_spaces-record.total_occupancy
            name = record.name+" ("+str(av_space)+")"
            res.append((record.id, name))
        return res

    
tarun_hotel_room() 

class tarun_hotel_room_bed(osv.osv):
    _name = "tarun.hotel.room.bed"
    _description = "Room&Bed"

        
    _columns = {
        'room_id': fields.many2one('tarun.hotel.room', 'Room Reference', required=True, ondelete='cascade', select=True),  
        'name': fields.many2one('tarun.hotel.bed', 'Bed Type', required=True, select=True),
        'bed_qty': fields.integer('Quantity'), 
    }
    
tarun_hotel_room_bed()


class tarun_hotel_bed(osv.osv):
    _name = "tarun.hotel.bed"
    _description = "Bed"

    def _get_available_stock(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        beds = self.browse(cr, uid, ids, context=context)
        room_lines_obj = self.pool.get('tarun.hotel.room.bed')        
        res = {}
        for bed in beds: 
            used_stock = 0 
            room_lines = room_lines_obj.search(cr,uid, [('name.id','=',bed.id)], context=context)
            if room_lines:
                for line in room_lines_obj.browse(cr,uid,room_lines,context=context):
                    used_stock+=line.bed_qty 
            res[bed.id] = bed.total_stock - used_stock
        return res  
    
    
    
    def _get_used_stock(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        beds = self.browse(cr, uid, ids, context=context)
        room_lines_obj = self.pool.get('tarun.hotel.room.bed')        
        res = {}
        for bed in beds: 
            used_stock = 0 
            room_lines = room_lines_obj.search(cr,uid, [('name.id','=',bed.id)], context=context)
            if room_lines:
                for line in room_lines_obj.browse(cr,uid,room_lines,context=context):
                    used_stock+=line.bed_qty 
            res[bed.id] = used_stock
        return res  
    

        
    _columns = {
        'name': fields.char('Type', size=128, required=True, select=True),
        'value': fields.integer('Capacity',help="1 for Single, 2 for Double. This will be used for counting available Spaces in a room"),
        'total_stock': fields.integer('Total Stock', help="Total Stock"),
        'available_stock': fields.function(_get_available_stock, string='Available Stock', type='integer'),
        'used_stock': fields.function(_get_used_stock, string='Used Stock', type='integer'),
    }
    

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name+" "+str(record.available_stock)
            res.append((record.id, name))
        return res



tarun_hotel_bed() 


class tarun_hotel_room_type(osv.osv):
    _name = "tarun.hotel.room.type"
    _description = "Room Type"

        
    _columns = {
        'name': fields.char('Type', size=128, required=True, select=True),
    }
    


tarun_hotel_room_type() 


class tarun_hotel_guest_type(osv.osv):
    _name = "tarun.hotel.guest.type"
    _description = "Guest Type"

        
    _columns = {
        'name': fields.char('Type', size=128, required=True, select=True),
    }
    


tarun_hotel_guest_type() 



class tarun_hotel_book_order(osv.osv):
    _name = "tarun.hotel.book.order"
    _description = "Book Order"

    def button_check_out(self, cr, uid, ids, context=None):
        
        for do in self.browse(cr, uid, ids, context=context):
            time_now = time.strftime('%Y-%m-%d %H:%M:%S')
            date_now = time.strftime('%Y-%m-%d')
            if do.guest_id:
                self.pool.get('tarun.hotel.guest.partner').write(cr,uid,do.guest_id.id,{'available':False},context=context)            
            return self.write(cr,uid,ids,{'state': 'cout','check_out_date': time_now,'check_out_date_view': date_now},context=context)


    def _get_auto_name(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        all_orders=self.search(cr,uid,[],context=context)
        orders = self.browse(cr, uid, all_orders, context=context)        
        res = {}
        for order in orders: 
            name =""
            name = order.first_name + " " + order.last_name +" ["+ order.guest_ref +"]"
            res[order.id] = name
        return res  
    
    
    def _get_auto_room_id_view(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        all_orders=self.search(cr,uid,[],context=context)
        orders = self.browse(cr, uid, all_orders, context=context)        
        res = {}
        for order in orders: 
            name =""
            av_space = 0
            av_space = order.room_id.total_spaces-order.room_id.total_occupancy
            if order.state=="cin":
                name = order.room_id.name + " ( "+ str(av_space)+" ) "+ order.guest_type.name
                if order.guest_type.name == "Single":
                    if order.gender == "m":
                        name+= " M"
                    else:
                        name+= " F"
            else:
                name = order.room_id.name + " ( "+ str(av_space)+" )"
            res[order.id] = name
        return res  
    
    def _tarun_hms_cleaner(self, cr, uid, ids, context=None):
        """
        @return: Dictionary of values.
        """
        date_3 = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S')
        orders = self.search(cr,uid,[('state','=','cout'),('check_in_date','<',date_3)])
        print orders
        #cr.execute("""DELETE FROM tarun_hotel_book_order WHERE id in %s""", (tuple(orders),))
        return True
    
    _columns = {
        'name':fields.function(_get_auto_name, string='Name', type='char',store=True),
        'guest_id': fields.many2one('tarun.hotel.guest.partner', 'Guest Name', select=True),
        'guest_ref': fields.char('Guest Ref.', size=128, required=True, select=True, readonly=True, states={'cin': [('readonly', False)]}),
        'first_name': fields.char('First Name', size=128, required=True, select=True, readonly=True, states={'cin': [('readonly', False)]}),
        'last_name': fields.char('Last Name', size=128, required=True, select=True, readonly=True, states={'cin': [('readonly', False)]}),
        'country_id': fields.many2one('res.country', 'Country', readonly=True, states={'cin': [('readonly', False)]}),
        'gender': fields.selection([('m', 'Male'), ('f', 'Female')], 'Gender', readonly=True, states={'cin': [('readonly', False)]}),
        'check_in_date': fields.datetime('Check - In', help="Check-in Time.", required=True, select=True, readonly=True, states={'cin': [('readonly', False)]}),
        'check_in_date_view': fields.date('Check - In', help="Check-in Date.", required=True,),
        'check_out_date_view': fields.date('Check - Out', help="Check-out Date.", readonly=True),
        'check_out_date': fields.datetime('Check - Out', help="Check-out Time.", select=True),
        'user_id': fields.many2one('res.users', 'User', readonly=True),
        'guest_type': fields.many2one('tarun.hotel.guest.type', 'Guest Type', select=True, readonly=True, states={'cin': [('readonly', False)]}),
        'state': fields.selection([
            ('cin', 'Check IN'),
            ('cout', 'Check OUT'),
            ], 'Status', readonly=True, select=True),    
        'room_id': fields.many2one('tarun.hotel.room', 'Room Number', required=True, ondelete='cascade', select=True, readonly=True, states={'cin': [('readonly', False)]}),
        'room_id_view':fields.function(_get_auto_room_id_view, string='Room Number', type='char',store=True),
        
    }
    
    _defaults = {
        'check_in_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'check_in_date_view': lambda *a: (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        'state': 'cin',
        'user_id': lambda obj, cr, uid, context: uid,
    }

    
    
    def create(self, cr, uid, vals, context=None):
            cur_date = vals.get('check_in_date_view')
            first_name=vals.get('first_name')
            last_name=vals.get('last_name')
            gender=vals.get('gender')
            guest_ref=vals.get('guest_ref')
            country_id=vals.get('country_id')
            dedicated_salesman=uid
            val={
                'name': first_name,
                'last_name': last_name,
                'gender': gender,
                'guest_ref': guest_ref,
                'country_id': country_id,
                'user_id': dedicated_salesman,
                'cin_date':cur_date,
                'available':True}            
            vals['guest_id'] = self.pool.get('tarun.hotel.guest.partner').create(cr, uid, val, context=context)
            dt_str = str(cur_date)+" 00:00:00"
            vals['check_in_date']=dt_str
            vals['check_in_date_view']=cur_date
            vals['user_id']=uid              
            self.pool.get('tarun.hotel.guest.points').create(cr,uid,{'guest_id':vals['guest_id'],
                                                                     'name':'Check-In Points',
                                                                     'qty':3675,
                                                                     'date':dt_str,
                                                                     },context=context) 
            print "date test", cur_date , dt_str
            return super(tarun_hotel_book_order, self).create(cr, uid, vals, context=context)


    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        time_now = time.strftime('%Y-%m-%d %H:%M:%S')   
        default.update({
            'guest_id':None,
            'state': 'cin',
            'check_in_date': time_now,
            'check_out_date': None,
        })
        return super(tarun_hotel_book_order, self).copy(cr, uid, id, default, context=context)
    
    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        if not part:
            return {'value': {'first_name': False,'last_name': False,'gender': False, 'guest_ref': False,  'country_id': False}}

        part = self.pool.get('tarun.hotel.guest.partner').browse(cr, uid, part, context=context)
        first_name = part.name or False
        last_name = part.last_name or False
        gender = part.gender or False
        guest_ref = part.guest_ref or False
        country_id = part.country_id and part.country_id.id or False
        dedicated_salesman = part.user_id and part.user_id.id or uid
        val = {
            'first_name': first_name,
            'last_name': last_name,
            'gender': gender,
            'guest_ref': guest_ref,
            'country_id': country_id,
            'user_id': dedicated_salesman,
        }
        return {'value': val}


    def onchange_room_id(self, cr, uid, ids, value, context=None):
        """ Otherwise a warning is thrown.            
        """
        res = {'value': {}}
        room_list=[]
        if not value:
            return res
        else:
            room_list.append(value)
            res.update(self.check_room_status(cr, uid, room_list, context=context))
            return res
    

    def gender_change(self, cr, uid, ids, gender, context=None):
        if not gender:
            return {'value': {'gender': False, 'guest_type': False,  'room_id': False}}
        else:
            return {'value': {'guest_type': False,  'room_id': False}}
    

    def guest_type_change(self, cr, uid, ids, gender, guest_type, context=None):
        """ Otherwise a warning is thrown.            
        """
        res = {'value': {}}
        room_list=[]
        if not gender:
            warning_msg = _('Please specify Gender..!!!')
            return {'warning': {
                    'title': _('Warning'),
                    'message': warning_msg,
                    }
                }
        if not guest_type:
            warning_msg = _('Please specify Guest Type..!!!')
            return {'warning': {
                    'title': _('Warning'),
                    'message': warning_msg,
                    }
                }
        
        rooms = self.pool.get('tarun.hotel.room').search(cr,uid,[],context=context)
        dm_room = []
        gt_name = self.pool.get('tarun.hotel.guest.type').browse(cr,uid,guest_type,context=context)
        for room in self.pool.get('tarun.hotel.room').browse(cr,uid,rooms,context=context):
                if gender=="f" and gt_name.name=="Single":                    
                    if (room.available and not room.male_available) or (room.total_occupancy==0 and room.total_spaces>0):
                        dm_room.append(room.id)
                elif gender=="m" and gt_name.name=="Single":
                    if room.available and room.male_available:
                        dm_room.append(room.id)
                elif gt_name.name == "Family":
                    if (room.available and room.total_occupancy==0) or (room.family_available and room.occupancy_rate<100.00):
                        dm_room.append(room.id)    
                else:
                    if room.available and room.total_occupancy==0 and room.total_spaces>0:
                        dm_room.append(room.id)
        set_dm = "[('id','in',["+','.join(map(str, dm_room))+"])]"                
        domain = {'room_id': set_dm}
        
        return {'domain': domain}
    

    def check_room_status(self, cr, uid, room_ids, context=None):
        """ .
            Otherwise throw a warning. """
        room_list=[]
        for room in self.pool.get('tarun.hotel.room').browse(cr, uid, room_ids, context=context):
            if not room.available:
                room_list.append(room)
        if not room_list:
            return {}
        warning_msg = _('Room %s has a Family. Are you sure you want to keep in this Room!!') % (room.name)
        return {'warning': {
                    'title': _('Room Confirmation'),
                    'message': warning_msg,
                    }
                }


tarun_hotel_book_order() 
