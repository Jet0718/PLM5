from odoo import models, fields;
class CadAttachmentRel(models.Model):
    _name = 'cad.attachment.rel'
    _description = '工程圖附件關聯表'
    _table = 'cad_attachment_rel'  # 顯式指定表名

    cad_id = fields.Many2one(
        'cad', 
        string="工程圖",
        ondelete='cascade',
        required=True
    )
    attachment_id = fields.Many2one(
        'ir.attachment',
        string="附件",
        ondelete='cascade',
        required=True
    )
    sort_order = fields.Integer(string="排序")  # 自定義擴展字段