from odoo import api,fields, models,_
from datetime import timedelta
from odoo.exceptions import UserError

class SelectionOption(models.Model):
    _name = 'pco.type'
    _description = 'pco Selection Option'

    # name = fields.Char('Name')
    name =fields.Selection(
        string="審批類別",
        selection=[('Product','產品'),('Bom','物料清單')]
    )

