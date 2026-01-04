from odoo import _, api, fields, models
from lxml import etree
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.tools.misc import frozendict
import logging


_logger = logging.getLogger(__name__)

class TierRjectValidation(models.Model):
    _name = "tier.reject.validation"
    _description = "reject.validation"
    
    definition_id =fields.Many2one('tier.definition',string='退化关卡')