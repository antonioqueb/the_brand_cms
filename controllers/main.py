import json
from odoo import http
from odoo.http import request

class TheBrandAPI(http.Controller):

    def _fix_url(self, url, base_url):
        """Convierte rutas relativas en absolutas usando web.base.url"""
        if not url:
            return ""
        if url.startswith("http") or url.startswith("//"):
            return url
        
        clean_base = base_url.rstrip('/')
        clean_path = url.lstrip('/')
        return f"{clean_base}/{clean_path}"

    def _traverse_and_fix_urls(self, data, base_url):
        """Recorre el JSON para hidratar URLs de imágenes y videos"""
        if isinstance(data, dict):
            for key, value in data.items():
                # Agregamos video_url a la lista de claves a revisar
                if key in ['image_url', 'src', 'video_url'] and isinstance(value, str):
                    data[key] = self._fix_url(value, base_url)
                elif isinstance(value, (dict, list)):
                    self._traverse_and_fix_urls(value, base_url)
        elif isinstance(data, list):
            for item in data:
                self._traverse_and_fix_urls(item, base_url)
        return data

    @http.route('/api/the-brand/content', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_content(self, **kwargs):
        try:
            # 1. Buscar registro
            page = request.env['the.brand.page'].sudo().search([], limit=1)

            if not page:
                return request.make_response(
                    json.dumps({"error": "No Brand Page configuration found."}),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            # 2. Obtener data cruda
            raw_data = page.get_brand_data()

            # 3. Obtener URL base
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            # 4. Hidratar URLs (Imágenes y Videos)
            final_data = self._traverse_and_fix_urls(raw_data, base_url)

            # 5. Respuesta
            response_data = {"data": final_data}
            
            headers = [
                ('Content-Type', 'application/json'),
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Methods', 'GET, OPTIONS'),
                ('Cache-Control', 'no-store')
            ]
            
            return request.make_response(
                json.dumps(response_data),
                headers=headers
            )

        except Exception as e:
            return request.make_response(
                json.dumps({"error": str(e)}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )