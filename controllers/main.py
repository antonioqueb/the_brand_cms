import json
from odoo import http
from odoo.http import request

class TheBrandAPI(http.Controller):

    def _fix_url(self, url, base_url):
        """Convierte rutas relativas en absolutas usando web.base.url"""
        if not url:
            return ""
        if url.startswith("http"):
            return url
        
        clean_base = base_url.rstrip('/')
        clean_path = url.lstrip('/')
        return f"{clean_base}/{clean_path}"

    def _traverse_and_fix_images(self, data, base_url):
        """Recorre el JSON para hidratar URLs de imágenes"""
        if isinstance(data, dict):
            for key, value in data.items():
                if key in ['image_url', 'src'] and isinstance(value, str):
                    data[key] = self._fix_url(value, base_url)
                elif isinstance(value, (dict, list)):
                    self._traverse_and_fix_images(value, base_url)
        elif isinstance(data, list):
            for item in data:
                self._traverse_and_fix_images(item, base_url)
        return data

    @http.route('/api/the-brand/content', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_content(self, **kwargs):
        """
        API Pública HTTP. 
        Reemplaza la versión jsonrpc para evitar el error 'Unsupported Media Type'.
        """
        try:
            # 1. Buscar registro (Singleton)
            page = request.env['the.brand.page'].sudo().search([], limit=1)

            if not page:
                return request.make_response(
                    json.dumps({"error": "No Brand Page configuration found."}),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            # 2. Obtener data cruda del modelo
            raw_data = page.get_brand_data()

            # 3. Obtener URL base para convertir imágenes
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            # 4. Hidratar URLs
            final_data = self._traverse_and_fix_images(raw_data, base_url)

            # 5. Construir respuesta JSON
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