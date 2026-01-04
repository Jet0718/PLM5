from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Cad(models.Model):
    _name = "cad"
    _description = "工程圖"
    _inherit = ['mail.thread','mail.activity.mixin']
    _parent_store = True
    _rec_name = "item_number"  # 顯示文件編號
    # 文件編號
    item_number = fields.Char(
        string="工程圖編號",
        required=True,
        default="New",
        readonly=True,
    )
    # 類別
    classification_id = fields.Many2one(
        "cad.classification",
        string="類別",
        domain="[('child_ids', '=', False)]",
        copy=False,  # 禁止複制
    )
    # 文件名稱
    name = fields.Char(string="名稱")
    # 描述
    description = fields.Text(string="描述")
    # 編輯工具
    editor_id = fields.Many2one("document.editor", string="編輯工具")
    # 變更中
    in_development = fields.Boolean(string="變更中", default=False)
    # 標准件
    is_standard = fields.Boolean(string="標准件", default=False)
    # 項目專屬
    is_project = fields.Boolean(string="專案專屬", default=False)
    # 模板
    is_template = fields.Boolean(string="模板", default=False)
    # 版本
    version = fields.Integer(string="版本", required=True, default=0)
    # 生效日期
    effective_date = fields.Date(string="生效日期")
    # 發行日期
    release_date = fields.Date(string="發行日期", readonly=True)
    # 源文件
    source_file = fields.Many2one(
        "ir.attachment",
        string="源文件",
    )
    # 預覽文件
    preview_file = fields.Many2one(
        "ir.attachment",
        string="預覽文件"
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

    # 發行文件
    release_file = fields.Many2one(
        "ir.attachment",
        string="發行文件"
    ) 
    # 子階工程圖
    child_ids = fields.One2many(
        "cad",
        "parent_id",
        string="子階工程圖",
        context={"active_test": False},  # 顯示所有子分類
    )
    # 父級工程圖
    parent_id = fields.Many2one(
        "cad", string="父級工程圖", domain="[('id', '!=', id)]"
    )  # 不能選擇自己爲父級
    parent_path = fields.Char(index=True)
    # 附件
    attachment_ids = fields.Many2many(
        "ir.attachment",
        relation="cad_attachment_rel",  # 指定自定義中間表
        column1="cad_id",  # 主表外鍵字段名
        column2="attachment_id",  # 關聯表外鍵字段名
        string="附件",
    )

    @api.constrains("classification_id")
    def _check_classification_leaf(self):
        for rec in self:
            if rec.classification_id and rec.classification_id.child_ids:
                raise ValidationError("只能選擇沒有下級分類的類別（子階節點）！")

    @api.model_create_multi  # 關鍵裝飾器
    def create(self, vals_list):
        """支持批量創建並自動生成序列號"""
        for vals in vals_list:
            if not vals.get("item_number") or vals.get("item_number") == "New":
                seq = self.env["ir.sequence"].next_by_code("cad_sequence")
                vals["item_number"] = seq
        # 調用ORM原生批量創建
        return super().create(vals_list)

    @api.constrains("parent_id")
    def _check_no_recursion(self):
        for rec in self:
            parent = rec.parent_id
            while parent:
                if parent == rec:
                    raise ValidationError("父級工程圖不能遞歸嵌套自己！")
                parent = parent.parent_id

    dco_ids = fields.One2many('express.dco','cad_ids')
    dco_count =fields.Integer("數量" ,compute='_compute_dco_count')

    #計算關聯DCO的數量
    @api.depends("dco_ids")
    def _compute_dco_count(self):
        for record in self:
            try: 
                record.dco_count = len(record.dco_ids)                
            except Exception as e:                
                record.dco_count =self.env['express.dco'].search_count([('cad_ids', '=', record.id)])

    def express_dco_model_action(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'DCO',
            'view_mode': 'list,form',
            'res_model': 'express.dco',
            'domain': [('cad_ids', '=', self.id) ],
            'context': {'default_cad_ids': self.id},
        }