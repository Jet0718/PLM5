from odoo import api,fields, models,_, SUPERUSER_ID
from datetime import timedelta
from odoo.exceptions import UserError
class ProjectTask(models.Model):
    _inherit = 'project.task'
    _description = "Task"

    
    document_ids = fields.Many2many('document', string='工程文件')
    documents_document_ids = fields.Many2many('documents.document', string='文件')

    def action_preview_first_document(self):
        self.ensure_one()
        if self.documents_document_ids:
            return self.documents_document_ids[0].access_content()
        else:
            raise UserError(_("No documents to preview."))
