from datetime import datetime

import pytz
from rest_framework import serializers

from common.drfexts.serializers.fields import ImageHandlerSerializer
from common.utils.sampling import random_sampling
from core.libs.intraday.intraday_manager import IntradayManager
from api.serializers.stock_price_chart import SimplePriceItemSerializer
from core.models.stocks.stock_price_realtime import StockPriceRealtime
from core.services.open_trading.get_trading_order_type import (
    GetTradingOrderTypeService,
)

DATE_RANGES = ["1d", "1w", "1m", "3m", "1y", "5y", "all"]
HISTORICAL_DATE_RANGES = ["1w", "1m", "3m", "1y", "5y", "all"]


class StockPriceRealtimeSerializer(serializers.ModelSerializer):
    change_percentage = serializers.SerializerMethodField()
    change_value = serializers.SerializerMethodField()
    stock_name = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    stock_photo = ImageHandlerSerializer()

    class Meta:
        model = StockPriceRealtime
        fields = [
            "id",
            "symbol",
            "type",
            "datetime",
            "price",
            "change_percentage",
            "change_value",
            "volume",
            "total_trading_value",
            "exchange",
            "type",
            "stock_name",
            "stock_photo",
        ]

    def get_change_value(self, obj):
        if not obj.reference or not obj.price:
            return None

        return obj.price - obj.reference

    def get_change_percentage(self, obj):
        if not obj.reference or not obj.price:
            return None

        return ((obj.price - obj.reference) / obj.reference) * 100

    def get_stock_name(self, obj):
        return obj.stock_name
    
    def get_type(self, obj):
        if obj.type and isinstance(obj.type, str):
            return obj.type.lower()
        return ""


class PriceRealtimeSerializer(serializers.ModelSerializer):
    change_percentage = serializers.SerializerMethodField()
    change_value = serializers.SerializerMethodField()

    class Meta:
        model = StockPriceRealtime
        fields = [
            "id",
            "symbol",
            "datetime",
            "price",
            "change_percentage",
            "change_value",
            "volume",
            "total_trading_value",
            "exchange",
            "type",
        ]

    def get_change_value(self, obj):
        if not obj.reference or not obj.price:
            return None

        return obj.price - obj.reference

    def get_change_percentage(self, obj):
        if not obj.reference or not obj.price:
            return None

        return ((obj.price - obj.reference) / obj.reference) * 100


class StockPriceRealtimeDetailSerializer(serializers.ModelSerializer):
    change_percentage = serializers.SerializerMethodField()
    change_value = serializers.SerializerMethodField()
    prices = serializers.SerializerMethodField()
    date_ranges = serializers.SerializerMethodField()
    date_range = serializers.SerializerMethodField()

    class Meta:
        model = StockPriceRealtime
        fields = [
            "id",
            "symbol",
            "datetime",
            "price",
            "volume",
            "fb_volume",
            "fs_volume",
            "foreign_room",
            "open",
            "high",
            "low",
            "close",
            "reference",
            "floor",
            "ceiling",
            "total_trading_value",
            "change_percentage",
            "change_value",
            "prices",
            "date_range",
            "date_ranges",
            "exchange",
            "type",
        ]

    def __convert_timestamp_in_datetime_utc(self, timestamp_received):
        dt_naive_utc = datetime.utcfromtimestamp(timestamp_received)
        return dt_naive_utc.replace(tzinfo=pytz.utc)

    def __ensure_timestamp_movement(self, movement: list) -> list:
        new_movement = []
        for d in movement:
            d["t"] = self.__convert_timestamp_in_datetime_utc(d["t"])
            new_movement.append(d)
        return new_movement

    def get_change_percentage(self, obj):
        date_range = self.context.get("date_range", "1d")

        if not obj.reference or not obj.price or not date_range:
            return None

        date_range = str(date_range).lower()
        last_price = obj.reference

        if date_range in HISTORICAL_DATE_RANGES:
            analytics_data = self.context.get("analytics")

            if not analytics_data:
                return None

            last_price = analytics_data.price_1w
            if date_range == "1w":
                last_price = analytics_data.price_1w
            elif date_range == "1m":
                last_price = analytics_data.price_1m
            elif date_range == "3m":
                last_price = analytics_data.price_3m
            elif date_range == "1y":
                last_price = analytics_data.price_1y
            elif date_range == "3y":
                last_price = analytics_data.price_3y
            elif date_range == "5y":
                last_price = analytics_data.price_5y
            elif date_range == "ytd":
                last_price = analytics_data.price_ytd
            elif date_range == "all":
                # TODO: current dont support all for stocks
                if analytics_data.price_5y:
                    last_price = analytics_data.price_5y
                elif analytics_data.price_3y:
                    last_price = analytics_data.price_3y
                elif analytics_data.price_1y:
                    last_price = analytics_data.price_1y

            if not last_price:
                return None

        return ((obj.price - last_price) / last_price) * 100

    def get_change_value(self, obj):
        date_range = self.context.get("date_range", "1d")

        if not obj.reference or not date_range:
            return None

        date_range = str(date_range).lower()

        last_price = obj.reference

        if date_range in HISTORICAL_DATE_RANGES:
            analytics_data = self.context.get("analytics")

            if not analytics_data:
                return None

            last_price = analytics_data.price_1w

            if date_range == "1w":
                last_price = analytics_data.price_1w
            elif date_range == "1m":
                last_price = analytics_data.price_1m
            elif date_range == "3m":
                last_price = analytics_data.price_3m
            elif date_range == "1y":
                last_price = analytics_data.price_1y
            elif date_range == "3y":
                last_price = analytics_data.price_3y
            elif date_range == "5y":
                last_price = analytics_data.price_5y
            elif date_range == "ytd":
                last_price = analytics_data.price_ytd
            elif date_range == "all":
                # TODO: current dont support all for stocks
                if analytics_data.price_5y:
                    last_price = analytics_data.price_5y
                elif analytics_data.price_3y:
                    last_price = analytics_data.price_3y
                elif analytics_data.price_1y:
                    last_price = analytics_data.price_1y

            if not last_price:
                return None

        return obj.price - last_price

    def get_prices(self, obj):
        date_range = self.context.get("date_range", "1d")
        date_range = str(date_range).lower()
        data: list = []

        if date_range in HISTORICAL_DATE_RANGES:
            charts_data = self.context.get("charts")

            if not charts_data:
                return None

            history_movement = charts_data.movement_1w

            if date_range == "1w":
                history_movement = charts_data.movement_1w
            elif date_range == "1m":
                history_movement = charts_data.movement_1m
            elif date_range == "3m":
                history_movement = charts_data.movement_3m
            elif date_range == "1y":
                history_movement = charts_data.movement_1y
            elif date_range == "3y":
                history_movement = charts_data.movement_3y
            elif date_range == "5y":
                history_movement = charts_data.movement_5y
            elif date_range == "ytd":
                history_movement = charts_data.movement_ytd
            elif date_range == "all":
                # TODO: current dont support all for stocks
                if charts_data.movement_5y:
                    return charts_data.movement_5y
                elif charts_data.movement_3y:
                    return charts_data.movement_3y
                elif charts_data.movement_1y:
                    return charts_data.movement_1y
                return None

            if history_movement and len(history_movement) > 0:
                # encode raw data to datetime
                history_movement = self.__ensure_timestamp_movement(history_movement)

                # add the latest price to the historical data only if it has values
                # otherwise, just leave it an empty list
                data = history_movement + [{"c": obj.price, "v": obj.volume, "t": obj.datetime}]
        else:  # default set to 1d
            trading_order_types = GetTradingOrderTypeService(symbol=obj.symbol).call()
            is_ato_time = any(
                filter(
                    lambda item: item["is_active"] and item["type"] == "ATO", trading_order_types
                )
            )

            intraday_manager = IntradayManager()
            if is_ato_time:
                intraday_manager.init_ato_time(obj.reference)

            data = intraday_manager.get_and_build_chart_1d(symbol=obj.symbol)
            data = random_sampling(data)

        return SimplePriceItemSerializer(data, many=True).data

    def get_date_ranges(self, obj):
        return DATE_RANGES

    def get_date_range(self, obj):
        return self.context.get("date_range", "1d")


class StockPriceRealtimeNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockPriceRealtime
        fields = [
            "id",
            "symbol",
            "datetime",
            "price",
        ]
