{
    'name': "Electronics industry of PR",
    'version': '19.0.1.0.0',
    'depends': ['base','mail','web','base_tier_validation','project','document','material','mrp_plm'],
    'author': "BWCS PMO",
    'category': 'Category',
    'license' : 'LGPL-3',
    'description': """
    Electronics industry of PR 電子業-問題單
    """,    
    'data': [        
        'security/ir.model.access.csv',
        'views/pr_view.xml',
        'views/errorcode_view.xml',
        'views/pr_stage_view.xml',
        'views/pr_tracking_view.xml',
        'views/pr_document_view.xml',
        'views/pr_cad_view.xml',
        'views/pr_project_view.xml',
        'views/pr_part_view.xml',
        'views/pr_menus.xml', 
        'data/pr_sequence.xml', 
        'data/pr_stage.xml'
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'demand/static/src/css/style.css',
    #     ]
    # }
}