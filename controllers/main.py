import json
import base64
import mimetypes  # <--- IMPORTANTE: Para detectar el tipo correcto
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
                if key in ['image_url', 'src', 'video_url'] and isinstance(value, str):
                    data[key] = self._fix_url(value, base_url)
                elif isinstance(value, (dict, list)):
                    self._traverse_and_fix_urls(value, base_url)
        elif isinstance(data, list):
            for item in data:
                self._traverse_and_fix_urls(item, base_url)
        return data

    # -------------------------------------------------------------------------
    # NUEVA RUTA: STREAMING DE VIDEO MEJORADO
    # Acepta el filename en la URL para ayudar al navegador a entender el contenido
    # -------------------------------------------------------------------------
    @http.route([
        '/api/the-brand/video/<int:chapter_id>', 
        '/api/the-brand/video/<int:chapter_id>/<string:filename>'
    ], type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def stream_video(self, chapter_id, filename=None, **kw):
        """
        Endpoint para streaming. El argumento 'filename' es decorativo para la URL
        pero ayuda al navegador a decidir reproducir en lugar de descargar.
        """
        chapter = request.env['the.brand.chapter'].sudo().browse(chapter_id)
        
        if not chapter.exists() or not chapter.video_file:
            return request.make_response("Video not found", status=404)

        try:
            # 1. Decodificar
            file_content = base64.b64decode(chapter.video_file)
            
            # 2. Detectar MimeType real usando librería de Python
            real_filename = chapter.video_filename or 'video.mp4'
            mimetype, _ = mimetypes.guess_type(real_filename)
            
            # Si falla la detección, forzamos mp4 que es lo más común
            if not mimetype:
                mimetype = 'video/mp4'

            # 3. Headers estrictos para reproducción "Inline"
            headers = [
                ('Content-Type', mimetype),
                ('Content-Disposition', f'inline; filename="{real_filename}"'),
                ('Content-Length', len(file_content)),
                ('Accept-Ranges', 'bytes'),  # Indica que aceptamos rangos (aunque enviamos todo)
                ('Access-Control-Allow-Origin', '*'),
            ]

            return request.make_response(file_content, headers)
            
        except Exception as e:
            return request.make_response(f"Error streaming video: {str(e)}", status=500)

    # -------------------------------------------------------------------------
    # RUTA PRINCIPAL (Sin Cambios)
    # -------------------------------------------------------------------------
    @http.route('/api/the-brand/content', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_content(self, **kwargs):
        try:
            page = request.env['the.brand.page'].sudo().search([], limit=1)

            if not page:
                return request.make_response(
                    json.dumps({"error": "No Brand Page configuration found."}),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            raw_data = page.get_brand_data()
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            final_data = self._traverse_and_fix_urls(raw_data, base_url)

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