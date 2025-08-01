from rest_framework import serializers

from core.models.stocks.stock_analytics import StockFA


# class StockFASerializer(LabelingKeyValueSerializer):
class StockFASerializer(serializers.ModelSerializer):
    label_mapping = {
        "symbol": "Mã Cổ Phiếu", "date": "Ngày cập nhật",
        "ev_ebitda": "EV/EBITDA", "ev_sales": "EV/SALES",
        "dividend": "Cổ tức (VND)",
        "profit_margin": "Biên lợi nhuận ròng", "gross_profit_to_sales": "Tỷ suất lợi nhuận",
        "debt_to_equity": "D/E (Nợ/Vốn chủ sở hữu)", "debt_to_asset": "D/A (Nợ/Tài sản)",
        "quick_ratio": "Thanh toán nhanh", "current_ratio": "Thanh toán hiện hành",
    }
    # `datatype` = numeric,percent,string,money
    datatype_mapping = {
        # v1
        'beta': 'numeric', 'eps': 'money', 'pe': 'numeric', 'pb': 'numeric',
        'ps': 'numeric',
        # v2
        'peg': 'numeric',
        'roa': 'percent', 'roe': 'percent', 'ros': 'percent',
        'ev_ebitda': 'numeric', 'ev_sales': 'numeric',
        'dividend': 'money',
        'profit_margin': 'percent', 'gross_profit_to_sales': 'percent',
        'debt_to_equity': 'percent', 'debt_to_asset': 'percent',
        'quick_ratio': 'percent', 'current_ratio': 'percent'
    }

    class Meta:
        model = StockFA
        fields = [
            'symbol', 'date', 'beta',
            'eps', 'pe', 'pb', 'ps',
            'peg',
            'roa', 'roe', 'ros',
            'ev_ebitda', 'ev_sales',
            'dividend',
            'profit_margin', 'gross_profit_to_sales',
            'debt_to_equity', 'debt_to_asset',
            'quick_ratio', 'current_ratio'
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        label_value_items = []
        for key, val in representation.items():
            if key not in self.label_mapping:
                # simple label key by remove underscore then upper the string
                label = key.replace("_", " ").upper()
            else:
                label = self.label_mapping[key]

            item = {
                "label": label,
                "key": key,
                "value": val,
                "datatype": self.datatype_mapping.get(key),
                # "ordering": 1
            }
            label_value_items.append(item)
        representation = {"items": label_value_items}

        return representation
