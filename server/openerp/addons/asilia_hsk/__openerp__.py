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
    'name': 'Asilia House Keeping',
    'version': '1.3',
    'author': 'Tarun Behal (PMI)',
    'summary': 'Hotel',
    'description' : """
Manage Hotel
    """,
    'website': 'http://www.linkedin.com/pub/tarun-behal/3b/644/a03',
    'depends': ['base','base_calendar'],
    'category': 'House Keeping System',
    'sequence': 16,
    'demo': [
    ],
    'data': [
        'asilia_hsk_view.xml',
        'asilia_seq_view.xml',
        'wizard/schedule_clean_view.xml',
        'board_asilia_hsk_view.xml',
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
