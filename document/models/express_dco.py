from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ExpressDCO(models.Model):
    _name = "express.dco"
    _description = "DCO-圖/文 送審單"
    _rec_name = "item_number"  # 顯示名稱
    _inherit = ["mail.thread", "mail.activity.mixin", "tier.validation"]

    # Base Tier Validation 配置
    _state_field = "state"  # 狀態字段名
    _state_from = ["New", "In Review","In Work"]  # 觸發審批前的狀態
    _state_to = ["In Review", "Released"]  # 審批後的目標狀態
    _tier_validation_manual_config = False

    # DCO 編號
    item_number = fields.Char(
        string="DCO編號",
        required=True,
        default="New",
        readonly=True,
    )
    # 主旨
    subject = fields.Char(string="主旨", required=True)
    # 原因說明
    reason = fields.Text(string="原因說明", required=True)
    # 描述
    description = fields.Text(string="描述")
    # 類別
    category = fields.Selection(
        [("Document", "文件"), ("CAD", "工程圖")],
        string="類別",
        required=True,
    )
    # 項目專屬
    is_project = fields.Boolean(string="專案專屬", default=False)
    # 狀態
    state = fields.Selection(
        [
            ("New", "新建立"),
            ("In Work", "編輯中"),
            ("In Review", "審核中"),
            ("Released", "已發布"),
            ("Cancelled", "已取消"),
        ],
        string="狀態",
        default="New",
        required=True,
        copy=False,
    )
    # 負責人
    owner_id = fields.Many2one(
        "res.users",
        string="負責人",
        default=lambda self: self.env.user,
    )
    # 管理者
    manager_id = fields.Many2one(
        "res.users",
        string="管理者",
        default=lambda self: self.env.user,
    )
    # 緊急程度
    priority = fields.Selection(
        [("0", "正常"), ("1", "緊急"), ("2", "非常緊急")],
        string="緊急程度",
        default="0",
    )
    # 發行日期
    release_date = fields.Date(string="發行日期")
    # 團隊
    team_id = fields.Char(string="團隊")
    # 工程圖初審人員
    cad_reviewer_id = fields.Many2one("res.users", string="工程圖初審人員")
    # 工程圖複審
    cad_reviewer2_id = fields.Many2one("res.users", string="工程圖複審")
    # 附件
    attachment_ids = fields.Many2many(
        "ir.attachment",
        relation="express_dco_attachment_rel",  # 指定自定義中間表
        column1="express_dco_id",  # 主表外鍵字段名
        column2="attachment_id",  # 關聯表外鍵字段名
        string="附件",
    )
    # 送審文件
    document_ids = fields.Many2many(
        "document",
        relation="express_dco_document_rel",  # 指定自定義中間表
        column1="express_dco_id",  # 主表外鍵字段名
        column2="document_id",  # 關聯表外鍵字段名
        string="送審文件",
        domain="[('state', '!=', 'cancel')]",
    )
    # 送審工程圖
    cad_ids = fields.Many2many(
        "cad",
        relation="express_dco_cad_rel",  # 指定自定義中間表
        column1="express_dco_id",  # 主表外鍵字段名
        column2="cad_id",  # 關聯表外鍵字段名
        string="送審工程圖",
        domain="[('state', '!=', 'cancel')]",
    )
    versionflog = fields.Integer(string="版本號", default="1")

    @api.model_create_multi  # 關鍵裝飾器
    def create(self, vals_list):
        """支持批量創建並自動生成序列號"""
        for vals in vals_list:
            if not vals.get("item_number") or vals.get("item_number") == "New":
                seq = self.env["ir.sequence"].next_by_code("express_dco_sequence")
                vals["item_number"] = seq
        # 調用ORM原生批量創建
        return super().create(vals_list)

    def write(self, vals):
        vals["create_uid"] = self.create_uid
        return super(ExpressDCO, self).write(vals)

    def setversionflog(self):
        if self.category == "Document":
            isSkip = True
            for document in self.document_ids:
                if document.state == "Released":
                    isSkip = False
                    break
            if isSkip == False:
                return self.write({"versionflog": "2"})
        else:
            isSkip = True
            for cad in self.cad_ids:
                if cad.state == "Released":
                    isSkip = False
                    break
            if isSkip == False:
                self.write({"versionflog": "2"})

    def action_InDraft(self):
        if self.category == "Document":
            isSkip = True
            for document in self.document_ids:
                if document.state == "Released":
                    isSkip = False
                    break
            if isSkip:
                self.action_set_InReview()
        else:
            isSkip = True
            for cad in self.cad_ids:
                if cad.state == "Released":
                    isSkip = False
                    break
            if isSkip:
                self.action_set_InReview()

    def action_InApprove(self):
        if self.category == "Document":
            for document in self.document_ids:
                document.write({"state": "New"})
                document.write({"version": document.version + 1})
        else:
            for cad in self.cad_ids:
                cad.write({"state": "New"})
                cad.write({"version": cad.version + 1})
        self.write({"state": "In Work"})

    def action_set_InReview(self):
        if self.category == "Document":
            for document in self.document_ids:
                document.write({"state": "In Review"})
        else:
            for cad in self.cad_ids:
                cad.write({"state": "In Review"})
        self.write({"state": "In Review"})

    def action_set_Released(self):
        if self.category == "Document":
            for document in self.document_ids:
                document.write({"state": "Released"})
        else:
            for cad in self.cad_ids:
                cad.write({"state": "Released"})
        self.write({"state": "Released"})

    def do_reject_New(self):
        if self.category == "Document":
            for document in self.document_ids:
                document.write({"state": "New"})
        else:
            for cad in self.cad_ids:
                cad.write({"state": "New"})
        self.write({"state": "New"})
