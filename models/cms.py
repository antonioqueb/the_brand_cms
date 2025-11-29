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
                # Resolvemos URLs dinámicamente
                'image_url': ch.get_image_src(),
                'video_url': ch.get_video_src(),
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
    
    # Selector de Tipo de Medio
    media_type = fields.Selection([
        ('image', 'Imagen'),
        ('video', 'Video')
    ], string="Tipo de Medio", default='image', required=True)

    # --- CAMPOS DE IMAGEN ---
    image = fields.Binary(string="Archivo de Imagen", attachment=True)
    image_filename = fields.Char("Nombre archivo imagen")
    image_src_manual = fields.Char(string="URL Externa (Imagen)", help="Opcional: URL externa si no subes archivo")

    # --- CAMPOS DE VIDEO ---
    video_file = fields.Binary(string="Archivo de Video", attachment=True)
    video_filename = fields.Char("Nombre archivo video")
    video_url_manual = fields.Char(string="URL Externa (Video)", help="Opcional: Youtube/Vimeo o link directo")

    def get_image_src(self):
        """Prioridad: 1. Manual URL, 2. Archivo subido"""
        self.ensure_one()
        if self.image_src_manual:
            return self.image_src_manual
        if self.image:
            return f"/web/image?model={self._name}&id={self.id}&field=image"
        return ""

    def get_video_src(self):
        """Prioridad: 1. Archivo subido (Ruta con nombre de archivo), 2. Manual URL"""
        self.ensure_one()
        
        if self.video_file:
            # TRUCO: Agregamos el nombre del archivo a la URL
            # Limpiamos el nombre de espacios para evitar errores de URL
            safe_filename = (self.video_filename or 'video.mp4').replace(' ', '_')
            return f"/api/the-brand/video/{self.id}/{safe_filename}"
        
        return self.video_url_manual or ""