class FearGreedModelConfig:

    FEAR_GREED_LEVEL = {
        1: "Rất sợ hãi",
        2: "Sợ hãi",
        3: "Trung bình",
        4: "Tham lam",
        5: "Rất tham lam",
    }

    def _score_to_level(self, score):
        level = 3
        if 45 <= score < 55:
            level = 3
        elif 55 <= score < 75:
            level = 4
        elif 75 <= score:
            level = 5
        elif 25 <= score < 45:
            level = 2
        elif score < 25:
            level = 1

        return level

    def recommend_action_by_score(self, score):
        level = self._score_to_level(score)
        comment = ""
        action_recommend = ""
        if level == 1:
            comment = "Nhiều người tham gia thị trường đang bán, khiến giá giảm Điều này có thể tạo ra cơ hội mua tốt."
            action_recommend = "Mua"
        elif level == 2:
            comment = "Số người bán đang nhiều hơn người mua, thị trường đang có xu hướng giảm trong ngắn hạn."
            action_recommend = "Mua"
        elif level == 3:
            comment = "Thị trường ít biến động, người mua và người bán đang cân bằng nhau."
            action_recommend = "Quan sát thêm"
        elif level == 4:
            comment = "Mọi người đang bắt đầu có xu hướng mua vào, làm thị trường tăng nhẹ trong ngắn hạn."
            action_recommend = "Bán"
        elif level == 5:
            comment = "Nhiều nhà đầu tư đang mua nhiều, đang diễn ra tâm lý"
            action_recommend = "Bán"
        status = self.FEAR_GREED_LEVEL.get(level, "")
        return comment, action_recommend, status

    def gen_momentum_comment(self, market_value, market_sma, momentum_diff, last_time, update_time, sma_day=125):

        if market_value > market_sma:
            level = "cao"
            speed = "nhanh"
        else:
            level = "thấp"
            speed = "chậm"

        def _momentum_diff_to_level(score):
            level = 3
            if 0 <= score < 1:
                level = 3
            elif 1 <= score < 5:
                level = 4
            elif 5 <= score:
                level = 5
            elif -5 <= score < 0:
                level = 2
            elif score < -5:
                level = 1

            return level
        fear_level = self.FEAR_GREED_LEVEL.get(_momentum_diff_to_level(momentum_diff))
        last_change = last_time.strftime('ngày %d tháng %m')
        update = update_time.strftime('ngày %d tháng %m lúc %H:%M')

        text = """
        Chỉ số VN30 {level} hơn {momentum_diff}% so với mức trung bình {sma_day} ngày.
        Điều này cho thấy nhà đầu đang tư rót vốn vào thị trường {speed} hơn so với trước đây.
        Thay đổi lần cuối vào {last_change} từ xếp hạng {fear_level}
        Cập nhật {update}
        """.format(
            level=level,
            sma_day=sma_day,
            speed=speed,
            momentum_diff=abs(momentum_diff),
            fear_level=fear_level,
            last_change=last_change,
            update=update
        )
        text = "Cập nhật {update}".format(update=update)
        text = f"{fear_level}"
        return text, fear_level

    def gen_market_volatility_comment(self, market_volatility, market_diff, market_volatility_sma, last_time, update_time):

        # diff = round((market_volatility - last_market_volatility) / market_volatility, 2)
        diff = abs(market_diff)
        # diff = market_volatility
        fear_lv = 3
        level = "trung bình"
        if market_volatility < 0.005:
            level = "thấp"
        elif market_volatility < 0.01:
            level = "trung bình"
            fear_lv = 2
        else:
            level = "cao"
            fear_lv = 1

        # vola_vs_sma = market_volatility - market_volatility_sma
        def _momentum_diff_to_level(score):
            level = 3
            if 0 <= score <= 1:
                level = 3
            elif 1 < score < 5:
                level = 4
            elif 5 <= score:
                level = 5
            elif -5 <= score < 0:
                level = 2
            elif score < -5:
                level = 1

            return level
        fear_lv = _momentum_diff_to_level(market_diff * 100)
        market_volatility = round(market_volatility, 2) * 100

        if market_diff > 0:
            vector = "tăng"
        else:
            vector = "giảm"
        last_change = last_time.strftime('ngày %d tháng %m')
        update = update_time.strftime('ngày %d tháng %m lúc %H:%M')
        diff = abs(round(diff, 2)) * 100

        fear_level = self.FEAR_GREED_LEVEL.get(fear_lv)
        text = """
        "Chỉ số Biến động thị trường ở mức {market_volatility}% {vector} {market_diff}% so với phiên trước . 
        Điều này chỉ ra rằng rủi ro thị trường có vẻ {level}.
        Thay đổi lần cuối vào {last_change} từ xếp hạng {fear_level}.
        """.format(
            market_volatility=market_volatility,
            vector=vector,
            level=level,
            market_diff=market_diff,
            last_change=last_change,
            fear_level=fear_level
        )
        text = "Cập nhật {update}".format(update=update)
        text = f"{fear_level}"
        return text, fear_level


    def gen_price_strength_comment(self, price_strength, last_price_strength, last_time, update_time):
        price_strength = price_strength

        if price_strength > last_price_strength:
            level = "cao"
        else:
            level = "thấp"

        fear_idx = 3
        if price_strength < 30:
            mess = "khối tài sản giao dịch đang bị bán quá mức và có thể phục hồi"
            fear_idx = 5
        elif 30 <= price_strength <= 50:
            mess = "dấu hiệu của một xu hướng giảm mới trong thị trường"
            fear_idx = 2
        elif 50 < price_strength <= 70:
            mess = "thị trường chưa xác định xu hướng"
            fear_idx = 3
        else:
            mess = "thị trường đang bị mua vượt mức và có thể điều chỉnh giảm"
            fear_idx = 4

        fear_level = self.FEAR_GREED_LEVEL.get(fear_idx)
        last_change = last_time.strftime('ngày %d tháng %m')
        update = update_time.strftime('ngày %d tháng %m lúc %H:%M')

        diff = round((price_strength-last_price_strength) / price_strength, 2)
        diff = abs(diff) * 100

        text = """
        Chỉ số sức mạnh giá tương đối đang ở mức {price_strength}% , {level} hơn {diff}% so với phiên trước. 
        Điều này cho thấy {mess}
        Thay đổi lần cuối vào {last_change} từ xếp hạng {fear_level}
        Cập nhật {update}

        """.format(
            price_strength=price_strength,
            level=level,
            diff=diff,
            mess=mess,
            fear_level=fear_level,
            last_change=last_change,
            update=update
        )
        text = "Cập nhật {update}".format(update=update)
        text = f"{fear_level}"
        return text, fear_level

    def gen_price_breadth_comment(self, price_breadth, last_price_breadth, last_time, update_time):

        diff = ((price_breadth - last_price_breadth) / price_breadth)
        if diff > 0:
            level = "cao"
        else:
            level = "thấp"

        if price_breadth < 0.3:
            mess = "số lượng cổ phiếu tăng giá đang ít, thị trường giá giảm"
            fear_idx = 1
        elif 0.3 <= price_breadth <= 0.5:
            mess = "số lượng cổ phiếu tăng giá đang ở mức trung bình"
            fear_idx = 2
        elif 0.5 < price_breadth <= 0.6:
            mess = "thị trường chưa xác định xu hướng"
            fear_idx = 3
        else:
            mess = "số lượng cổ phiếu tăng giá đang ở mức cao, có thể điều chỉnh giảm"
            fear_idx = 4

        diff = abs(round(diff, 2)) * 100
        price_breadth = abs(round(price_breadth, 2)) * 100
        fear_level = self.FEAR_GREED_LEVEL.get(fear_idx)

        last_change = last_time.strftime('ngày %d tháng %m')
        update = update_time.strftime('ngày %d tháng %m lúc %H:%M')
        text = """
        Tỷ lệ cổ phiếu giá cao và giá thấp trong 52 tuần ở mức {price_breadth}% , {level} hơn {diff}% so với phiên trước. 
        Điều này cho thấy {mess}
        Thay đổi lần cuối vào {last_change} từ xếp hạng {fear_level}
        Cập nhật {update}
        """.format(
            price_breadth=price_breadth,
            level=level,
            diff=diff,
            mess=mess,
            fear_level=fear_level,
            last_change=last_change,
            update=update
        )
        text = "Cập nhật {update}".format(update=update)
        text = f"{fear_level}"
        return text, fear_level
