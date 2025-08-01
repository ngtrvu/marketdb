from xpider.models import NewsPost, NewsTopic
from xpider.services.base import BaseService
from xpider.services.news_post import GetNewsPostService


class NewsTopicService(BaseService):
    data: NewsPost = None

    def __init__(self, topic_token, limit=100):
        self.topic_token = topic_token
        self.limit = limit

    def valid(self):
        if " " in self.topic_token:
            self.error_message = "Invalid topic identify"
            return False
        if self.limit < 1:
            self.error_message = "Invalid limit number"
            return False

        return True

    def call(self) -> bool:
        if not self.valid():
            return False

        if not self.topic_token or len(self.topic_token) < 1:
            queryset = GetNewsPostService.get_queryset()
        else:
            topic_tokens = self.topic_token.split(",")
            docs_via_topic = (
                NewsTopic.objects
                    .filter(topic_token__in=topic_tokens)
                    .order_by('-created')
                    .values_list('doc_id', flat=True)
                    .distinct()
            )
            doc_ids = list(docs_via_topic)
            queryset = (
                GetNewsPostService
                    .get_queryset()
                    .filter(doc_id__in=doc_ids)
                # [: self.limit]
            )

        self.data = queryset
        return True
