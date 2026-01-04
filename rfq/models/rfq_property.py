from odoo import models, fields, api


class RfqPrperty(models.Model):
    # 模型名稱
    _name = "rfq.property"
    # 模型描述
    _description = "RFQ報價主檔"
    # 繼承郵件線程和活動混合類
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # 顯示名稱
    _rec_name = "item_number"

    # RFQ報價編號
    item_number = fields.Char(
        string="RFQ報價編號",
        readonly=True,  # 禁止編輯
        default="New",  # 默認值
        help="RFQ報價編號",
        required=True,  # 必填
        copy=False,  # 禁止複制
    )
    # 客戶名稱
    customer = fields.Many2one("res.partner", string="客戶名稱", required=True)
    #  客戶産品名稱
    part_name = fields.Char(string="客戶産品名稱", required=True)
    # 客戶産品編號
    part_number = fields.Char(string="客戶産品編號", required=True)
    # 變更記錄
    change_record = fields.Char(string="變更記錄")
    # 競爭對手
    comprtitors = fields.Char(string="競爭對手")
    # 是否成交
    deal = fields.Selection(
        [("yes", "是"), ("no", "否")], string="是否成交", default="no"
    )
    # 産品型號
    is_car_type = fields.Char(string="産品型號")
    # 機種別
    model = fields.Char(string="機種別")
    # 部品價格
    part_price = fields.Float(string="部品價格")
    # 項目編號
    project_number = fields.Char(string="項目編號")
    # 每台用量
    quantity = fields.Integer(string="每台用量")
    # 報價日期
    quotation_date = fields.Date(string="報價日期")
    # 報價信息
    quotation_info = fields.Char(string="報價信息")
    # 接案日期
    receie_date = fields.Date(string="接案日期")
    # 接案人員
    receier = fields.Many2one("res.users", string="接案人員")
    # 分攤說明
    share_description = fields.Char(string="分攤說明")
    # 模治檢具價格
    tooling_price = fields.Float(string="模治檢具價格")
    # 年預示量
    year_indication = fields.Char(string="年預示量")
    # 圖面審查
    ct01 = fields.Date(string="圖面審查")
    # 送樣
    ct02 = fields.Date(string="送樣")
    # 量試(DURA)
    ct03 = fields.Date(string="量試(DURA)")
    # PSW
    ct04 = fields.Date(string="PSW")
    # 狀態
    state = fields.Selection(
        [
            ("Preliminary", "新建立"),
            ("In Review", "審核中"),
            ("On Close", "已結案"),
            ("Cancelled", "已取消"),
        ],
        string="狀態",
        default="Preliminary",
        required=True,
        copy=False,
    )
    # 是否歸檔
    active = fields.Boolean(string="是否歸檔", default=True)

    # 關聯客戶需求模型
    customer_demand = fields.One2many("custom.demand", "rfq_id", string="客戶需求")
    # 關聯RFQ附加文件模型
    quotation_attachment = fields.One2many(
        "quotation.additional.document", "rfq_id", string="RFQ附加文件"
    )
    # 關聯産品特性模型
    product_characteristics = fields.One2many(
        "product.characteristic", "rfq_id", string="産品特性"
    )
    # 關聯競爭記錄模型
    competitor_record = fields.One2many(
        "competitor.record", "rfq_id", string="競爭記錄"
    )

    @api.model_create_multi  # 關鍵裝飾器
    def create(self, vals_list):
        """支持批量創建並自動生成序列號"""
        for vals in vals_list:
            if not vals.get("item_number") or vals.get("item_number") == "New":
                seq = self.env["ir.sequence"].next_by_code("rfq_property_sequence")
                vals["item_number"] = seq
        return super().create(vals_list)  # 調用ORM原生批量創建
