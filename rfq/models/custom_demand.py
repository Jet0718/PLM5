from odoo import models, fields, api


class CustomDemand(models.Model):
    _name = "custom.demand"
    _description = "客戶需求"

    # 文件上傳時間
    upload_time = fields.Datetime(
        string="文件上傳時間", default=fields.Datetime.now, readonly=True
    )
    file_name = fields.Char(string="文件名稱")
    # 附加文件名稱
    attach_file_name = fields.Char(string="附加文件名稱")
    # 文件信息
    file_info = fields.Char(string="文件信息")
    # 變更記錄
    change_record = fields.Char(string="變更記錄")
    # 附件
    file = fields.Binary(string="附件", required=True)
    # 附加文件
    attach_file = fields.Binary(string="附加文件")
    # 文件所屬RFQ
    rfq_id = fields.Many2one("rfq.property", string="文件所屬RFQ", required=True)

    # @api.model
    # def create(self, vals):
    #     """在創建記錄時自動設置文件名"""
    #     if vals.get('file') and not vals.get('file_name'):
    #         vals['file_name'] = "uploaded_file"  # 默認文件名，可根據需求修改
    #     if vals.get('attach_file') and not vals.get('attach_file_name'):
    #         vals['attach_file_name'] = "attached_file"  # 默認附加文件名，可根據需求修改
    #     return super(CustomDemand, self).create(vals)

    # def write(self, vals):
    #     """在更新記錄時自動設置文件名"""
    #     for record in self:
    #         if vals.get('file') and not vals.get('file_name'):
    #             vals['file_name'] = "uploaded_file"  # 默認文件名
    #         if vals.get('attach_file') and not vals.get('attach_file_name'):
    #             vals['attach_file_name'] = "attached_file"  # 默認附加文件名
    #     return super(CustomDemand, self).write(vals)

