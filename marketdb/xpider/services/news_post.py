from xpider.models.news import NewsPost
from django.db.models import Q


class GetNewsPostService:

    @staticmethod
    def get_queryset():
        queryset = (
            NewsPost.objects
                .exclude(published__isnull=True)
                .exclude(relevant_score__isnull=True)
                .filter(Q(is_relevant=True) & Q(relevant_score__gte=0.6))
                .order_by('-relevant_score', '-published')
        )

        return queryset
