import json
from utils import generate_competitor_list, analyze_price_band, build_swot


def run(params):
    product = params.get("product_name")
    market = params.get("market", "中国")
    platform = params.get("platform", "全渠道")
    count = int(params.get("competitor_count", 5))

    # 1. 获取竞品列表
    competitors = generate_competitor_list(product, count)

    # 2. 构建产品对比
    product_table = []
    for c in competitors:
        product_table.append({
            "brand": c,
            "price": "待分析",
            "spec": "待分析",
            "selling_point": "待分析"
        })

    # 3. 价格分析
    price_analysis = analyze_price_band(competitors)

    # 4. SWOT
    swot = build_swot(competitors)

    result = {
        "product": product,
        "market": market,
        "platform": platform,
        "competitors": competitors,
        "product_table": product_table,
        "price_analysis": price_analysis,
        "swot": swot
    }

    return json.dumps(result, ensure_ascii=False, indent=2)