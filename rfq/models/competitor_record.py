from odoo import models, fields, api;


class CompetitorRecord(models.Model):
    _name = 'competitor.record'
    _description = '競爭記錄'

    # 競品簡稱
    competitor_name = fields.Char(string='競品簡稱')
    # 競品描述
    competitor_desc = fields.Char(string='競品描述')
    # 參考檔案
    reference_file = fields.Binary(string='參考檔案')
    # 競爭記錄所屬RDQ
    rfq_id = fields.Many2one("rfq.property", string="競爭記錄所屬RFQ", required=True)