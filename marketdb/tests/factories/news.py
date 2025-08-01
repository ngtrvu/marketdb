from datetime import datetime
from pytz import timezone
from factory.django import DjangoModelFactory

from common.utils.datetime_util import VN_TIMEZONE
from xpider.models import NewsPost, NewsTopic, Topic, NewsTrending


class NewsPostFactory(DjangoModelFactory):

    class Meta:
        model = NewsPost

    published = datetime.now(tz=timezone(VN_TIMEZONE))


class NewsTopicFactory(DjangoModelFactory):

    class Meta:
        model = NewsTopic

    modified = datetime.now(tz=timezone(VN_TIMEZONE))


class TopicFactory(DjangoModelFactory):

    class Meta:
        model = Topic


class NewsTrendingFactory(DjangoModelFactory):

    class Meta:
        model = NewsTrending
