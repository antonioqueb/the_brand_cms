from odoo import http
from odoo.http import request

class TheBrandAPI(http.Controller):

    @http.route('/api/the-brand/content', type='json', auth='public', methods=['POST', 'GET'], csrf=False, cors='*')
    def get_content(self, **kwargs):
        """
        API Pública para obtener el contenido CMS.
        No requiere login. Devuelve JSON estructurado para React.
        """
        # Obtenemos el registro principal (ID 1 definido en data.xml)
        # O el primero que encontremos si el ID 1 fue borrado y recreado.
        page = request.env['the.brand.page'].sudo().search([], limit=1)

        if not page:
            return {'error': 'No content found', 'status': 404}

        chapters_data = []
        for ch in page.chapter_ids:
            chapters_data.append({
                'id': ch.id,
                'year': ch.year,
                'title': ch.title,
                'subtitle': ch.subtitle,
                'description': ch.description,
                'media_type': ch.media_type,
                'image_url': ch.get_image_url() if ch.media_type == 'image' else None,
                'video_url': ch.video_url if ch.media_type == 'video' else None,
            })

        return {
            'hero': {
                'number': page.hero_number,
                'label': page.hero_label,
                'title': page.hero_title,
                'subtitle': page.hero_subtitle,
            },
            'manifesto': {
                'title': page.manifesto_title,
                'text': page.manifesto_text,
            },
            'chapters': chapters_data
        }
