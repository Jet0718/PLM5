from odoo import models, fields, api


class ProductCharacteristic(models.Model):
    _name = 'product.characteristic'
    _description = '産品特性'

    # 特性
    name = fields.Char(string='特性', required=True)
    # 描述
    description = fields.Text(string='描述')
    # 産品或過程標記
    product_process_mark = fields.Selection([('Product', '産品'), ('Process', '過程')], string='産品或過程標記', default='Product')
    # 類型
    type = fields.Selection([('Dimensional', '尺寸'), ('Material', '材料'),("Functional","功能")], string='類型', default='Dimensional')
    # 特性所屬RDQ
    rfq_id = fields.Many2one("rfq.property", string="特性所屬RFQ", required=True)
