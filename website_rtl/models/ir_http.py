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


from openerp.http import request
from openerp.osv import orm


class ir_http(orm.AbstractModel):
    _inherit = 'ir.http'

    def _dispatch(self):
        if request.httprequest.method != "GET":
            return super(ir_http, self)._dispatch()
        
        if hasattr(request, 'website'):
            langs = request.website.get_languages_dir()
            dirr = langs.get(request.context['lang'], None)
            if dirr is None:
                request.website._get_languages_dir.clear_cache(request.website)
                langs = request.website.get_languages_dir()
                dirr = langs.get(request.context['lang'], None)
                if dirr is None:
                    dirr = 'ltr'
            request.context['lang_dir'] = dirr
            request.lang_dir = dirr
            request.website = request.website.with_context(request.context)
            return super(ir_http, self)._dispatch()

        else:
            resp = super(ir_http, self)._dispatch()
            cook_lang = request.httprequest.cookies.get('website_lang')
            cook_lang = getattr(request, 'lang', False) or (cook_lang or 'en_US')
            ws = request.registry['website'].get_current_website(request.cr, request.uid, context=request.context)
            langs = ws.get_languages_dir()
            request.lang_dir = langs.get(cook_lang)
            request.context['lang_dir'] = request.lang_dir
            return super(ir_http, self)._dispatch()

        resp = super(ir_http, self)._dispatch()

        return resp
