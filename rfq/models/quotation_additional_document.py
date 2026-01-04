from odoo import models, fields, api;

class QuotationAdditionalDocument(models.Model):
    _name = 'quotation.additional.document'
    _description = 'RFQ附加文件'

    # 上傳時間
    upload_time = fields.Datetime(string='上傳時間', default=fields.Datetime.now)
    # 文件名稱
    file_name = fields.Char(string='文件名稱')
    # 附加文件名稱
    attach_file_name = fields.Char(string='附加文件名稱')
    # 文件信息
    file_info = fields.Char(string='文件信息')
    # 變更記錄
    change_record = fields.Char(string='變更記錄')
    # 文件
    file = fields.Binary(string='文件', attachment=True)
    # 附加文件
    attach_file = fields.Binary(string="附加文件", attachment=True)
    # 文件所屬RFQ
    rfq_id = fields.Many2one("rfq.property", string="文件所屬RFQ", required=True)
