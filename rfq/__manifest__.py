{
    "name": "報價管理",  # 模塊名稱
    "summary": "報價管理，報價流程審批",  # 模塊摘要
    "version": "19.0.0.1",  # 版本號
    "category": "PLM/RFQ",# 模塊分類
    'author': "BWCS PMO",
    "data": [
        "security/ir.model.access.csv",  # 權限訪問控制文件
        "views/rfq_flow_state_views.xml", # RFQ送審流程狀態視圖文件
        "views/rfq_property_state_views.xml",  # RFQ報價主檔狀態視圖文件
        "views/rfq_property_views.xml",  # RFQ報價主檔視圖文件
        "views/custom_demand_views.xml",  # 客戶需求視圖文件
        "views/quotation_additional_document_views.xml",  # 報價單附加文件視圖文件
        "views/product_characteristic_views.xml",  # 産品特性視圖文件
        "views/competitor_record_views.xml",  #  競爭記錄視圖文件
        "views/rfq_flow_views.xml",  # RFQ送審流程視圖文件
        "views/rfq_menus.xml",  # 菜單視圖文件
        "data/rfq_sequence.xml",  # 序列數據文件
        "data/form_state_data.xml",  # 狀態數據文件
    ],  # 數據文件列表
    "assets": {
        "web.assets_backend": [
            "rfq/static/src/js/assignmentfilename.js",
            "rfq/static/src/css/kanban.scss",
        ],
    },  # 資源文件列表
    "depends": ["base", "mail",'base_tier_validation'],  # 依賴的模塊列表
    "license": "LGPL-3",  # 許可證類型
    "installable": True,  # 是否可安裝
    "application": True,  # 是否爲應用程序
}
