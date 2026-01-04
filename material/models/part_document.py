from odoo import fields, models,api,_

class PartDocument(models.Model):
    _inherit = "document"
    # 增加關聯物料 及 數量
    part_ids = fields.One2many('product.template','document_id')
    part_count =fields.Integer("數量" ,compute='_compute_part_count')

#計算關聯part的數量
    @api.depends("part_ids")
    def _compute_part_count(self):
        for record in self:
            try: 
                record.part_count = len(record.part_ids)                
            except Exception as e:                
                record.part_count =self.env['product.template'].search_count([('document_id', '=', record.id)])

    def product_template_action(self):
        return {
            'type': 'ir.actions.act_window',
            'name': '物料',
            'view_mode': 'list,form',
            'res_model': 'product.template',
            'domain': [('document_id', '=', self.id) ],
            'context': {'default_document_id': self.id},
        }