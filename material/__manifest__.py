{
    'name': "Electronics industry of Material",
    'version': '1.0',
    'depends': ['base', 'mail', 'web', 'mrp', 'mrp_plm', 'document','project'],
    'author': "BWCS PMO",
    'category': 'Manufacturing',
    'license': 'LGPL-3',
    'summary': "Electronics industry material management",
    'description': """
    Electronics industry of Material 電子業-產品管理
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/class_template_view.xml',
        'views/part_list_view.xml',
        'views/part_stage_view.xml',
        'views/partbom_stage_view.xml',
        'views/part_view.xml',
        'views/part_class_view.xml',
        'views/part_bom_view.xml',
        'views/pco_type_view.xml',
        'views/pco_tag_view.xml',
        'views/pco_view.xml',
        'views/pco_product_view.xml',
        'views/pco_bom_view.xml',
        'views/project_task_view.xml',
        'views/material_menus.xml',
        'views/part_document_view.xml',
        'views/part_cad_view.xml',
        'data/part_sequence.xml',
        'data/partbom_sequence.xml',
        'data/pco_sequence.xml',
        'data/part_stage.xml',
        'data/partbom_stage.xml',
        'data/pco_type.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'material/static/src/css/style.css',
        ]
    },
    'installable': True,
    'application': False,
}