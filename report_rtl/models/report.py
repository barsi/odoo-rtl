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


from openerp.osv import orm, osv
from openerp.tools.translate import _
import openerp
from openerp.http import request

import lxml.html
import time
import logging

# remove after issue #1227 been merged
import subprocess
import tempfile
from os import name as OsName
from shutil import rmtree
import base64
_logger = logging.getLogger(__name__)


class Report(orm.Model):

    _inherit = 'report'

    def render(self, cr, uid, ids, template, values=None, context=None):
        if values is None:
            values = {}

        if context is None:
            context = {}
        langs = self.pool.get('res.lang').get_languages_dir(cr, uid, [], context=context)
        values['lang_direction'] = langs.get(context.get('lang', 'en_US'), 'ltr')

        view_obj = self.pool['ir.ui.view']

        def translate_doc(doc_id, model, lang_field, template):
            ctx = context.copy()
            doc = self.pool[model].browse(cr, uid, doc_id, context=ctx)
            qcontext = values.copy()
            # Do not force-translate if we chose to display the report in a specific lang
            if ctx.get('translatable') is True:
                qcontext['o'] = doc
            else:
                # Reach the lang we want to translate the doc into
                ctx['lang'] = eval('doc.%s' % lang_field, {'doc': doc})
                qcontext['o'] = self.pool[model].browse(cr, uid, doc_id, context=ctx)
                qcontext['lang_direction'] = langs.get(ctx['lang'], 'ltr')
                context['lang'] = ctx['lang']
            return view_obj.render(cr, uid, template, qcontext, context=ctx)

        user = self.pool['res.users'].browse(cr, uid, uid)
        website = None
        if request and hasattr(request, 'website'):
            website = request.website
        values.update(
            time=time,
            translate_doc=translate_doc,
            editable=True,  # Will active inherit_branding
            user=user,
            res_company=user.company_id,
            website=website,
            editable_no_editor=True,
        )
        return view_obj.render(cr, uid, template, values, context=context)

    # Remove this after issue #1273 merged with trunk

    def _run_wkhtmltopdf(self, cr, uid, headers, footers, bodies, landscape, paperformat, spec_paperformat_args=None, save_in_attachment=None):
        command = ['wkhtmltopdf']
        command_args = []
        tmp_dir = tempfile.mkdtemp(prefix='report.tmp.')

        # Passing the cookie to wkhtmltopdf in order to resolve internal links.
        try:
            if request:
                command_args.extend(['--cookie', 'session_id', request.session.sid])
        except AttributeError:
            pass

        # Wkhtmltopdf arguments
        command_args.extend(['--quiet'])  # Less verbose error messages
        if paperformat:
            # Convert the paperformat record into arguments
            command_args.extend(self._build_wkhtmltopdf_args(paperformat, spec_paperformat_args))

        # Force the landscape orientation if necessary
        if landscape and '--orientation' in command_args:
            command_args_copy = list(command_args)
            for index, elem in enumerate(command_args_copy):
                if elem == '--orientation':
                    del command_args[index]
                    del command_args[index]
                    command_args.extend(['--orientation', 'landscape'])
        elif landscape and not '--orientation' in command_args:
            command_args.extend(['--orientation', 'landscape'])

        # Execute WKhtmltopdf
        pdfdocuments = []
        todel = True
        if OsName == 'nt':
            todel = False

        for index, reporthtml in enumerate(bodies):
            local_command_args = []
            pdfreport = tempfile.NamedTemporaryFile(delete=todel, suffix='.pdf', prefix='report.tmp.', dir=tmp_dir, mode='w+b')

            # Directly load the document if we already have it
            if save_in_attachment and save_in_attachment['loaded_documents'].get(reporthtml[0]):
                pdfreport.write(save_in_attachment['loaded_documents'].get(reporthtml[0]))
                pdfreport.seek(0)
                pdfdocuments.append(pdfreport)
                continue

            # Wkhtmltopdf handles header/footer as separate pages. Create them if necessary.
            if headers:
                head_file = tempfile.NamedTemporaryFile(delete=todel, suffix='.html', prefix='report.header.tmp.', dir=tmp_dir, mode='w+')
                head_file.write(headers[index])
                head_file.seek(0)
                local_command_args.extend(['--header-html', head_file.name])
            if footers:
                foot_file = tempfile.NamedTemporaryFile(delete=todel, suffix='.html', prefix='report.footer.tmp.', dir=tmp_dir, mode='w+')
                foot_file.write(footers[index])
                foot_file.seek(0)

                foot_file.close()
                local_command_args.extend(['--footer-html', foot_file.name])

            # Body stuff
            content_file = tempfile.NamedTemporaryFile(delete=todel, suffix='.html', prefix='report.body.tmp.', dir=tmp_dir, mode='w+')
            content_file.write(reporthtml[1])
            content_file.seek(0)

            try:
                wkhtmltopdf = command + command_args + local_command_args
                wkhtmltopdf += [content_file.name] + [pdfreport.name]

                process = subprocess.Popen(wkhtmltopdf, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = process.communicate()

                if process.returncode not in [0, 1]:
                    raise osv.except_osv(_(u'Report (PDF)'),
                                         _(u'Wkhtmltopdf failed (error code: %s). '
                                           u'Message: %s') % (unicode(process.returncode), err.decode('utf-8')))

                # Save the pdf in attachment if marked
                if reporthtml[0] is not False and save_in_attachment.get(reporthtml[0]):
                    attachment = {
                        'name': save_in_attachment.get(reporthtml[0]),
                        'datas': base64.encodestring(pdfreport.read()),
                        'datas_fname': save_in_attachment.get(reporthtml[0]),
                        'res_model': save_in_attachment.get('model'),
                        'res_id': reporthtml[0],
                    }
                    self.pool['ir.attachment'].create(cr, uid, attachment)
                    _logger.info(u'The PDF document %s is now saved in the '
                                 u'database' % attachment['name'])

                pdfreport.seek(0)
                pdfdocuments.append(pdfreport)

                content_file.close()

                if headers:
                    head_file.close()
                if footers:
                    foot_file.close()
            except:
                raise

        # Return the entire document
        if len(pdfdocuments) == 1:
            content = pdfdocuments[0].read()
            pdfdocuments[0].close()
            rmtree(tmp_dir, ignore_errors=True)
        else:
            content = self._merge_pdf(pdfdocuments)

        return content



    def _build_wkhtmltopdf_args(self, paperformat, specific_paperformat_args=None):
        command_args = []
        if paperformat.format and paperformat.format != 'custom':
            command_args.extend(['--page-size', paperformat.format])

        if paperformat.page_height and paperformat.page_width and paperformat.format == 'custom':
            command_args.extend(['--page-width', str(paperformat.page_width) + 'mm'])
            command_args.extend(['--page-height', str(paperformat.page_height) + 'mm'])

        if specific_paperformat_args and specific_paperformat_args.get('data-report-margin-top'):
            command_args.extend(['--margin-top', str(specific_paperformat_args['data-report-margin-top'])])
        elif paperformat.margin_top:
            command_args.extend(['--margin-top', str(paperformat.margin_top)])

        if specific_paperformat_args and specific_paperformat_args.get('data-report-dpi'):
            command_args.extend(['--dpi', str(specific_paperformat_args['data-report-dpi'])])
        elif paperformat.dpi:
            if OsName == 'nt' and int(paperformat.dpi) <= 95:
                _logger.info("Generating PDF on Windows platform require DPI >= 96. Using 96 instead.")
                command_args.extend(['--dpi', '96'])
            else:
                command_args.extend(['--dpi', str(paperformat.dpi)])

        if specific_paperformat_args and specific_paperformat_args.get('data-report-header-spacing'):
            command_args.extend(['--header-spacing', str(specific_paperformat_args['data-report-header-spacing'])])
        elif paperformat.header_spacing:
            command_args.extend(['--header-spacing', str(paperformat.header_spacing)])

        if paperformat.margin_left:
            command_args.extend(['--margin-left', str(paperformat.margin_left)])
        if paperformat.margin_bottom:
            command_args.extend(['--margin-bottom', str(paperformat.margin_bottom)])
        if paperformat.margin_right:
            command_args.extend(['--margin-right', str(paperformat.margin_right)])
        if paperformat.orientation:
            command_args.extend(['--orientation', str(paperformat.orientation)])
        if paperformat.header_line:
            command_args.extend(['--header-line'])
        #command_args.extend(['--javascript-delay', '1000'])

        return command_args

