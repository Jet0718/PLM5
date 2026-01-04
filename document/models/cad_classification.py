from odoo import models, fields, api;
class CadClassification(models.Model):
    _name = 'cad.classification'
    _description = "工程圖分類"
    _parent_store = True
    _rec_name = 'complete_name' # 顯示完整路徑

    name = fields.Char(string="類名", required=True)
    parent_id = fields.Many2one(
        "cad.classification",
        string="上級分類",
        ondelete="cascade",
        index=True,
        domain="[('id', '!=', id)]",  # 添加層級深度限制
    )
    child_ids = fields.One2many(
        "cad.classification",
        "parent_id",
        string="下級分類",
        context={"active_test": False},  # 顯示所有子分類
    )
    parent_path = fields.Char(index=True)  # 自動用于遞歸層級計算
    complete_name = fields.Char(
        string="路徑", compute="_compute_complete_name", store=True, recursive=True
    )

    cad_ids = fields.One2many("cad", "classification_id", string="文件")

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for rec in self:
            if rec.parent_id:
                rec.complete_name = f"{rec.parent_id.complete_name} / {rec.name}"
            else:
                rec.complete_name = rec.name
    def name_get(self):
        result = []
        for rec in self:
            name = rec.complete_name if rec.complete_name else rec.name
            result.append((rec.id, name))
        return result