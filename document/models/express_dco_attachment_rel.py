from odoo import models, fields


class ExpressDCOAttachmentRel(models.Model):
    _name = "express.dco.attachment.rel"
    _description = "DCO-圖/文 送審單-附件 關聯表"
    _table = "express_dco_attachment_rel"  # 顯式指定表名

    express_dco_id = fields.Many2one(
        "express.dco",
        string="DCO-圖/文 送審單",
        required=True,
    )
    attachment_id = fields.Many2one(
        "ir.attachment",
        string="附件",
        required=True,
    )
