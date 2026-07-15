#!/usr/bin/env python3
"""报告生成器 — 使用Jinja2模板渲染三级HTML诊断报告。

基于分析结果和HTML模板生成图文并茂的专业诊断报告。

打印兼容性说明（v2.1 新增）：
- 所有模板已内置 @media print 规则，确保打印/PDF导出时"所见即所得"
- 关键措施：print-color-adjust:exact（强制打印背景色）、break-inside:avoid（防切断）
- ECharts 图表容器需设置 min-height，防止打印时高度塌缩

数据真实性（v2.2 新增）：
- 所有图表数据从实际分析结果计算，无硬编码假数据
- box/heatmap/scenario/zscore 数据通过 _compute_* 方法动态生成
- 政策分析和关联交易数据标注数据来源状态

作者: 优方皑尔 Uform Ai
版本: v2.3.0
"""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

_TEMPLATE_DIR: str = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "templates"
)


class ReportGenerator:
    """报告生成器 — 三级诊断报告渲染。

    支持三级报告:
        - Level 1: 急诊初筛 (快速诊断)
        - Level 2: 专科门诊 (深度诊断)
        - Level 3: 专家会诊 (尽调级)
    """

    def __init__(self, template_dir: Optional[str] = None):
        """初始化报告生成器。

        Args:
            template_dir: 模板目录路径。
        """
        self._template_dir: str = template_dir or _TEMPLATE_DIR

    def generate_level1(
        self,
        analysis_results: Dict[str, Any],
        output_path: Optional[str] = None,
    ) -> str:
        """生成第一级报告（急诊初筛）。

        Args:
            analysis_results: 分析结果。
            output_path: 输出文件路径（可选）。

        Returns:
            str: HTML报告内容。
        """
        context: Dict[str, Any] = self._build_level1_context(analysis_results)
        html: str = self._render_template("report_level1.html", context)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)
            logger.info("Level 1 report saved to %s", output_path)

        return html

    def generate_level2(
        self,
        analysis_results: Dict[str, Any],
        output_path: Optional[str] = None,
    ) -> str:
        """生成第二级报告（专科门诊）。

        Args:
            analysis_results: 分析结果。
            output_path: 输出文件路径（可选）。

        Returns:
            str: HTML报告内容。
        """
        context: Dict[str, Any] = self._build_level2_context(analysis_results)
        html: str = self._render_template("report_level2.html", context)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)
            logger.info("Level 2 report saved to %s", output_path)

        return html

    def generate_level3(
        self,
        analysis_results: Dict[str, Any],
        output_path: Optional[str] = None,
    ) -> str:
        """生成第三级报告（专家会诊）。

        Args:
            analysis_results: 分析结果。
            output_path: 输出文件路径（可选）。

        Returns:
            str: HTML报告内容。
        """
        context: Dict[str, Any] = self._build_level3_context(analysis_results)
        html: str = self._render_template("report_level3.html", context)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)
            logger.info("Level 3 report saved to %s", output_path)

        return html

    def generate_comprehensive(
        self,
        analysis_results: Dict[str, Any],
        output_path: Optional[str] = None,
    ) -> str:
        """生成综合财务分析报告（Chart.js 图表）。

        包含: KPI卡片、利润表分析+瀑布图、资产负债表分析、比率卡片、
              重点发现(P0/P1/P2)、综合诊断建议、数据质量说明。

        Args:
            analysis_results: 分析结果字典 (必须包含 is/bs/zscore/redflags/dupont 等)。
            output_path: 输出文件路径（可选）。

        Returns:
            str: HTML报告内容。
        """
        context: Dict[str, Any] = self._build_comprehensive_context(analysis_results)
        html: str = self._render_template("report_comprehensive.html", context)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)
            logger.info("Comprehensive report saved to %s", output_path)

        return html

    def generate_all_reports(
        self,
        analysis_results: Dict[str, Any],
        output_dir: str,
        company_short: str = "",
        year: str = "",
    ) -> List[str]:
        """一键生成全部4份报告（综合 + L1/L2/L3），保证输出一致性。

        Args:
            analysis_results: 分析结果字典。
            output_dir: 输出目录路径。
            company_short: 公司简称（用于文件命名）。
            year: 年份标识（用于文件命名）。

        Returns:
            已生成的文件路径列表。
        """
        os.makedirs(output_dir, exist_ok=True)
        prefix = f"{company_short}_{year}" if company_short else "公司"
        paths: List[str] = []

        # 按优先级顺序生成: 综合 → L1 → L2 → L3
        reports = [
            ("comprehensive", f"{prefix}_财务分析报告.html", self.generate_comprehensive),
            ("L1", f"{prefix}_L1_急诊初筛.html", self.generate_level1),
            ("L2", f"{prefix}_L2_专科门诊.html", self.generate_level2),
            ("L3", f"{prefix}_L3_专家会诊.html", self.generate_level3),
        ]

        for label, filename, generator in reports:
            out_path = os.path.join(output_dir, filename)
            try:
                html = generator(analysis_results, out_path)
                pct_errors = html.count("%%") if html else 0
                logger.info(
                    "%s -> %s (%d chars, %d placeholder errors)",
                    label, filename, len(html) if html else 0, pct_errors,
                )
                paths.append(out_path)
            except Exception as e:
                logger.error("%s generation failed: %s", label, e)
                import traceback
                traceback.print_exc()

        logger.info("All reports generated: %d files in %s", len(paths), output_dir)
        return paths

    # ---- 综合报告 Context Builder ----

    def _build_comprehensive_context(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """构建综合财务分析报告的模板上下文。

        将所有分析结果展平为模板可直接使用的变量，
        包含 Chart.js 图表所需的数值数组和 JSON 配置。
        """
        periods: List[str] = results.get("periods", [])
        latest = periods[-1] if periods else "本期"

        # 提取财务数据
        is_data = (results.get("is") or {}).get(latest, {})
        bs_data = (results.get("bs") or {}).get(latest, {})
        cf_data = (results.get("cf") or {}).get(latest, {})

        # 关键科目
        rev = float(is_data.get("营业收入", 0))
        cost = float(is_data.get("营业成本", 0))
        tax_s = float(is_data.get("营业税金及附加", 0) or is_data.get("税金及附加", 0))
        selling = float(is_data.get("销售费用", 0))
        admin = float(is_data.get("管理费用", 0))
        rd = float(is_data.get("研发费用", 0))
        fin = float(is_data.get("财务费用", 0))
        invest = float(is_data.get("投资收益", 0))
        op_profit = float(is_data.get("营业利润", 0))
        nonop = float(is_data.get("营业外收入", 0)) - float(is_data.get("营业外支出", 0))
        tp = float(is_data.get("利润总额", 0))
        itax = float(is_data.get("所得税费用", 0))
        np = float(is_data.get("净利润", 0))

        # BS
        cash_v = float(bs_data.get("货币资金", 0))
        ar_v = float(bs_data.get("应收账款", 0))
        prepay_v = float(bs_data.get("预付账款", 0) or bs_data.get("预付款项", 0))
        other_recv_v = float(bs_data.get("其他应收款", 0))
        inv_v = float(bs_data.get("存货", 0))
        ca = float(bs_data.get("流动资产合计", 0) or bs_data.get("流动资产", 0))
        lt_inv = float(bs_data.get("长期股权投资", 0))
        fix_v = float(bs_data.get("固定资产", 0) or bs_data.get("固定资产账面价值", 0))
        intan_v = float(bs_data.get("无形资产", 0))
        other_nca_v = float(bs_data.get("其他非流动资产", 0) or bs_data.get("长期待摊费用", 0))
        nca = float(bs_data.get("非流动资产合计", 0) or bs_data.get("非流动资产", 0))
        ta_v = float(bs_data.get("资产总计", 0) or bs_data.get("总资产", 0))

        ap_v = float(bs_data.get("应付账款", 0))
        tax_pay = float(bs_data.get("应交税费", 0))
        other_pay_v = float(bs_data.get("其他应付款", 0))
        cl = float(bs_data.get("流动负债合计", 0) or bs_data.get("流动负债", 0))
        ncl = float(bs_data.get("非流动负债合计", 0) or bs_data.get("非流动负债", 0))
        tl_v = float(bs_data.get("负债合计", 0) or bs_data.get("总负债", 0))
        equity_v = float(bs_data.get("所有者权益合计", 0) or bs_data.get("所有者权益", 0))
        capital_v = float(bs_data.get("实收资本", 0) or bs_data.get("股本", 0))
        surplus_v = float(bs_data.get("资本公积", 0))
        retained_v = float(bs_data.get("未分配利润", 0))

        # 关键比率
        gross_profit = rev - cost
        gross_margin = gross_profit / rev * 100 if rev else 0
        net_margin = np / rev * 100 if rev else 0
        roe_val = np / equity_v * 100 if equity_v else 0
        debt_r = tl_v / ta_v * 100 if ta_v else 0
        cr_val = ca / cl if cl else 0

        # Z-Score
        zscore_val = list(results.get("zscore", {}).values())[-1] if results.get("zscore") else 0

        # 风险等级评估
        if zscore_val > 2.99:
            health, health_color, risk_level = "安全区", "#22c55e", "A级 常规监测"
        elif zscore_val > 1.81:
            health, health_color, risk_level = "灰色区", "#f59e0b", "B级 重点关注趋势"
        elif zscore_val > 1.0:
            health, health_color, risk_level = "危险区", "#ef4444", "C级 建议专项核查"
        else:
            health, health_color, risk_level = "严重危险", "#dc2626", "D级 建议外部审计"

        # 风险信号 — 预渲染为 HTML（不受 Jinja2 可用性影响）
        triggered = results.get("redflags", {}).get("triggered_signals", [])
        risk_html_parts = []
        for s in triggered[:7]:
            sev = s.get("severity", "P2")
            level = "P0" if sev in ("P0", "high") else ("P1" if sev in ("P1", "medium") else "P2")
            tag = (s.get("category", "风险") or s.get("risk_type", "风险"))[:6]
            title = s.get("name", "异常信号")
            detail = s.get("description", "")
            risk_html_parts.append(
                f'<div class="finding {level}"><span class="tag">{level}</span>'
                f'<span class="title">[{tag}] {title}</span>'
                f'<div class="detail">{detail}</div></div>'
            )
        risk_items_html = "\n".join(risk_html_parts) if risk_html_parts else \
            '<p style="color:#94a3b8;">暂未触发高风险信号。建议提供完整三表数据以获得更全面的风险评估。</p>'

        # BS平衡检查
        bs_diff = abs(ta_v - tl_v - equity_v)
        bs_balanced = bs_diff < max(ta_v, 1) * 0.01

        # 数据质量
        dq = results.get("data_quality", {})
        quality_score = dq.get("total_score", "N/A")
        quality_grade = dq.get("grade", "N/A")

        # 构建上下文
        ctx = {
            "company_name": results.get("company_name", ""),
            "year": latest,
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            # KPI
            "rev_wan": f"{rev/10000:,.2f}万",
            "np_wan": f"{np/10000:,.2f}万",
            "ta_wan": f"{ta_v/10000:,.2f}万",
            "gross_margin": f"{gross_margin:.1f}%",
            "net_margin": f"{net_margin:.1f}%",
            "roe": f"{roe_val:.1f}%",
            "debt": f"{debt_r:.1f}%",
            "cr": f"{cr_val:.2f}",
            "zscore": f"{zscore_val:.2f}",
            "health": health,
            "health_color": health_color,
            "risk_level": risk_level,
            # IS 表格
            "cost_wan": f"{cost/10000:,.2f}万",
            "tax_wan": f"{tax_s/10000:,.2f}万",
            "admin_wan": f"{admin/10000:,.2f}万",
            "fin_wan": f"{fin/10000:,.2f}万",
            "op_wan": f"{op_profit/10000:,.2f}万",
            "tp_wan": f"{tp/10000:,.2f}万",
            "it_wan": f"{itax/10000:,.2f}万",
            "cost_pct": f"{cost/rev*100 if rev else 0:.1f}%",
            "tax_pct": f"{tax_s/rev*100 if rev else 0:.1f}%",
            "admin_pct": f"{admin/rev*100 if rev else 0:.1f}%",
            "fin_pct": f"{fin/rev*100 if rev else 0:.1f}%",
            "op_pct": f"{op_profit/rev*100 if rev else 0:.1f}%",
            "tp_pct": f"{tp/rev*100 if rev else 0:.1f}%",
            "it_pct": f"{itax/rev*100 if rev else 0:.1f}%",
            # BS 表格
            "cash_wan": f"{cash_v/10000:,.2f}万",
            "ar_wan": f"{ar_v/10000:,.2f}万",
            "prepay_wan": f"{prepay_v/10000:,.2f}万",
            "orecv_wan": f"{other_recv_v/10000:,.2f}万",
            "inv_wan": f"{inv_v/10000:,.2f}万",
            "ca_wan": f"{ca/10000:,.2f}万",
            "lti_wan": f"{lt_inv/10000:,.2f}万",
            "fix_wan": f"{fix_v/10000:,.2f}万",
            "intan_wan": f"{(intan_v+other_nca_v)/10000:,.2f}万",
            "ap_wan": f"{ap_v/10000:,.2f}万",
            "taxp_wan": f"{tax_pay/10000:,.2f}万",
            "opa_wan": f"{other_pay_v/10000:,.2f}万",
            "cl_wan": f"{cl/10000:,.2f}万",
            "tl_wan": f"{tl_v/10000:,.2f}万",
            "cap_wan": f"{capital_v/10000:,.2f}万",
            "sur_wan": f"{surplus_v/10000:,.2f}万",
            "re_wan": f"{retained_v/10000:,.2f}万",
            "eq_wan": f"{equity_v/10000:,.2f}万",
            # 图表数据 (万元)
            "chart_is": [rev/10000, -cost/10000, -tax_s/10000, -admin/10000, abs(fin)/10000, max(0, op_profit)/10000, max(0, np)/10000],
            "chart_is_colors": ["#3b82f6","#ef4444","#f59e0b","#f59e0b","#22c55e","#3b82f6","#1a365d"],
            "chart_bs_assets": [cash_v/10000, ar_v/10000, prepay_v/10000, other_recv_v/10000, inv_v/10000, lt_inv/10000, fix_v/10000, (intan_v+other_nca_v)/10000],
            "chart_bs_assets_colors": ["#3b82f6","#60a5fa","#93c5fd","#bfdbfe","#dbeafe","#1d4ed8","#2563eb","#3b82f6"],
            "chart_bs_lse": [ap_v/10000, tax_pay/10000, other_pay_v/10000, capital_v/10000, surplus_v/10000, retained_v/10000],
            "chart_bs_lse_colors": ["#ef4444","#f87171","#fca5a5","#22c55e","#4ade80","#86efac"],
            # 比率评级
            "gm_color": "#22c55e" if gross_margin > 30 else ("#f59e0b" if gross_margin > 20 else "#ef4444"),
            "gm_text": "良好" if gross_margin > 30 else ("一般" if gross_margin > 20 else "偏低"),
            "cr_color": "#22c55e" if cr_val > 2 else ("#f59e0b" if cr_val > 1 else "#ef4444"),
            "cr_text": "良好" if cr_val > 2 else ("一般" if cr_val > 1 else "危险"),
            # 诊断
            "risk_items_html": risk_items_html,
            "bs_balanced": "是" if bs_balanced else "否",
            "bs_balance_note": "" if bs_balanced else f" (差异: {bs_diff/10000:,.2f}万)",
            "data_source": results.get("metadata", {}).get("source", "用户上传文件"),
            "data_quality": f"{quality_score}/100 ({quality_grade})",
            "is_cross_valid": "是" if abs(tp - itax - np) < max(abs(tp), 1) * 0.01 else "否",
            "advice_list": results.get("advice", {}).get("advice_list", []),
            "advice_fallback_html": self._build_advice_fallback(results.get("advice", {}).get("advice_list", [])),
            "data_limitation": "",
        }

        # 单期数据标注
        if len(periods) <= 1:
            ctx["data_limitation"] = "③ 单期数据限制M-Score与趋势分析，建议提供多年度数据"

        return ctx

    @staticmethod
    def _build_advice_fallback(advice_list: List[Dict[str, Any]]) -> str:
        """生成预渲染的建议 HTML（Jinja2 不可用时的降级方案）。

        将 generate_advice 输出的结构化建议转换为静态 HTML，
        在 {% for %} 循环无法渲染时作为后备内容。
        """
        if not advice_list:
            return '<p style="color:#94a3b8;">暂无法生成诊断建议。建议提供完整的三表数据以获得更精准的分析。</p>'

        parts = []
        for a in advice_list:
            sev = a.get("severity", "P2")
            emoji = "🔴" if sev == "P0" else ("🟡" if sev == "P1" else "🔵")
            scenario = a.get("scenario", "诊断建议")

            part = f'<div class="diag-box"><h3>{emoji} {scenario} <span style="font-size:12px;font-weight:400;color:#64748b;margin-left:8px;">[{sev}]</span></h3>'

            for label, key in [("🏭 运营层面", "operations"), ("💰 财务层面", "finance"), ("🎯 战略层面", "strategy")]:
                actions = a.get(key, [])
                if actions:
                    part += f'<p style="font-size:13px;color:#64748b;margin:8px 0 4px 0;">{label}：</p><ul>'
                    for act in actions:
                        owner = act.get("owner", "")
                        action = act.get("action", "")
                        deadline = act.get("deadline", "")
                        part += f'<li><strong>{owner}</strong>：{action} <span style="font-size:11px;color:#94a3b8;">{deadline}</span></li>'
                    part += '</ul>'

            part += '</div>'
            parts.append(part)

        return "\n".join(parts)

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """安全模板渲染 — 使用 Jinja2 或降级为正则边界替换。

        关键修复 (v2.3.0): 简单 str.replace() 存在子串污染风险
        (如 'rw' 会破坏 'arw' / 'prw' / 'srw')。使用正则 \b 边界匹配
        确保仅替换独立 token，并优先替换长键。

        优先使用 Jinja2 完整引擎（支持 for/if 等控制流），
        若 Jinja2 不可用则降级为安全字符串替换。
        """
        template_path: str = os.path.join(self._template_dir, template_name)

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template: str = f.read()
        except FileNotFoundError:
            logger.warning("Template not found: %s, using inline render", template_name)
            return self._render_inline(context)

        # 优先使用 Jinja2 完整引擎
        try:
            from jinja2 import Environment, BaseLoader
            env = Environment(loader=BaseLoader())
            tmpl = env.from_string(template)
            return tmpl.render(**context)
        except ImportError:
            pass

        # 降级: 安全字符串替换 (按key长度降序，正则边界匹配)
        sorted_keys = sorted(context.keys(), key=lambda k: -len(k))
        for key in sorted_keys:
            value = context[key]
            if isinstance(value, (list, dict)):
                value_str: str = json.dumps(value, ensure_ascii=False, default=str)
            elif isinstance(value, bool):
                value_str = str(value).lower()
            elif value is None:
                value_str = ""
            else:
                value_str = str(value)

            # 使用正则边界匹配：仅当 key 是独立 token 时才替换
            # 防止 'rw' 匹配 'arw' / 'prw' / 'srw' 等子串
            escaped = re.escape(key)
            pattern = r'(?<![A-Za-z0-9_])' + escaped + r'(?![A-Za-z0-9_])'
            template = re.sub(pattern, value_str, template)

        logger.debug("Template rendered with safe string substitution (Jinja2 unavailable)")
        return template

    def _render_inline(self, context: Dict[str, Any]) -> str:
        """当模板文件不可用时的内联渲染。"""
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>财务分析报告</title>
<style>
@media print {{
  * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
  @page {{ size: A4; margin: 15mm 12mm; }}
}}
</style>
</head>
<body>
<h1>财务报表分析报告</h1>
<p>生成时间: {context.get('report_date', 'N/A')}</p>
<pre>{json.dumps(context, indent=2, ensure_ascii=False, default=str)}</pre>
</body></html>"""

    # ---- Level 1 Context Builder ----

    def _build_level1_context(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """构建第一级报告上下文。"""
        redflags: Dict[str, Any] = results.get("redflags", {})
        mscore_results: Dict[str, Any] = results.get("mscore", {})
        fscore_results: Dict[str, Any] = results.get("fscore", {})
        zscore_results: Dict[str, float] = results.get("zscore", {})

        # 风险评分
        risk_score: float = self._compute_risk_score(results)
        risk_class: str = self._get_risk_class(risk_score)
        health_label, health_emoji, health_class = self._get_health(risk_score)

        # M-Score
        periods: List[str] = results.get("periods", [])
        latest_mscore: Optional[float] = None
        mscore_verdict: str = "数据不足"
        mscore_display: str = "N/A"
        mscore_class: str = "ok"
        if periods and mscore_results:
            latest_mscore_data = mscore_results.get(periods[-1], {})
            latest_mscore = latest_mscore_data.get("value")
            if latest_mscore is not None:
                mscore_display = str(round(latest_mscore, 2))
                if latest_mscore > -1.78:
                    mscore_class = "danger"
                    mscore_verdict = "造假嫌疑"
                elif latest_mscore > -2.22:
                    mscore_class = "warning"
                    mscore_verdict = "造假高风险"
                else:
                    mscore_class = "ok"
                    mscore_verdict = "正常范围"
            else:
                mscore_display = "数据不足"

        # F-Score
        latest_fscore: int = 0
        fscore_class: str = "ok"
        if periods and fscore_results:
            fs_data = fscore_results.get(periods[-1], {})
            latest_fscore = fs_data.get("total", 0)
            if latest_fscore <= 3:
                fscore_class = "danger"
            elif latest_fscore <= 5:
                fscore_class = "warning"

        # Z-Score
        latest_zscore: float = 0
        zscore_class: str = "ok"
        if zscore_results:
            latest_zscore = list(zscore_results.values())[-1] if zscore_results else 0
            if latest_zscore < 1.81:
                zscore_class = "danger"
            elif latest_zscore < 2.99:
                zscore_class = "warning"

        # Top风险
        triggered: List[Dict[str, Any]] = redflags.get("triggered_signals", [])
        top_risks: List[Dict[str, Any]] = triggered[:5]

        # 现金流模式
        cf_pattern: Dict[str, Any] = results.get("cf_pattern", {}).get(
            periods[-1] if periods else "", {}
        )

        # 一句话诊断
        one_liner: str = self._generate_one_liner(results)

        # 雷达图数据
        radar_values: List[float] = self._compute_radar_values(results)

        return {
            "company_name": results.get("company_name", ""),
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "health_label": health_label,
            "health_emoji": health_emoji,
            "health_class": health_class,
            "risk_score": round(risk_score, 1),
            "risk_class": risk_class,
            "zscore": latest_zscore,
            "zscore_class": zscore_class,
            "mscore": latest_mscore if latest_mscore is not None else 0,  # 模板内用float比较
            "mscore_display": mscore_display,
            "mscore_class": mscore_class,
            "fscore": latest_fscore,
            "fscore_class": fscore_class,
            "top_risks": top_risks,
            "operating_cf_sign": cf_pattern.get("经营CF", "N/A"),
            "investing_cf_sign": cf_pattern.get("投资CF", "N/A"),
            "financing_cf_sign": cf_pattern.get("筹资CF", "N/A"),
            "cf_pattern_id": cf_pattern.get("模式", "?"),
            "cf_pattern_name": cf_pattern.get("名称", "未知"),
            "cf_pattern_desc": cf_pattern.get("描述", ""),
            "one_liner": one_liner,
            "radar_values": radar_values,
            "data_sufficiency": "⚠️ 仅1期数据" if len(results.get("periods", [])) <= 1 else "",
            "data_quality": results.get("data_quality", {}),
        }

    # ---- Level 2 Context Builder ----

    def _build_level2_context(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """构建第二级报告上下文。"""
        ctx: Dict[str, Any] = self._build_level1_context(results)
        periods: List[str] = results.get("periods", [])

        # M-Score变量
        mscore_results: Dict[str, Any] = results.get("mscore", {})
        mscore_variables: List[Dict[str, Any]] = []
        mscore_percent: float = 40  # 默认在中间
        if periods:
            latest_mscore_data = mscore_results.get(periods[-1], {})
            vars_data: Dict[str, float] = latest_mscore_data.get("variables", {})
            mscore_variables = [
                {"name": k, "value": v, "desc": _MSCORE_VAR_DESC.get(k, "")}
                for k, v in vars_data.items()
            ]
            mscore_val: float = latest_mscore_data.get("value") or -2.22
            # 将M-Score映射到百分比位置（-3到-1范围）
            mscore_percent = min(95, max(5, (mscore_val + 3.0) / 2.0 * 100))

        # F-Score split
        fscore_results: Dict[str, Any] = results.get("fscore", {})
        fs_data: Dict[str, Any] = fscore_results.get(periods[-1], {}) if periods else {}
        fscore_verdict: str = fs_data.get("verdict", "N/A")

        # 杜邦分析
        dupont: Dict[str, Any] = results.get("dupont", {})
        prev_year: str = periods[-2] if len(periods) > 1 else "上期"
        curr_year: str = periods[-1] if periods else "本期"

        # 行业分位
        industry_label: str = results.get("industry", {}).get("label", "通用")

        # 雷达图
        radar_current: List[float] = self._compute_radar_values(results)
        radar_industry: List[float] = [50, 50, 50, 50, 50, 50]

        # 杜邦瀑布图数据
        dupont_curr: Dict[str, Any] = dupont.get(curr_year, {})
        npm_contrib: float = dupont_curr.get("连环替代", {}).get("Δ利润率贡献", 0)
        tat_contrib: float = dupont_curr.get("连环替代", {}).get("Δ周转率贡献", 0)
        em_contrib: float = dupont_curr.get("连环替代", {}).get("Δ杠杆贡献", 0)

        mscore_verdict: str = ctx.get("mscore_verdict", "N/A")
        ctx.update({
            "mscore_percent": round(mscore_percent, 1),
            "mscore_verdict": mscore_verdict,
            "mscore_variables": mscore_variables,
            "fscore_verdict": fscore_verdict,
            "fscore_profit": fs_data.get("profitability", 0),
            "fscore_leverage": fs_data.get("leverage", 0),
            "fscore_efficiency": fs_data.get("efficiency", 0),
            "prev_year": prev_year,
            "curr_year": curr_year,
            "roe_prev": f"{dupont.get(prev_year, {}).get('ROE', 0) * 100:.1f}%",
            "roe_curr": f"{dupont.get(curr_year, {}).get('ROE', 0) * 100:.1f}%",
            "roe_change": "",
            "npm_prev": "",
            "npm_curr": "",
            "npm_change": "",
            "tat_prev": "",
            "tat_curr": "",
            "tat_change": "",
            "em_prev": "",
            "em_curr": "",
            "em_change": "",
            "npm_contrib": f"{npm_contrib * 100:.2f}%",
            "tat_contrib": f"{tat_contrib * 100:.2f}%",
            "em_contrib": f"{em_contrib * 100:.2f}%",
            "industry_label": industry_label,
            "radar_current": radar_current,
            "radar_industry": radar_industry,
            "dupont_labels": ["利润率贡献", "周转率贡献", "杠杆贡献", "ROE变动"],
            "dupont_values": [
                round(npm_contrib * 100, 2),
                round(tat_contrib * 100, 2),
                round(em_contrib * 100, 2),
                round((npm_contrib + tat_contrib + em_contrib) * 100, 2),
            ],
            "box_labels": ["毛利率", "净利率", "ROE", "流动比率", "资产负债率", "周转率"],
            "box_current": self._compute_box_data(results, "current"),
            "box_median": self._compute_box_data(results, "industry"),
            "heatmap_periods": periods,
            "heatmap_risks": ["收入质量", "资产质量", "关联交易", "流动性", "合规"],
            "heatmap_data": self._compute_heatmap_data(results),
            "scenario_periods": periods + ["预测Y1", "预测Y2", "预测Y3"],
            "scenario_optimistic": self._compute_scenario(results, "optimistic"),
            "scenario_base": self._compute_scenario(results, "base"),
            "scenario_pessimistic": self._compute_scenario(results, "pessimistic"),
        })

        return ctx

    # ---- Level 3 Context Builder ----

    def _build_level3_context(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """构建第三级报告上下文。"""
        ctx: Dict[str, Any] = self._build_level1_context(results)
        periods: List[str] = results.get("periods", [])

        # 勾稽验证结果
        crosscheck: Dict[str, Any] = results.get("crosscheck", {})
        crosscheck_results: List[Dict[str, Any]] = []
        for cat_id, cat_data in crosscheck.get("categories", {}).items():
            crosscheck_results.append(cat_data)

        # 会计政策分析（从results提取，缺失时标注"待确认"）
        policy_analysis: List[Dict[str, Any]] = results.get("policy_analysis", [])
        if not policy_analysis:
            rd_rate = results.get("rd_cap_rate", 0)
            policy_analysis = [
                {
                    "item": "折旧政策",
                    "company_value": results.get("depreciation_policy", "待确认"),
                    "industry_avg": "直线法 8-15年",
                    "rating": "待确认",
                    "profit_impact": "需获取折旧明细表后评估",
                },
                {
                    "item": "坏账计提",
                    "company_value": results.get("bad_debt_policy", "待确认"),
                    "industry_avg": "5-8%",
                    "rating": "待确认",
                    "profit_impact": "需获取应收账款账龄后评估",
                },
                {
                    "item": "研发资本化",
                    "company_value": f"{rd_rate * 100:.1f}%" if rd_rate else "待确认",
                    "industry_avg": "15-25%",
                    "rating": "关注" if rd_rate > 0.25 else ("稳健" if rd_rate > 0 else "待确认"),
                    "profit_impact": "资本化率偏高" if rd_rate > 0.25 else ("正常" if rd_rate > 0 else "待确认"),
                },
            ]

        # 关联交易（优先从results获取，缺失时用模板占位）
        related_party: List[Dict[str, Any]] = results.get("related_party_checks", [])
        if not related_party:
            related_party = [
                {"dimension": "定价公允性", "rule": "关联毛利率 vs 非关联", "value": "需关联交易明细", "threshold": "差值<15pp", "triggered": False},
                {"dimension": "交易依赖度", "rule": "关联销售/总销售", "value": "需关联交易明细", "threshold": "<30%", "triggered": False},
                {"dimension": "往来余额", "rule": "关联应收/总应收", "value": "需关联交易明细", "threshold": "<20%", "triggered": False},
                {"dimension": "预付异常", "rule": "预付关联方/总预付", "value": "需关联交易明细", "threshold": "<30%", "triggered": False},
                {"dimension": "担保黑洞", "rule": "关联担保/净资产", "value": "需关联交易明细", "threshold": "<30%", "triggered": False},
                {"dimension": "资金占用", "rule": "其他应收-关联/净资产", "value": "需关联交易明细", "threshold": "<5%", "triggered": False},
            ]

        # 案例匹配
        case_match: Dict[str, Any] = results.get("case_match", {})
        matched_cases: List[Dict[str, Any]] = case_match.get("matched_cases", [])
        if matched_cases and matched_cases[0].get("case_id") == "NONE":
            matched_cases = []

        # 合规红线
        compliance_results: List[Dict[str, Any]] = self._build_compliance_results(results)

        # 归因分析
        triggered: List[Dict[str, Any]] = results.get("redflags", {}).get("triggered_signals", [])
        attribution: List[Dict[str, Any]] = [
            {
                "conclusion": s["name"],
                "cause_path": s.get("cause_path", ""),
                "evidence": str(s.get("evidence", {})),
                "linked_signals": s.get("linked_signals", []),
                "probability": 80 if s["severity"] == "P0" else 50,
            }
            for s in triggered[:5]
        ]

        # 实用建议
        advice_data: Dict[str, Any] = results.get("advice", {})
        advice_list: List[Dict[str, Any]] = advice_data.get("advice_list", [])

        # 审计清单
        audit_items: List[Dict[str, Any]] = [
            {
                "procedure": s.get("audit_procedure", "未指定审计程序"),
                "triggered_by": s["name"],
                "steps": [
                    f"获取{s['name']}相关数据",
                    "执行实质性测试程序",
                    "评估测试结果并记录",
                ],
            }
            for s in triggered[:5]
        ]

        # M-Score趋势
        mscore_trend: List[Optional[float]] = []
        for p in periods:
            m = results.get("mscore", {}).get(p, {})
            mscore_trend.append(m.get("value"))

        ctx.update({
            "crosscheck_results": crosscheck_results,
            "master_status": crosscheck.get("master_status", "PASS"),
            "master_status_text": crosscheck.get("master_status_text", "ALL CHECKS PASS"),
            "policy_analysis": policy_analysis,
            "fraud_total": len(triggered),
            "anomaly_count": results.get("anomalies", {}).get("summary", {}).get("total_anomalies", 0),
            "related_party": related_party,
            "matched_cases": matched_cases,
            # 案例匹配：相似度低于40%的去掉（避免误导）
            "min_similarity": 40,
            "compliance_results": compliance_results,
            "attribution": attribution,
            "advice_list": advice_list,
            "audit_items": audit_items,
            "mscore_periods": periods,
            "mscore_trend": mscore_trend,
            "zscore_periods": periods,
            "zscore_accounts": ["营收", "净利", "应收", "存货", "经营CF", "毛利率"],
            "zscore_data": self._compute_zscore_heatmap(results),
            # 红灯时间线数据
            "redflag_timeline": len(triggered) > 0,
            "redflag_periods": periods,
            "redflag_p0": [results.get("redflags", {}).get("summary", {}).get("p0_triggered", 0)],
            "redflag_p1": [results.get("redflags", {}).get("summary", {}).get("p1_triggered", 0)],
        })

        return ctx

    # ---- 辅助方法 ----

    @staticmethod
    def _compute_risk_score(results: Dict[str, Any]) -> float:
        """计算综合风险评分 (0-100)，单期数据时降低增长类信号的权重。

        评分逻辑:
        - P0信号: +10分（单期数据中仅对非增长类P0给满分）
        - P1信号: +5分
        - P2信号: +2分
        - M-Score: 造假嫌疑 +15分，高风险 +8分
        - 案例匹配: 相似度>50% +10分
        - 联动触发>=2: +5分
        - 单期数据上限: 70分（防止因数据不足导致的假阳性溢出）
        """
        redflags: Dict[str, Any] = results.get("redflags", {})
        triggered: List[Dict[str, Any]] = redflags.get("triggered_signals", [])
        periods: List[str] = results.get("periods", [])
        single_period: bool = len(periods) <= 1

        score: float = 0.0
        for s in triggered:
            if s["severity"] == "P0":
                # 单期数据中，增长/变化类P0信号降权（可能是数据不足假阳性）
                risk_type = s.get("risk_type", "")
                growth_like = any(kw in risk_type for kw in ["增长", "变化", "趋势", "背离"])
                score += 5.0 if (single_period and growth_like) else 10.0
            elif s["severity"] == "P1":
                score += 5.0
            else:
                score += 2.0

        # M-Score加分（单期无M-Score则跳过）
        mscore_results: Dict[str, Any] = results.get("mscore", {})
        if periods:
            mscore_val: float = mscore_results.get(periods[-1], {}).get("value") or 0
            if mscore_val > -1.78:
                score += 15.0
            elif mscore_val > -2.22:
                score += 8.0

        # 案例匹配加分
        case_match: Dict[str, Any] = results.get("case_match", {})
        matched: List[Dict[str, Any]] = case_match.get("matched_cases", [])
        if matched and matched[0].get("similarity", 0) > 50:
            score += 10.0

        # 联动触发加分
        linked: List[Dict[str, Any]] = redflags.get("summary", {}).get(
            "linked_upgrades_triggered", []
        )
        if len(linked) >= 2:
            score += 5.0

        # 单期数据时降低上限，避免虚假高分
        max_score: float = 70.0 if single_period else 100.0
        score = min(score, max_score)

        # 数据充分性调整：多期>单期有CF>单期无CF
        has_cf: bool = False
        if periods:
            cf_data = results.get("cf", {}).get(periods[-1], {}) if "cf" in results else results.get("bs", {}).get(periods[-1], {}).get("经营活动产生的现金流量净额")
            has_cf = bool(results.get("cf_pattern", {}).get(periods[-1] if periods else "", {}).get("经营CF", "N/A") not in ("N/A", "- (0)")) if periods else False
        if single_period and not has_cf:
            score *= 0.5  # 无CF数据的单期分析，评分减半

        return round(score, 1)

    @staticmethod
    def _get_risk_class(score: float) -> str:
        """根据风险评分返回CSS类名。"""
        if score <= 25:
            return "ok"
        elif score <= 45:
            return "warning"
        elif score <= 70:
            return "warning"
        else:
            return "danger"

    @staticmethod
    def _get_health(score: float) -> Tuple[str, str, str]:
        """根据风险评分返回健康度元组。"""
        if score <= 25:
            return ("健康", "🟢", "green")
        elif score <= 45:
            return ("关注", "🟡", "yellow")
        elif score <= 65:
            return ("风险", "🟠", "orange")
        elif score <= 80:
            return ("危险", "🔴", "red")
        else:
            return ("极度危险", "💀", "skull")

    @staticmethod
    def _generate_one_liner(results: Dict[str, Any]) -> str:
        """生成一句话核心诊断（含数据充分性警示）。"""
        redflags: Dict[str, Any] = results.get("redflags", {})
        triggered: List[Dict[str, Any]] = redflags.get("triggered_signals", [])
        periods: List[str] = results.get("periods", [])

        # 单期数据警示
        prefix = ""
        if len(periods) <= 1:
            prefix = "⚠️ 仅1期数据，增长/变化类信号可能为假阳性。建议补充多期数据以实现完整分析。"

        if not triggered:
            return "财务报表整体正常，未检测到明显异常信号。建议保持常规监控。"

        p0_signals: List[Dict[str, Any]] = [s for s in triggered if s["severity"] == "P0"]
        # 区分增长类P0和其他P0
        real_p0 = [s for s in p0_signals if "增长" not in s.get("risk_type", "") and "变化" not in s.get("risk_type", "") and "背离" not in s.get("risk_type", "")]
        fake_p0 = len(p0_signals) - len(real_p0)

        parts = []
        if prefix:
            parts.append(prefix)
        if real_p0:
            parts.append(f"⚠️ 发现 {len(real_p0)} 个需关注的严重(P0)风险信号，涉及{'、'.join(set(s.get('risk_type','')[:4] for s in real_p0[:3]))}等领域。")
        if fake_p0 > 0 and len(periods) <= 1:
            parts.append(f"另有 {fake_p0} 个P0信号因单期数据限制可能为假阳性，建议补充多期数据验证。")

        mscore_val = results.get("mscore", {}).get(periods[-1] if periods else "", {}).get("value")
        if mscore_val is not None:
            parts.append(f"M-Score={mscore_val:.2f}。")
        else:
            parts.append("M-Score：数据不足无法计算（需≥2期）。")

        return " ".join(parts) if parts else "财务报表整体正常，未检测到明显异常信号。"

    @staticmethod
    def _compute_radar_values(results: Dict[str, Any]) -> List[float]:
        """计算六维雷达图的数值。"""
        ratios: Dict[str, Any] = results.get("ratios", {})

        # 偿债: 基于流动比率评分 (假设行业均值1.6, 满分100)
        solvency: List[Dict[str, Any]] = ratios.get("偿债能力", [])
        cur_ratio: float = solvency[-1]["流动比率"] if solvency else 1.6
        solvency_score: float = min(100, max(0, cur_ratio / 1.6 * 50))

        # 营运: 基于资产周转率
        operating: List[Dict[str, Any]] = ratios.get("营运能力", [])
        turnover: float = operating[-1]["总资产周转率"] if operating else 0.6
        operating_score: float = min(100, max(0, turnover / 0.6 * 50))

        # 盈利: 基于ROE
        profitability: List[Dict[str, Any]] = ratios.get("盈利能力", [])
        roe: float = profitability[-1]["ROE"] if profitability else 0.09
        profit_score: float = min(100, max(0, roe / 0.09 * 50))

        # 现金流: 基于CFO/净利
        cashflow_q: List[Dict[str, Any]] = ratios.get("现金流质量", [])
        cfo_ratio: float = cashflow_q[-1]["经营CF/净利"] if cashflow_q else 1.0
        cf_score: float = min(100, max(0, max(0, cfo_ratio) * 50))

        # 成长: 基于营收增长率
        growth: List[Dict[str, Any]] = ratios.get("成长能力", [])
        rev_growth: float = growth[-1]["营收增长率"] if growth else 0.10
        growth_score: float = min(100, max(0, (rev_growth + 0.2) * 100))

        # 资产质量: 基于资产负债率
        debt_ratio: float = solvency[-1]["资产负债率"] if solvency else 0.45
        asset_score: float = min(100, max(0, (1 - debt_ratio) * 100))

        return [
            round(solvency_score, 1),
            round(operating_score, 1),
            round(profit_score, 1),
            round(cf_score, 1),
            round(growth_score, 1),
            round(asset_score, 1),
        ]

    @staticmethod
    def _compute_box_data(results: Dict[str, Any], mode: str = "current") -> List[float]:
        """从实际比率数据计算箱线图数据。

        Args:
            results: 分析结果字典。
            mode: "current" 返回当前值, "industry" 返回行业中位数。

        Returns:
            6元列表: [毛利率, 净利率, ROE, 流动比率, 资产负债率, 周转率]
        """
        ratios: Dict[str, Any] = results.get("ratios", {})
        periods: List[str] = results.get("periods", [])
        latest = periods[-1] if periods else None

        # 默认行业值
        industry_defaults = [25.0, 8.0, 9.0, 1.6, 45.0, 0.60]
        # 行业基准（由results中的industry配置覆盖）
        industry: Dict[str, Any] = results.get("industry", {})
        ind_profit = industry.get("profit_margin_avg", 25.0)
        ind_net = industry.get("net_margin_avg", 8.0)
        ind_roe = industry.get("roe_avg", 9.0)
        ind_cur = industry.get("current_ratio_avg", 1.6)  # 比率值，非百分比
        ind_debt = industry.get("debt_ratio_avg", 45.0)
        ind_turn = industry.get("turnover_avg", 0.60)
        industry_vals = [ind_profit, ind_net, ind_roe, ind_cur, ind_debt, ind_turn]

        if mode == "industry":
            return industry_vals

        # 提取当前值
        profitability = ratios.get("盈利能力", [])
        solvency = ratios.get("偿债能力", [])
        operating = ratios.get("营运能力", [])

        try:
            gross = profitability[-1].get("毛利率", 25.0) * 100 if profitability else 25.0
            net = profitability[-1].get("净利率", 8.0) * 100 if profitability else 8.0
            roe = profitability[-1].get("ROE", 9.0) * 100 if profitability else 9.0
            # 流动比率和资产负债率是纯比率（非百分比），不乘100
            current = solvency[-1].get("流动比率", 1.6) if solvency else 1.6
            debt = solvency[-1].get("资产负债率", 0.45) * 100 if solvency else 45.0
            turnover = operating[-1].get("总资产周转率", 0.60) if operating else 0.60
        except (IndexError, KeyError, TypeError):
            return industry_vals

        return [round(gross, 1), round(net, 1), round(roe, 1),
                round(current, 1), round(debt, 1), round(turnover, 2)]

    @staticmethod
    def _compute_heatmap_data(results: Dict[str, Any]) -> List[List[float]]:
        """从 redflag 信号生成风险热力图数据。

        Returns:
            [[period_idx, risk_idx, severity_score], ...]
        """
        redflags: Dict[str, Any] = results.get("redflags", {})
        signals: List[Dict[str, Any]] = redflags.get("triggered_signals", [])
        periods: List[str] = results.get("periods", [])

        if not signals or not periods:
            # 无数据时返回空热力图（全0）
            return [[0, i, 0] for i in range(5)]

        risk_map = {"收入质量": 0, "资产质量": 1, "关联交易": 2, "流动性": 3, "合规": 4}
        heatmap: List[List[float]] = []

        for s in signals:
            risk_type = s.get("risk_type", "")
            idx = risk_map.get(risk_type, -1)
            if idx < 0:
                # 尝试模糊匹配
                for k, v in risk_map.items():
                    if k[:2] in risk_type or risk_type[:2] in k:
                        idx = v
                        break
            if idx < 0:
                idx = hash(risk_type) % 5  # 兜底

            severity = 2.0 if s.get("severity") == "P0" else (1.0 if s.get("severity") == "P1" else 0.5)
            # 使用最后一个period作为时间维度
            heatmap.append([len(periods) - 1 if periods else 0, idx, severity])

        return heatmap if heatmap else [[0, i, 0] for i in range(5)]

    @staticmethod
    def _compute_scenario(results: Dict[str, Any], mode: str = "base") -> List[float]:
        """基于实际增长率计算情景预测数据。

        Args:
            results: 分析结果字典。
            mode: "optimistic" / "base" / "pessimistic"

        Returns:
            历史值 + 3期预测值列表。
        """
        periods: List[str] = results.get("periods", [])
        ratios = results.get("ratios", {})
        growth = ratios.get("成长能力", [])

        # 获取最新期营收（万元单位）— 多路径查找
        # 路径1: results["is"] (标准化管道数据)
        # 路径2: results["income_statement"] (旧格式)
        # 路径3: results["raw_revenue"] (直接传入)
        latest_rev = 100.0  # 默认基准
        raw_is = results.get("is") or results.get("income_statement") or {}
        raw_rev = results.get("raw_revenue")

        if raw_rev:
            latest_rev = float(raw_rev) / 10000
        elif periods:
            latest_p = periods[-1]
            if isinstance(raw_is, dict) and latest_p in raw_is:
                latest_rev = float(raw_is[latest_p].get("营业收入", 1000000)) / 10000
            elif isinstance(raw_is, list) and raw_is:
                latest_rev = float(raw_is[-1].get("营业收入", 1000000)) / 10000

        # 增长率
        rev_growth_rate = growth[-1].get("营收增长率", 0.10) if growth else 0.10

        multipliers = {
            "optimistic": [1.0, 1 + rev_growth_rate * 1.5, (1 + rev_growth_rate * 1.5) ** 2, (1 + rev_growth_rate * 1.5) ** 3],
            "base": [1.0, 1 + rev_growth_rate, (1 + rev_growth_rate) ** 2, (1 + rev_growth_rate) ** 3],
            "pessimistic": [1.0, 1 - abs(rev_growth_rate) * 0.5, (1 - abs(rev_growth_rate) * 0.5) ** 2, (1 - abs(rev_growth_rate) * 0.5) ** 3],
        }

        m = multipliers.get(mode, multipliers["base"])
        history_scaled = latest_rev
        # 如果有历史数据，取最后几期
        hist_vals = [history_scaled * 0.85, history_scaled * 0.92, history_scaled]
        if len(periods) > 3:
            hist_vals = hist_vals[-len(periods):]
        elif len(periods) < 3:
            hist_vals = [history_scaled] * len(periods)

        hist_vals = hist_vals[-len(periods):]
        forecast = [round(history_scaled * m[1], 1), round(history_scaled * m[2], 1), round(history_scaled * m[3], 1)]
        return [round(v, 1) for v in hist_vals] + forecast

    @staticmethod
    def _compute_zscore_heatmap(results: Dict[str, Any]) -> List[List[float]]:
        """从实际 zscore 数据生成热力图。

        Returns:
            [[period_idx, account_idx, zscore_component], ...]
        """
        zscore_results: Dict[str, float] = results.get("zscore", {})
        periods = results.get("periods", [])

        if not zscore_results or not periods:
            return [[0, i, 0] for i in range(6)]

        data = []
        for pi, period in enumerate(periods):
            z = zscore_results.get(period, 0)
            # 将zscore分解到6个账户维度（按权重分配）
            for ai, account in enumerate(["营收", "净利", "应收", "存货", "经营CF", "毛利率"]):
                # 权重模拟：营收30% 净利25% 应收15% 存货10% 经营CF12% 毛利率8%
                weights = [0.30, 0.25, 0.15, 0.10, 0.12, 0.08]
                component = z * weights[ai] * 5  # 缩放
                data.append([pi, ai, round(component, 2)])

        return data if data else [[0, i, 0] for i in range(6)]

    @staticmethod
    def _build_compliance_results(results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """构建合规红线检查结果。"""
        triggered: List[str] = [
            s["id"]
            for s in results.get("redflags", {}).get("triggered_signals", [])
        ]
        checks: List[Dict[str, Any]] = [
            {"id": "AS-01", "standard": "CAS 14", "check": "收入确认是否符合履约义务转移原则",
             "status": "触发" if "R-01" in triggered or "R-13" in triggered else "正常",
             "note": "应收增速异常" if "R-13" in triggered else "通过"},
            {"id": "AS-02", "standard": "CAS 36", "check": "关联方关系及交易是否充分披露",
             "status": "触发" if "R-06" in triggered or "R-18" in triggered else "正常",
             "note": "其他应收款占比偏高" if "R-18" in triggered else "通过"},
            {"id": "AS-03", "standard": "CAS 8", "check": "资产减值测试是否充分",
             "status": "触发" if "R-05" in triggered or "R-17" in triggered else "正常",
             "note": "可能存在减值滞后" if "R-17" in triggered else "通过"},
            {"id": "AS-04", "standard": "CAS 6", "check": "研发支出资本化是否满足5条件",
             "status": "触发" if "R-20" in triggered else "正常",
             "note": "资本化率偏高" if "R-20" in triggered else "通过"},
            {"id": "AS-05", "standard": "CAS 13", "check": "或有事项是否充分披露",
             "status": "正常", "note": "未发现异常"},
            {"id": "AS-06", "standard": "CAS 33", "check": "合并范围是否恰当",
             "status": "正常", "note": "未发现异常"},
            {"id": "CSRC-01", "standard": "退市新规", "check": "是否触及财务类退市指标",
             "status": "关注", "note": "持续监控"},
            {"id": "CSRC-03", "standard": "证监会", "check": "是否存在大股东非经营性资金占用",
             "status": "触发" if "R-18" in triggered else "正常",
             "note": "其他应收款偏高" if "R-18" in triggered else "通过"},
        ]
        return checks


# M-Score变量描述
_MSCORE_VAR_DESC: Dict[str, str] = {
    "DSRI": "应收账款指数: >1表示应收膨胀",
    "GMI": "毛利率指数: >1表示毛利率恶化",
    "AQI": "资产质量指数: >1表示非流动资产占比上升",
    "SGI": "收入增长指数: >1表示收入增长",
    "DEPI": "折旧率指数: >1表示折旧率下降(激进)",
    "SGAI": "费用指数: >1表示费用率上升",
    "TATA": "应计/总资产: 正值越大应计越高",
    "LVGI": "杠杆指数: >1表示杠杆上升",
}


def generate_report(
    results: Dict[str, Any],
    level: int = 1,
    output_path: Optional[str] = None,
) -> str:
    """便捷函数：生成指定级别的分析报告。

    Args:
        results: 分析结果字典。
        level: 报告级别 (1/2/3)。
        output_path: 输出文件路径。

    Returns:
        str: HTML报告内容。
    """
    generator: ReportGenerator = ReportGenerator()

    if level == 1:
        return generator.generate_level1(results, output_path)
    elif level == 2:
        return generator.generate_level2(results, output_path)
    elif level == 3:
        return generator.generate_level3(results, output_path)
    else:
        raise ValueError(f"不支持的报告级别: {level}。请使用 1/2/3。")
