from odoo import models, fields;
class ExpressDCOCADRel(models.Model):
    _name = 'express.dco.cad.rel'
    _description = '送審單與工程圖關聯表'
    _table = 'express_dco_cad_rel'  # 顯式指定表名

    express_dco_id = fields.Many2one(
        'express.dco',
        string="DCO",
        ondelete='cascade',
        required=True
    )
    cad_id = fields.Many2one(
        'cad',
        string="CAD",
        ondelete='cascade',
        required=True
    )
    sort_order = fields.Integer(string="排序")  # 自定義擴展字段