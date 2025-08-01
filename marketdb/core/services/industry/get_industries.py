from core.services.product import ProductService
from core.models.industries.industry import Industry
from core.models.industries.industry_analytics import IndustryAnalytics


class GetIndustriesService(ProductService):

    main_model = Industry
    meta_models = [IndustryAnalytics]
    join_field = 'icb_code'
    mapping_fields = {}

    fields = []
    filters = []
    sorts = []
