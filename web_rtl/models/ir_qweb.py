# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo RTL support
#    Copyright (C) 2014 Mohammed Barsi.
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


from odoo import models, fields, api
from odoo import SUPERUSER_ID

from odoo.http import request
from odoo.addons.base.ir.ir_qweb.qweb import QWeb


class IrQWeb(models.AbstractModel, QWeb):
    _inherit = 'ir.qweb'

    @api.model
    def render(self, id_or_xml_id, values=None, **options):
        values = values or {}
        context = dict(self.env.context, **options)
        if 'lang_direction' in values:
            return super(IrQWeb, self).render(id_or_xml_id, values=values, **options)
        Language = self.env['res.lang']
        lang = context.get('lang', 'en_US')
        directions = Language.get_languages_dir()
        direction = directions.get(lang, 'ltr')
        values['lang_direction'] = direction
        return super(IrQWeb, self).render(id_or_xml_id, values=values, **options)
