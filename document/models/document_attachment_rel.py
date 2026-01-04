from odoo import models, fields, api;
class DocumentAttachmentRel(models.Model):
    _name = 'document.attachment.rel'
    _description = '文件附件關聯表'
    _table = 'document_attachment_rel'  # 顯式指定表名

    document_id = fields.Many2one(
        'document', 
        string="文件",
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