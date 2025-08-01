from core.services.product import ProductService
from core.models.bank import Bank


class GetBanksService(ProductService):

    main_model = Bank
    meta_models = []
    join_field = 'symbol'
    mapping_fields = {}

    fields = []
    filters = []
    sorts = []
