from odoo import models, fields, api

class TheBrandPage(models.Model):
    _name = 'the.brand.page'
    _description = 'Configuración Página The Brand'
    _rec_name = 'hero_title'

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
    video_url = fields.Char(string="URL del Video", help="URL externa o embed")

    # Campos técnicos para exponer la URL completa en la API
    def get_image_url(self):
        self.ensure_one()
        if not self.image:
            return False
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/web/image?model=the.brand.chapter&id={self.id}&field=image"

