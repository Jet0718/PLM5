from odoo import models, fields;
class ExpressDCODocumentRel(models.Model):
    _name = 'express.dco.document.rel'
    _description = '送審單與文件關聯表'
    _table = 'express_dco_document_rel'  # 顯式指定表名

    express_dco_id = fields.Many2one(
        'express.dco',
        string="DCO",
        ondelete='cascade',
        required=True
    )
    document_id = fields.Many2one(
        'document',
        string="文件",
        ondelete='cascade',
        required=True
    )