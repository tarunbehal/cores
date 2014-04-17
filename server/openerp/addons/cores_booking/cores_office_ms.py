from openerp.osv import fields, osv
from datetime import datetime
from datetime import timedelta 
from openerp import tools 
from openerp.tools.translate import _

class cores_office_type(osv.osv):
    _name = "cores.office.type"
    _description = "Cores Office Type"
        
    _columns = {
        'name': fields.char('Type', size=128, required=True, select=True),
    }

cores_office_type() 

class cores_office_workstation(osv.osv):
    _name = "cores.office.workstation"
    _description = "Cores Office Workstation"
        
    _columns = {
        'name': fields.char('Type', size=128, required=True, select=True),
    }

cores_office_workstation() 

class cores_office(osv.osv):
    _name = "cores.office"
    _description = "Cores Offices"



    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)
      
    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True),
        'type_id': fields.many2one('cores.office.type', 'Type', required=True, select=True),
        'workstation_id': fields.many2one('cores.office.workstation', 'Workstation', select=True),
        'size': fields.integer('Size', required=True, select=True),
        'description': fields.text('Notes'),
        'options': fields.one2many('cores.office.options', 'office_id', 'Additional Options (if any)'),
        'pricing': fields.one2many('cores.office.pricing', 'office_id', 'Pricing'),
        'active': fields.boolean('Active', help="If unchecked, it will allow you to hide the office without removing it."),
        'image': fields.binary("Image",
            help="This field holds the image used as image for the office, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized image", type="binary", multi="_get_image",
            store={
                'cores.office': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized image of the office. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved, "\
                 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Small-sized image", type="binary", multi="_get_image",
            store={
                'cores.office': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized image of the office. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
    }

    _defaults ={
        'active':1,
                 }

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.type_id.name + ' - ' + record.name
            res.append((record.id, name))
        return res

    
cores_office() 



class cores_office_options(osv.osv):
    _name = "cores.office.options"
    _description = "Cores Options"


    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True),
        'office_id': fields.many2one('cores.office', 'Office', select=True),
        'description': fields.text('Description'),
    }

    _sql_constraints = [
        ('office_options_uniq', 'unique (name,office_id)', 'Options must be unique per office !')
    ]

cores_office_options() 

class cores_office_pricing(osv.osv):
    _name = "cores.office.pricing"
    _description = "Cores Pricing"

    _columns = {
        'office_id': fields.many2one('cores.office', 'Office', select=True),
        'name': fields.selection([
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ], 'Type', required=True, select=True),
        'price': fields.float('Price'),
    }


    _sql_constraints = [
        ('office_pricings_uniq', 'unique (name,office_id)', 'Options must be unique per office !')
    ]

cores_office_pricing() 

class cores_book_order(osv.osv):
    _name = "cores.book.order"
    _description = "Cores Book Order"


    def button_issue(self, cr, uid, ids, context=None):
        return self.write(cr,uid,ids,{'state': 'issue'},context=context)
     
    def button_done(self, cr, uid, ids, context=None):
        return self.write(cr,uid,ids,{'state': 'done'},context=context)
    
    _columns = {
        'name':fields.char('Name', size=128, required=True, select=True),
        'partner_id': fields.many2one('res.partner', 'Customer', select=True),
        'order_date': fields.date('Check - In', help="Order.", required=True, select=True, readonly=True, states={'draft': [('readonly', False)]}),
        'user_id': fields.many2one('res.users', 'User', readonly=True),
        'order_lines': fields.one2many('cores.book.order.lines', 'order_id', 'Order lines', readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('issue', 'Issued'),
            ('done', 'Done'),
            ], 'Status', readonly=True, select=True),    
        
    }


    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cores.book.order') or '/'
        return super(cores_book_order, self).create(cr, uid, vals, context=context)
    
    _defaults = {
        'name': lambda obj, cr, uid, context: '/',
        'order_date': lambda *a: datetime.now().strftime("%Y-%m-%d"),
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
    }


cores_book_order() 

class cores_book_order_lines(osv.osv):
    _name = "cores.book.order.lines"
    _description = "Cores Book Order Lines"

    def onchange_office_id(self, cr, uid, ids, office_id, pricing, units, context=None):
        context = context or {}
        value = {'pricing': pricing,
                 'price': 0.0,
                 'units': units}
        warning = {
                       'title': _('Configuration Error!'),
                       'message' : 'Please specify proper pricing for Office Type'
                    }
        if not office_id:
            return {'value': value}
            
        office = self.pool.get('cores.office').browse(cr, uid, office_id, context=context)
        for pp in office.pricing:
            if pp.name == pricing:
                return {'value': {'pricing': pricing,
                                  'units': units,
                                  'price': units*pp.price,
                                  'office_id':office_id}}
        
        return {'warning': warning, 'value': value}

   
    _columns = {
        'order_id': fields.many2one('cores.book.order', 'Order ID', select=True),
        'office_id': fields.many2one('cores.office', 'Office', required=True, select=True),
        'start_date': fields.datetime('Start Date', select=True, required=True),
        'end_date': fields.datetime('End Date', required=True, select=True),
        'pricing': fields.selection([
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ], 'Pricing', required=True, select=True),
        'units': fields.float('Total Units', required=True),
        'price': fields.float('Total Price'),
    }
    
    _defaults = {
        'start_date': lambda *a: (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
        'end_date': lambda *b: (datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
        'pricing':'hourly',
        'units':1.0,
        'price':0.0,
    }


cores_book_order_lines() 
