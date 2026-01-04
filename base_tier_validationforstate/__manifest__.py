# Copyright 2017-24 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Base Tier Validation for state",
    "summary": "Implement a validation process based on tiers  for state.",
    "version": '19.0.1.0.0',
    "maintainers": ["LoisRForgeFlow"],
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "BWCS PMO",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["mail", "base_tier_validation","base"],
    "data": [
        'security/ir.model.access.csv',
        "views/tier_definition_view.xml",
        # "views/cn_template_view.xml",  # temporarily disabled due to missing model
        # "views/tier_reject_validation_view.xml",
    ],
    # "assets": {
    #     "web.assets_backend": [
    #         "base_tier_validationforstate/static/src/components/tier_review_widget/tier_review_widget.xml",
    #     ],
    # },
}
