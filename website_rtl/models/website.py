# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo RTL support
#    Copyright (C) 2016 Mohammed Barsi.
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
from odoo.http import request

import odoo


class Website(models.Model):
    _inherit = 'website'

    @api.model
    @odoo.tools.ormcache()
    def _get_languages_dir(self):
        website = self
        return dict([(lg.code, lg.direction) for lg in website.language_ids])

    @api.multi
    def get_languages_dir(self):
        return self._get_languages_dir()

    @api.multi
    def write(self, vals):
        self._get_languages_dir.clear_cache(self)
        return super(Website, self).write(vals)
