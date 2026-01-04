from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

# 導入異常類


class Document(models.Model):
    _name = "document"
    _description = "文件管理"
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = "item_number"  # 顯示文件編號
    # 文件編號
    item_number = fields.Char(
        string="文件編號",
        required=True,
        default="New",
        readonly=True,
    )
    # 類別
    classification_id = fields.Many2one(
        "document.classification",
        string="類別",
        domain="[('child_ids', '=', False)]",
        copy=False,  # 禁止複制
    )
    # 文件名稱
    name = fields.Char(string="文件名稱")
    # 文件說明
    description = fields.Text(string="文件說明")
    # 版本
    version = fields.Integer(string="版本", required=True, default=0)
    # 文件類型
    document_type = fields.Selection(
        [("DHF", "DHF"), ("DMR", "DMR")], string="文件類型"
    )
    # 編輯工具
    editor_id = fields.Many2one("document.editor", string="編輯工具")
    # 變更中
    in_development = fields.Boolean(string="變更中", default=False)
    # 項目專屬
    is_project = fields.Boolean(string="專案專屬", default=False)
    # 狀態
    state = fields.Selection(
        [
            ("New", "新建立"),
            ("In Review", "審核中"),
            ("Released", "已發布"),
        ],
        string="狀態",
        default="New",
        required=True,
        copy=False,
    )
    # 擁有者
    owner_id = fields.Many2one(
        "res.users", string="擁有者", default=lambda self: self.env.user
    )
    # 管理者
    manager_id = fields.Many2one(
        "res.users", string="管理者", default=lambda self: self.env.user
    )
    # 團隊
    team_id = fields.Char(string="團隊")
    # 縮略圖
    thumbnail = fields.Image(string="縮略圖") 
    # 生效日期
    effective_date = fields.Date(string="生效日期")
    # 發行日期
    release_date = fields.Date(string="發行日期", readonly=True)
    # 附加附檔
    has_attachment = fields.Boolean(string="附加附檔", default=False)
    # 模板
    is_template = fields.Boolean(string="模板", default=False)
    # 附件
    attachment_ids = fields.Many2many(
        "ir.attachment",
        relation="document_attachment_rel",  # 指定自定義中間表
        column1="document_id",  # 主表外鍵字段名
        column2="attachment_id",  # 關聯表外鍵字段名
        string="附件",
    )

    @api.constrains("classification_id")
    def _check_classification_leaf(self):
        for rec in self:
            if rec.classification_id and rec.classification_id.child_ids:
                raise ValidationError("只能選擇沒有下級分類的類別（葉子節點）！")

    @api.model_create_multi  # 關鍵裝飾器
    def create(self, vals_list):
        """支持批量創建並自動生成序列號"""
        for vals in vals_list:
            if not vals.get("item_number") or vals.get("item_number") == "New":
                seq = self.env["ir.sequence"].next_by_code("document_sequence")
                vals["item_number"] = seq
        # 調用ORM原生批量創建
        return super().create(vals_list)
    
    dco_ids = fields.One2many('express.dco','document_ids')
    dco_count =fields.Integer("數量" ,compute='_compute_dco_count')

    #計算關聯DCO的數量
    @api.depends("dco_ids")
    def _compute_dco_count(self):
        for record in self:
            try: 
                record.dco_count = len(record.dco_ids)                
            except Exception as e:                
                record.dco_count =self.env['express.dco'].search_count([('document_ids', '=', record.id)])

    def express_dco_model_action(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'DCO',
            'view_mode': 'list,form',
            'res_model': 'express.dco',
            'domain': [('document_ids', '=', self.id) ],
            'context': {'default_document_ids': self.id},
        }
