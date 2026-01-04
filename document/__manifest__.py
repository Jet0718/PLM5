{
    "name": "圖文管理",  # 模組名稱
    "summary": "圖文管理模組",  # 模組摘要
    "version": "19.0.0.1",  # 版本號
    "category": "PLM/Document",  # 模組分類
    'author': "BWCS PMO",
    "data": [
        "security/ir.model.access.csv",  # 許可權存取控制文件
        "views/document_views.xml",  # 視圖文件
        "views/document_state_views.xml",  # 狀態視圖檔
        "views/document_classification_views.xml",  # 分類視圖檔
        "views/document_editor_views.xml",  # 編輯器視圖檔
        "views/cad_views.xml",  # CAD視圖文件
        "views/cad_state_views.xml",  # CAD狀態視圖檔
        "views/cad_classification_views.xml",  # CAD分類視圖檔
        "views/express_dco_state_views.xml",  # DCO狀態視圖檔
        "views/express_dco_views.xml",  # DCO視圖文件
        "data/document_sequence.xml",  # 序列資料檔案
        "views/document_menus.xml",  # 菜單視圖檔
        "data/form_state_data.xml",  # 狀態資料檔案
        "data/document_classification_data.xml",  # 文件分類資料檔案
        "data/cad_classification_data.xml",  # CAD分類資料檔案
        "data/document_editor_data.xml",  # 編輯器資料檔案
    ],  # 資料檔案列表
    "assets": {
        "web.assets_backend": [],
    },  # 資源檔列表
    "depends": ["base", "mail", "web", "base_tier_validation"],  # 依賴的模組清單
    "license": "LGPL-3",  # 許可證類型
    "installable": True,  # 是否可安裝
    "application": True,  # 是否為應用程式
}


