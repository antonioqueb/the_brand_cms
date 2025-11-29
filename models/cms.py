from odoo import models, fields, api
from odoo.exceptions import UserError

class TheBrandPage(models.Model):
    _name = 'the.brand.page'
    _description = 'Configuración Página The Brand'
    _rec_name = 'hero_label'

    # --- Sección Hero ---
    hero_number = fields.Char(string="Número Hero", default="01")
    hero_label = fields.Char(string="Etiqueta Hero", default="Philosophy")
    hero_title = fields.Html(string="Título Principal", help="Usa <br> para saltos de linea")
    hero_subtitle = fields.Char(string="Subtítulo Itálico")

    # --- Sección Manifiesto ---
    manifesto_title = fields.Text(string="Título Manifiesto")
    manifesto_text = fields.Text(string="Texto Manifiesto")

    # --- Capítulos de Historia ---
    chapter_ids = fields.One2many('the.brand.chapter', 'page_id', string="Capítulos de Historia")

    @api.model_create_multi
    def create(self, vals_list):
        """Prevenir crear más de una configuración de Brand"""
        if self.search_count([]) >= 1:
            raise UserError('Ya existe una configuración para The Brand Page. Por favor edita la existente.')
        return super().create(vals_list)

    def get_brand_data(self):
        """Retorna la estructura completa para la API"""
        self.ensure_one()
        
        chapters_data = []
        for ch in self.chapter_ids:
            chapters_data.append({
                'id': ch.id,
                'year': ch.year or '',
                'title': ch.title or '',
                'subtitle': ch.subtitle or '',
                'description': ch.description or '',
                'media_type': ch.media_type,
                'image_url': ch.get_image_url(),
                'video_url': ch.video_url or '',
            })

        return {
            'hero': {
                'number': self.hero_number or '',
                'label': self.hero_label or '',
                'title': self.hero_title or '',
                'subtitle': self.hero_subtitle or '',
            },
            'manifesto': {
                'title': self.manifesto_title or '',
                'text': self.manifesto_text or '',
            },
            'chapters': chapters_data
        }

class TheBrandChapter(models.Model):
    _name = 'the.brand.chapter'
    _description = 'Capítulo de Historia'
    _order = 'sequence, id'

    page_id = fields.Many2one('the.brand.page', string="Página Padre")
    sequence = fields.Integer(string="Orden", default=10)

    year = fields.Char(string="Año / Época", required=True)
    title = fields.Char(string="Título", required=True)
    subtitle = fields.Char(string="Subtítulo")
    description = fields.Text(string="Descripción")
    
    # Configuración de Medios
    media_type = fields.Selection([
        ('image', 'Imagen'),
        ('video', 'Video URL')
    ], string="Tipo de Medio", default='image', required=True)

    image = fields.Binary(string="Imagen de Fondo", attachment=True)
    image_filename = fields.Char("Nombre archivo imagen")
    
    # Campo para URL manual si prefieren hostear la imagen fuera, similar al modulo HOME
    image_src_manual = fields.Char(string="URL Manual Imagen", help="Si se llena, tiene prioridad sobre la imagen subida")
    
    video_url = fields.Char(string="URL del Video", help="URL externa o embed")

    def get_image_url(self):
        """Retorna la URL relativa, el controlador la convertirá en absoluta"""
        self.ensure_one()
        if self.image_src_manual:
            return self.image_src_manual
        
        if self.image:
            # Retornamos la ruta relativa estándar de Odoo
            return f"/web/image?model={self._name}&id={self.id}&field=image"
        return ""