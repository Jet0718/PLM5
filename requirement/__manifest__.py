{
    'name': "Requirement & Evaluate",
    'version': '19.0.1.0.0',
    'depends': ['base','product','project'],
    'author': "BWCS PMO",
    'category': 'Category',
    'license' : 'LGPL-3',
    'description': """
    Requirement & Evaluate 需求評估
    """,    
    'data': [
        'security/ir.model.access.csv',
        'views/requirement_view.xml',
        'views/requirement_purpose_view.xml',
        'views/requirement_spec_view.xml',
        'views/requirement_menus.xml',  
        'views/requirement_project_view.xml',
        'views/requirement_lead_view.xml',
        'data/requirement_sequence.xml'     
    ]
}