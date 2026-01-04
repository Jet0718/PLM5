from odoo import api,fields, models,_, SUPERUSER_ID
from datetime import timedelta
from odoo.exceptions import UserError 

class PartBomline(models.Model):
    _inherit = 'mrp.bom.line'
    _description = "Material management main model of part_bom_line."

    product_id = fields.Many2one('product.product', 'Component', required=True, check_company=True)
    product_qty = fields.Float(
        'Quantity', default=1.0,
        digits='Product Unit of Measure', required=True)
    group =fields.Char(string="替代群組")
    order =fields.Integer(string="替代順序")
    ratio =fields.Float(string="替代比例" ,digits=(5,2))
    reference =fields.Char(string="插件位置")

class PartBom(models.Model):
    _inherit = 'mrp.bom'
    _description = "Material management main model of part_bom."
    
    code =fields.Char("編號" , default=lambda self: _('New'), copy=False , readonly=True )
    version=fields.Integer(string="版本",default=0,copy=False,readonly=True)
    stage_id = fields.Many2one('partbom.stage', string='狀態階段', group_expand='_read_group_stage_ids',
                               copy=False,default=lambda self: self.env['partbom.stage'].search([('name', '=', 'New')], limit=1))
    
 # Seqence 自動領號寫法
    @api.model_create_multi
    def create(self, vals_list):
        """ Create a sequence for the partbom model """
        for vals in vals_list:
                if vals.get('code', _('New')) == _('New'):
                    vals['code'] = self.env['ir.sequence'].next_by_code('partbom')
        return super().create(vals_list)


    @api.constrains('bom_line_ids')
    def _check_reference(self):
        """
        檢查 reference 欄位的值是否符合要求:
        1. reference 中的內容使用 "," 隔開。
        2. reference 中的每個 "," 區分的內容不能重複。
        3. 若 reference 中有值，必須包含逗號（","），且逗號數量與 product_qty 一致。
        若不一致，錯誤資訊要列出是哪一個 product_id,數量為 "product_qty" 多少，但 "reference" 的數量只有多少。
        """
        error_messages = []  # 用於存儲錯誤資訊

        for record in self.bom_line_ids:
            # 檢查 reference 是否有值
            if record.reference:
                # 檢查 reference 中的內容是否使用 "," 隔開
                references = record.reference.split(',')
                references = [ref.strip() for ref in references]  # 去除首尾空格

                # 檢查 reference 中的每個 "," 區分的內容是否重複
                if len(references) != len(set(references)):
                    error_messages.append(
                        _("PLM編號為 %s,品名為 %s 的記錄中，插件位置存在重複的內容！") % (record.product_id.name, record.product_id.name)
                    )

                # 檢查逗號數量是否與 product_qty 一致
                if len(references) != record.product_qty:
                    error_messages.append(
                        _("PLM編號為 %s,品名為 %s 的記錄中，數量為 %s,但插件位置的數量為 %s,不一致!") % (
                            record.product_id.name, record.product_id.name, record.product_qty, len(references)
                        )
                    )

        # 如果有錯誤訊息，一起拋出異常
        if error_messages:
            raise UserError("\n".join(error_messages))

    