from odoo import models, fields, api


class RfqFlow(models.Model):
    _name = "rfq.flow"
    _description = "RFQ送審流程"
    _inherit = ["mail.thread", "mail.activity.mixin", "tier.validation"]
    _rec_name = "item_number"  # 顯示名稱字段

    _state_field = "state"
    _state_from = ["Preliminary", "In Review"]
    _state_to = ["In Review", "On Close"]
    _tier_validation_manual_config = False
    # 送審編號
    item_number = fields.Char(
        string="送審編號", required=True, default="New", readonly=True
    )

    # 送審備注
    submit_remark = fields.Text(string="送審備注")
    # 送審主旨
    submit_subject = fields.Text(string="送審主旨")
    # 參考RFQ編號
    rfq_id = fields.Many2one("rfq.property", string="參考RFQ編號", required=True)
    # PM/設變負責人
    pm_id = fields.Many2one("res.users", string="PM/設變負責人", required=True)
    # 送審狀態
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
    # 送審RFQ（改爲 One2many）
    rfq_property_ids = fields.Many2many(
        "rfq.property",
        "rfq_flow_rfq_property_rel",  # 中間表名
        "rfq_flow_id",  # 當前模型在中間表的字段名
        "rfq_property_id",  # 目標模型在中間表的字段名
        string="送審RFQ",
        help="選擇需要送審的RFQ表單",
    )
    versionflog = fields.Integer(string="版本號", default="1")
    # 評估人員
    assess_id = fields.Many2many("res.users", string="評估人員")

    @api.model_create_multi  # 關鍵裝飾器
    def create(self, vals_list):
        """支持批量創建並自動生成序列號"""
        for vals in vals_list:
            if not vals.get("item_number") or vals.get("item_number") == "New":
                seq = self.env["ir.sequence"].next_by_code("rfq_flow_sequence")
                vals["item_number"] = seq
        return super().create(vals_list)

    def setversionflog(self):
        pass

    def write(self, vals):
        vals["create_uid"] = self.create_uid
        return super(RfqFlow, self).write(vals)

    def action_set_InReview(self):
        # 改變rfq_property_ids的狀態爲In Review
        for rfq_property in self.rfq_property_ids:
            rfq_property.write({"state": "In Review"})
        self.write({"state": "In Review"})

    def do_reject_Preliminary(self):
        for rfq_property in self.rfq_property_ids:
            rfq_property.write({"state": "Preliminary"})
        self.write({"state": "Preliminary"})

    def action_set_OnClose(self):
        for rfq_property in self.rfq_property_ids:
            rfq_property.write({"state": "On Close"})
        self.write({"state": "On Close"})
