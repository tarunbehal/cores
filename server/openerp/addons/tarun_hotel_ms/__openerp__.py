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

{
    'name': 'Asylum Seeker Center',
    'version': '1.3',
    'author': 'Tarun Behal',
    'summary': 'Hotel',
    'description' : """
Manage Hotel
    """,
    'website': 'http://www.linkedin.com/pub/tarun-behal/3b/644/a03',
    'depends': ['base','base_calendar','board'],
    'category': 'Hotel Management System',
    'sequence': 16,
    'demo': [
    ],
    'data': [
        'wizard/change_guest_points_view.xml',
        'wizard/change_bed_qty_view.xml',
        'wizard/transfer_guest_view.xml',
        'wizard/cout_guest_view.xml',
        'tarun_hotel_ms_view.xml',
        'tarun_hotel_seq_view.xml',
        'tarun_hotel_guest_partner_view.xml',
        'hms_activity_view.xml',
        'board_tarun_hotel_ms_view.xml',
        'tarun_hotel_stock_view.xml',
        'wizard/tarun_customer_selection_view.xml',
        'tarun_hotel_purchase_view.xml',
        'Large_Label_report.xml',
    ],
    'test': [
#        'test/opening_stock.yml',
#        'test/shipment.yml',
#        'test/stock_report.yml',
    ],
    'installable': True,
    'auto_install': False,
    'css': [ 'static/src/css/stock.css' ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
