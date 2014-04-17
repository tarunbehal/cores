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
    'name': 'Cores : Office Management',
    'version': '1.3',
    'author': 'Tarun Behal - CoresIT',
    'summary': 'Office',
    'description' : """
Manage Office
    """,
    'website': 'http://www.linkedin.com/pub/tarun-behal/3b/644/a03',
    'depends': ['base'],
    'category': 'Office Management System',
    'sequence': 16,
    'demo': [
    ],
    'data': [
        'cores_office_ms_seq_view.xml',
        'cores_office_ms_view.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'css': [ 'static/src/css/stock.css' ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
