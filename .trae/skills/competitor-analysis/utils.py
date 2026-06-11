def generate_competitor_list(product, count):
    base_list = [
        f"{product}品牌A",
        f"{product}品牌B",
        f"{product}品牌C",
        f"{product}品牌D",
        f"{product}品牌E",
        f"{product}品牌F"
    ]
    return base_list[:count]


def analyze_price_band(competitors):
    return {
        "low": "0-20元",
        "mid": "20-50元",
        "high": "50元以上",
        "mainstream": "20-30元"
    }


def build_swot(competitors):
    result = {}
    for c in competitors:
        result[c] = {
            "strength": "品牌/渠道优势",
            "weakness": "产品同质化",
            "opportunity": "市场增长",
            "threat": "价格竞争"
        }
    return result