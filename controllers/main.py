import json
import base64
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
                # Busamos keys de imagen y video
                if key in ['image_url', 'src', 'video_url'] and isinstance(value, str):
                    data[key] = self._fix_url(value, base_url)
                elif isinstance(value, (dict, list)):
                    self._traverse_and_fix_urls(value, base_url)
        elif isinstance(data, list):
            for item in data:
                self._traverse_and_fix_urls(item, base_url)
        return data

    # -------------------------------------------------------------------------
    # NUEVA RUTA: STREAMING DE VIDEO
    # Sirve el archivo con Content-Disposition: inline para evitar la descarga
    # -------------------------------------------------------------------------
    @http.route('/api/the-brand/video/<int:chapter_id>', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def stream_video(self, chapter_id, **kw):
        """
        Endpoint específico para streaming de video desde Binary field.
        """
        # 1. Buscamos el capítulo con permisos de administrador (sudo)
        chapter = request.env['the.brand.chapter'].sudo().browse(chapter_id)
        
        if not chapter.exists() or not chapter.video_file:
            return request.make_response("Video not found", status=404)

        try:
            # 2. Decodificamos el binario (Odoo lo guarda en base64)
            file_content = base64.b64decode(chapter.video_file)
            
            # 3. Determinamos el mimetype basado en la extensión del nombre de archivo
            filename = chapter.video_filename or 'video.mp4'
            mimetype = 'video/mp4' # Default
            
            if filename.lower().endswith('.webm'): 
                mimetype = 'video/webm'
            elif filename.lower().endswith('.mov'): 
                mimetype = 'video/quicktime'
            
            # 4. Configuramos headers para streaming (inline)
            headers = [
                ('Content-Type', mimetype),
                ('Content-Disposition', f'inline; filename="{filename}"'), # <--- ESTO EVITA LA DESCARGA
                ('Content-Length', len(file_content)),
                ('Access-Control-Allow-Origin', '*'),
                ('Cache-Control', 'public, max-age=31536000') # Cache agresivo para mejorar performance
            ]

            return request.make_response(file_content, headers)
            
        except Exception as e:
            return request.make_response(f"Error streaming video: {str(e)}", status=500)

    # -------------------------------------------------------------------------
    # RUTA PRINCIPAL: JSON CONTENT
    # -------------------------------------------------------------------------
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

            # 2. Obtener data cruda del modelo
            # Nota: El modelo ya debe estar devolviendo la URL apuntando a /api/the-brand/video/...
            raw_data = page.get_brand_data()

            # 3. Obtener URL base del sistema
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            # 4. Hidratar URLs (Convertir relativas a absolutas)
            final_data = self._traverse_and_fix_urls(raw_data, base_url)

            # 5. Respuesta JSON
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