from rest_framework import serializers

from common.drfexts.serializers.fields import ExternalImageSerializer
from core.models.cryptos.crypto import Crypto

COINGECKO_ASSET_URL = "https://assets.coingecko.com/coins/images"
COINGECKO_ALIAS = "coingecko_assets"


class CryptoSerializer(serializers.ModelSerializer):
    photo = ExternalImageSerializer(host_alias=COINGECKO_ALIAS, host_url=COINGECKO_ASSET_URL)

    class Meta:
        model = Crypto
        fields = "__all__"
        singular_resource_name = "item"


class CryptoDetailSerializer(serializers.ModelSerializer):
    photo = ExternalImageSerializer(host_alias=COINGECKO_ALIAS, host_url=COINGECKO_ASSET_URL)

    class Meta:
        model = Crypto
        fields = "__all__"
        singular_resource_name = "item"


class CryptoNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crypto
        fields = ["id", "name", "symbol"]


class CryptoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crypto
        fields = "__all__"


class CryptoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crypto
        fields = "__all__"
