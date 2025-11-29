{
    'name': 'The Brand CMS API',
    'version': '1.0',
    'category': 'Website/CMS',
    'summary': 'Gestor de contenido headless para The Brand Page',
    'description': """
        Módulo diseñado para gestionar el contenido de la página React 'The Brand'.
        - API Pública de lectura
        - Gestión de Historias/Capítulos
        - Soporte para Imágenes y Videos
        - Interfaz unificada sin redirecciones complejas
    """,
    'author': 'Alphaque Consulting',
    'website': 'https://alphaque.com',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/cms_views.xml',
        'data/cms_data.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
