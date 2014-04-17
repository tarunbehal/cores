from openerp.osv import fields, osv
import time
import re
from datetime import datetime
from datetime import timedelta  
from openerp.tools.translate import _


class tarun_hotel_product_category(osv.osv):
    _name = "tarun.hotel.product.category"
    _description = "Products Category"

        
    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True),
    }
    


tarun_hotel_product_category() 


class tarun_hotel_product(osv.osv):
    _name = "tarun.hotel.product"
    _description = "Products"

    
    def _get_total_stock(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        prod = self.browse(cr, uid, ids, context=context)  
        trans_obj = self.pool.get('tarun.hotel.stock.transfer')
        res = {}
        for o in prod:
            ip = 0.0
            op = 0.0
            trans_op = trans_obj.search(cr,uid,[('loc_des_id.name','ilike','stock'),('product_id.id','=',o.id),('state','=','done')]) 
            trans_ip = trans_obj.search(cr,uid,[('loc_id.name','ilike','stock'),('product_id.id','=',o.id),('state','=','done')])   
            op_list = trans_obj.read(cr,uid,trans_op,['qty']) 
            ip_list = trans_obj.read(cr,uid,trans_ip,['qty'])
            if op_list:
                for i in op_list:
                    ip+=i['qty']
            if ip_list:
                for i in ip_list:
                    op+=i['qty']
            res[o.id] = ip-op
        return res  


    def _get_alert_bol(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        prods = self.browse(cr, uid, ids, context=context)   
        res = {}
        for prod in prods:
            avail = False      
            if prod.stock_alert>prod.total_stock:
                avail=True
            res[prod.id] = avail
        return res  

    def _get_alert(self, cr, uid, ids, field_name, arg, context=None):
        """
        @return: Dictionary of values.
        """
        prods = self.browse(cr, uid, ids, context=context)        
        res = {}
        for prod in prods: 
            name =""
            if prod.stock_alert>prod.total_stock:
                name = "!!!"
            res[prod.id] = name
        return res  
    
        
    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True),
        'default_code' : fields.char('Ref. Number', size=64, select=True),
        'unit': fields.float('Unit'),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure ', required=True),
        'value': fields.float('Value'),
        'product_category': fields.many2one('tarun.hotel.product.category', 'Category', required=True),
        'stock_alert': fields.integer('Stock Alert'),
        'active': fields.boolean('Active', help="If unchecked, it will allow you to hide the product without removing it."),
        'total_stock': fields.function(_get_total_stock, string='Current Stock', type='float', digits=(14,3)),
        'alert':fields.function(_get_alert, string='Alert', type='char'),
        'alert_bol': fields.function(_get_alert_bol, string='Alert', type='boolean'),       
        
    }
    _defaults = {
        'active': lambda *a: 1,
    }


    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.default_code+" "+record.name+" "+str(record.unit)+record.product_uom.name
            res.append((record.id, name))
        return res

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            ids = self.search(cr, user, [('default_code','=',name)]+ args, limit=limit, context=context)
            if not ids:
                ids = set()
                ids.update(self.search(cr, user, args + [('default_code',operator,name)], limit=limit, context=context))
                if not limit or len(ids) < limit:
                    ids.update(self.search(cr, user, args + [('name',operator,name)], limit=(limit and (limit-len(ids)) or False) , context=context))
                ids = list(ids)
            if not ids:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(cr, user, [('default_code','=', res.group(2))] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        fin = []
        if context.get('positive_only',False):
	    for prod in self.browse(cr, user, ids, context=context):
                if prod.total_stock>0.0:
	            fin.append(prod.id)
        if fin:
            result = self.name_get(cr, user, fin, context=context)
        else:
            result = self.name_get(cr, user, ids, context=context)
        return result

   
    def unlink(self, cr, uid, ids, context=None):
        for product in self.browse(cr, uid, ids, context=context):
            raise osv.except_osv(_('Warning!'), _("To delete a product un-check the active field on product form!!"))
        return True


tarun_hotel_product() 


class tarun_hotel_stock_location(osv.osv):
    _name = "tarun.hotel.stock.location"
    _description = "Stock Location"
    
    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True),  
        'description': fields.text('Description'),    
    }
    
tarun_hotel_stock_location() 


class tarun_hotel_stock_transfer(osv.osv):
    _name = "tarun.hotel.stock.transfer"
    _description = "Stock Transfer"


    def button_done(self, cr, uid, ids, context=None):
        
        for do in self.browse(cr, uid, ids, context=context):
            time_now = time.strftime('%Y-%m-%d %H:%M:%S')
            return self.write(cr,uid,ids,{'state': 'done','date': time_now,},context=context)

    def button_cancel(self, cr, uid, ids, context=None):
        
        for do in self.browse(cr, uid, ids, context=context):
            time_now = time.strftime('%Y-%m-%d %H:%M:%S')
            return self.write(cr,uid,ids,{'state': 'cancel','date': time_now,},context=context)
        
    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True),
        'qty': fields.float('Quantity', digits=(14,3)),
        'product_id': fields.many2one('tarun.hotel.product', 'Product', required=True),
        'loc_id': fields.many2one('tarun.hotel.stock.location', 'Source', required=True),
        'loc_des_id': fields.many2one('tarun.hotel.stock.location', 'Destination', required=True),
        'date': fields.datetime('Date', help="Date.", required=True, select=True, readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('done', 'Done'),
            ('cancel', 'Cancel'),
            ], 'Status', readonly=True, select=True),    
        'user_id': fields.many2one('res.users', 'User', readonly=True),
    }

    
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
    }


tarun_hotel_stock_transfer() 


class tarun_hotel_update_stock(osv.osv):
    _name = "tarun.hotel.update.stock"
    _description = "Stock Update"

    def action_view_new_inv(self, cr, uid, ids, context=None):        
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        inv_ids =[]
        result = mod_obj.get_object_reference(cr, uid, 'tarun_hotel_ms', 'action_tarun_hotel_update_stock_form')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        test_id = self.create(cr,uid,{'name':'Today Inv','date':time.strftime('%Y-%m-%d %H:%M:%S')})
        print test_id
        prod_ids= self.pool.get('tarun.hotel.product').search(cr,uid,[])
        for prod in prod_ids:
            self.pool.get('tarun.hotel.update.stock.lines').create(cr,uid,{'inv_id':test_id,'product_id':prod})
        inv_ids.append(test_id)
        res = mod_obj.get_object_reference(cr, uid, 'tarun_hotel_ms', 'tarun_hotel_update_stock_form')
        result['views'] = [(res and res[1] or False, 'form')]
        result['res_id'] = inv_ids and inv_ids[0] or False
        result['target'] = 'inline'
        return result
     


    def button_done(self, cr, uid, ids, context=None):
        
        for do in self.browse(cr, uid, ids, context=context):
            time_now = time.strftime('%Y-%m-%d %H:%M:%S')
            try:
                stock = self.pool.get('tarun.hotel.stock.location').search(cr,uid,[('name','ilike','stock')])
                purchase = self.pool.get('tarun.hotel.stock.location').search(cr,uid,[('name','ilike','purchase')])
            except:                
                raise osv.except_osv(_('Location Error!'), _('Please create location name "Stock" and "Purchase"!'))
            for lines in do.inv_lines:
                if lines.qty and lines.qty>0.0:
                    self.pool.get('tarun.hotel.stock.transfer').create(cr,uid,{'name':do.name,
                                                                               'product_id':lines.product_id.id,
                                                                               'qty':lines.qty,
                                                                               'loc_id':purchase[0],
                                                                               'loc_des_id':stock[0],
                                                                               'date':time_now,
                                                                               'user_id':uid,
                                                                               'state':'done'})
                    
            self.write(cr,uid,ids,{'state': 'done','date': time_now,},context=context)
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'tarun_hotel_ms', 'action_tarun_hotel_product')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        inv_ids = self.pool.get('tarun.hotel.product').search(cr,uid,[])
        result['domain'] = "[('id','in',["+','.join(map(str, inv_ids))+"])]"
        return result

    def button_cancel(self, cr, uid, ids, context=None):
        
        for do in self.browse(cr, uid, ids, context=context):
            time_now = time.strftime('%Y-%m-%d %H:%M:%S')
            return self.write(cr,uid,ids,{'state': 'cancel','date': time_now,},context=context)
        
    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True),
        'date': fields.datetime('Date', help="Date.", required=True, select=True, readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('done', 'Done'),
            ('cancel', 'Cancel'),
            ], 'Status', readonly=True, select=True),    
        'user_id': fields.many2one('res.users', 'User', readonly=True),
        'inv_lines': fields.one2many('tarun.hotel.update.stock.lines','inv_id', 'Stock Lines', readonly=True, states={'draft': [('readonly', False)]}),
    }

    
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
    }


tarun_hotel_update_stock() 

class tarun_hotel_update_stock_lines(osv.osv):
    _name = "tarun.hotel.update.stock.lines"
    _description = "Stock Update Lines"
       
    _columns = {
        'inv_id': fields.many2one('tarun.hotel.update.stock', 'INV'),
        'product_id': fields.many2one('tarun.hotel.product', 'Product', required=True),
        'cur_qty': fields.related('product_id','total_stock',type='float', digits=(14,3),string='Current Stock',
            readonly=True, store=True),
        'qty': fields.float('Quantity', digits=(14,3)),
    }


tarun_hotel_update_stock_lines() 


