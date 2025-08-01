from core.services.product import ProductService
from core.models.funds.fund import MutualFund
from core.models.funds.fund_nav import MutualFundNavIndex


class GetFundsService(ProductService):

    main_model = MutualFund
    meta_models = [MutualFundNavIndex]
    join_field = 'symbol'
    mapping_fields = {}

    fields = []
    filters = []
    sorts = []
