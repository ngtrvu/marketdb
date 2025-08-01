from xpider.models import NewsPost, NewsTrending
from xpider.services.base import BaseService
from xpider.services.news_post import GetNewsPostService


class NewsTrendingService(BaseService):
    data: NewsPost = None

    def __init__(self, input_date=None, limit=20):
        self.input_date = input_date
        self.limit = limit

    def valid(self):
        if self.limit < 1:
            self.error_message = "Invalid limit number"
            return False

        return True

    def call(self) -> bool:
        if not self.valid():
            return False

        trending_doc_ids = NewsTrending.objects.filter().order_by('-created').all()
        docs_via_topic = trending_doc_ids[: self.limit]
        doc_ids = [d.doc_id for d in docs_via_topic]
        queryset = GetNewsPostService.get_queryset().filter(doc_id__in=doc_ids)

        self.data = queryset
        return True
