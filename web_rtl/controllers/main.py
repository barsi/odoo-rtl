# -*- coding: utf-8 -*-
from openerp.addons.web.controllers.main import WebClient, http

class FixMomentLocale(WebClient):
    @http.route('/web/webclient/locale/<string:lang>', type='http', auth="none")
    def load_locale(self, lang):
        if lang.startswith('ar_SY'):
            lang = 'ar_SA'
        return super(FixMomentLocale, self).load_locale(lang)
        magic_file_finding = [lang.replace("_",'-').lower(), lang.split('_')[0]]
        if lang.startswith('ar'):
            magic_file_finding = ['ar-sa', 'ar']
        addons_path = http.addons_manifest['web']['addons_path']
        #load momentjs locale
        momentjs_locale_file = False
        momentjs_locale = ""
        for code in magic_file_finding:
            try:
                with open(os.path.join(addons_path, 'web', 'static', 'lib', 'moment', 'locale', code + '.js'), 'r') as f:
                    momentjs_locale = f.read()
                #we found a locale matching so we can exit
                break
            except IOError:
                continue

        #return the content of the locale
        headers = [('Content-Type', 'application/javascript'), ('Cache-Control', 'max-age=%s' % (36000))]
        return request.make_response(momentjs_locale, headers)