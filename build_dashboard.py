#!/usr/bin/env python3
"""Build a self-contained GitHub Pages dashboard from generated finance outputs.

Run after `python python/analyze_finance.py`. The resulting index.html embeds
its KPI values and chart SVGs, so GitHub Pages does not need runtime data fetches.
"""
from __future__ import annotations

from html import escape
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "index.html"
OUTPUTS = ROOT / "outputs"


def money_m(value: float) -> str:
    return f"${value / 1_000_000:.2f}M"


def money_k_signed(value: float, digits: int = 1) -> str:
    sign = "+" if value >= 0 else "−"
    return f"{sign}${abs(value) / 1_000:.{digits}f}K"


def signed_pct(value: float, digits: int = 2) -> str:
    sign = "+" if value >= 0 else "−"
    return f"{sign}{abs(value):.{digits}f}%"


def line_path(points: list[tuple[float, float]]) -> str:
    return " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}" for i, (x, y) in enumerate(points))


def revenue_svg(monthly: pd.DataFrame) -> str:
    width, height = 620, 280
    left, right, top, bottom = 58, 12, 28, 43
    plot_w, plot_h = width - left - right, height - top - bottom
    min_y, max_y = 3_000_000.0, 3_500_000.0
    xs = [left + (i * plot_w / (len(monthly) - 1)) for i in range(len(monthly))]
    y = lambda value: top + (max_y - value) / (max_y - min_y) * plot_h
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Monthly actual revenue and budget revenue from the synthetic finance data">',
             f'<rect x="42" y="14" width="{width-52}" height="{height-53}" rx="8" fill="#f7f9fd"/>']
    for tick in range(3_000_000, 3_500_001, 100_000):
        yy = y(tick)
        parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{width-right}" y2="{yy:.1f}" stroke="#dfe6f0"/>')
        parts.append(f'<text x="{left-8}" y="{yy+4:.1f}" fill="#718096" font-size="18" text-anchor="end">${tick/1_000_000:.1f}M</text>')
    actual = [(xs[i], y(float(row.revenue_actual))) for i, row in enumerate(monthly.itertuples())]
    budget = [(xs[i], y(float(row.revenue_budget))) for i, row in enumerate(monthly.itertuples())]
    parts.append(f'<path d="{line_path(budget)}" fill="none" stroke="#8798b7" stroke-width="3" stroke-dasharray="7 5" stroke-linejoin="round"/>')
    parts.append(f'<path d="{line_path(actual)}" fill="none" stroke="#285ee8" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>')
    for i, row in enumerate(monthly.itertuples()):
        xx = xs[i]
        month = pd.Timestamp(row.month_start).strftime("%b")
        parts.append(f'<circle cx="{xx:.1f}" cy="{y(float(row.revenue_actual)):.1f}" r="3.5" fill="#285ee8"><title>{month} actual revenue: ${row.revenue_actual:,.0f}</title></circle>')
        parts.append(f'<circle cx="{xx:.1f}" cy="{y(float(row.revenue_budget)):.1f}" r="3" fill="#8798b7"><title>{month} budget revenue: ${row.revenue_budget:,.0f}</title></circle>')
        parts.append(f'<text x="{xx:.1f}" y="{height-16}" fill="#718096" font-size="17" text-anchor="middle">{month}</text>')
    parts.append('</svg>')
    return ''.join(parts)


def department_svg(departments: pd.DataFrame) -> str:
    d = departments.sort_values("operating_profit_variance").reset_index(drop=True)
    width, height = 620, 280
    base, value_col = 390, 610
    max_abs = max(abs(float(v)) for v in d.operating_profit_variance) or 1
    max_len = 190
    row_h, top = 46, 20
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Operating profit variance by department, actual minus budget">',
             f'<line x1="{base}" y1="12" x2="{base}" y2="{height-18}" stroke="#cbd5e1"/>']
    for i, row in enumerate(d.itertuples()):
        yy = top + i * row_h + 13
        value = float(row.operating_profit_variance)
        length = abs(value) / max_abs * max_len
        x = base - length if value < 0 else base
        color = "#bd3b36" if value < 0 else "#087b62"
        parts.append(f'<text x="8" y="{yy+5}" fill="#526178" font-size="19">{escape(str(row.department_name))}</text>')
        parts.append(f'<rect x="{x:.1f}" y="{yy-10}" width="{max(length,1):.1f}" height="20" rx="4" fill="{color}"/>')
        label = ("−" if value < 0 else "+") + f"${abs(value)/1000:.0f}K"
        parts.append(f'<text x="{value_col}" y="{yy+5}" text-anchor="end" fill="#526178" font-size="18" font-weight="700">{label}<title>{escape(str(row.department_name))}: ${value:,.2f}</title></text>')
    parts.append('</svg>')
    return ''.join(parts)

def expense_svg(accounts: pd.DataFrame) -> str:
    d = accounts[accounts.account_type == "Operating Expense"].sort_values("variance_amount", ascending=False).reset_index(drop=True)
    width, height = 620, max(155, len(d) * 52 + 25)
    base, value_col = 185, 610
    max_abs = max(abs(float(v)) for v in d.variance_amount) or 1
    max_len = 330
    row_h, top = 52, 20
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Operating expense variance by account, actual minus budget">',
             f'<line x1="{base}" y1="12" x2="{base}" y2="{height-10}" stroke="#cbd5e1"/>']
    for i, row in enumerate(d.itertuples()):
        yy = top + i * row_h + 14
        value = float(row.variance_amount)
        length = abs(value) / max_abs * max_len
        x = base - length if value < 0 else base
        color = "#087b62" if value < 0 else "#bd3b36"
        parts.append(f'<text x="8" y="{yy+4}" fill="#526178" font-size="17">{escape(str(row.account_name))}</text>')
        parts.append(f'<rect x="{x:.1f}" y="{yy-11}" width="{max(length,1):.1f}" height="22" rx="4" fill="{color}"/>')
        label = ("−" if value < 0 else "+") + f"${abs(value)/1000:.1f}K"
        parts.append(f'<text x="{value_col}" y="{yy+4}" text-anchor="end" fill="#526178" font-size="17" font-weight="700">{label}<title>{escape(str(row.account_name))}: ${value:,.2f}</title></text>')
    parts.append('</svg>')
    return ''.join(parts)

def scatter_svg(monthly: pd.DataFrame) -> str:
    width, height = 620, 265
    left, right, top, bottom = 58, 12, 22, 45
    plot_w, plot_h = width-left-right, height-top-bottom
    min_x, max_x = 3_100_000.0, 3_500_000.0
    min_y, max_y = 24.0, 27.0
    px = lambda value: left + (value-min_x)/(max_x-min_x)*plot_w
    py = lambda value: top + (max_y-value)/(max_y-min_y)*plot_h
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Monthly actual revenue versus actual operating margin using observed monthly values">',
             f'<rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" rx="8" fill="#f7f9fd"/>']
    for tick in [24,25,26,27]:
        yy = py(tick)
        parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{width-right}" y2="{yy:.1f}" stroke="#dfe6f0"/>')
        parts.append(f'<text x="{left-10}" y="{yy+4:.1f}" fill="#718096" font-size="18" text-anchor="end">{tick}%</text>')
    for tick in [3_100_000,3_200_000,3_300_000,3_400_000,3_500_000]:
        xx = px(tick)
        parts.append(f'<line x1="{xx:.1f}" y1="{top}" x2="{xx:.1f}" y2="{height-bottom}" stroke="#e8edf5"/>')
        parts.append(f'<text x="{xx:.1f}" y="{height-20}" fill="#718096" font-size="17" text-anchor="middle">${tick/1_000_000:.1f}M</text>')
    parts.append(f'<text x="{left+plot_w/2:.1f}" y="{height-4}" fill="#64748b" font-size="18" text-anchor="middle">Actual monthly revenue</text>')
    for row in monthly.itertuples():
        xx, yy = px(float(row.revenue_actual)), py(float(row.operating_margin_actual_pct))
        month = pd.Timestamp(row.month_start).strftime("%b")
        title = f"{month}: revenue ${row.revenue_actual:,.0f}; operating margin {row.operating_margin_actual_pct:.2f}%"
        parts.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="5" fill="#285ee8" stroke="white" stroke-width="2"><title>{escape(title)}</title></circle>')
    parts.append('</svg>')
    return ''.join(parts)


def replace_id(html: str, element_id: str, value: str) -> str:
    pattern = rf'(<[^>]*\bid="{re.escape(element_id)}"[^>]*>).*?(</[^>]+>)'
    updated, count = re.subn(pattern, lambda m: m.group(1) + escape(value) + m.group(2), html, count=1, flags=re.S)
    if count != 1:
        raise ValueError(f"Expected exactly one HTML element with id={element_id}; found {count}")
    return updated


def replace_svg(html: str, label: str, svg: str) -> str:
    # Match SVG by its accessibility label, then replace only that inline element.
    pattern = r'<svg\b(?=[^>]*aria-label="' + re.escape(label) + r'")[^>]*>.*?</svg>'
    updated, count = re.subn(pattern, lambda _m: svg, html, count=1, flags=re.S)
    if count != 1:
        raise ValueError(f"Expected one SVG for chart: {label}; found {count}")
    return updated


def build() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    kpi_frame = pd.read_csv(OUTPUTS / "executive_kpis.csv").set_index("metric")
    k = kpi_frame["value"].to_dict()
    monthly = pd.read_csv(OUTPUTS / "monthly_pnl_summary.csv", parse_dates=["month_start"])
    depts = pd.read_csv(OUTPUTS / "department_profit_variance.csv")
    accounts = pd.read_csv(OUTPUTS / "account_variance_summary.csv")

    # Build targets are inserted into the HTML once, then kept stable for re-builds.
    known_ids = ["kpi-revenue-actual", "kpi-revenue-budget", "kpi-revenue-variance", "kpi-profit-actual", "kpi-profit-budget", "kpi-profit-variance", "kpi-margin-actual", "kpi-margin-budget", "kpi-margin-variance", "finding-revenue-title", "finding-revenue-text", "finding-profit-text", "finding-department-text", "finding-account-title", "finding-account-text"]
    if any(f'id="{target}"' not in html for target in known_ids):
        raise ValueError("Dashboard build markers are missing from index.html; do not run against an unexpected template")

    revenue_var = float(k["revenue_variance"])
    profit_var = float(k["operating_profit_variance"])
    profit_var_pct = profit_var / float(k["operating_profit_budget"]) * 100
    margin_gap = float(k["operating_margin_actual_pct"]) - float(k["operating_margin_budget_pct"])
    html = replace_id(html, "kpi-revenue-actual", money_m(float(k["revenue_actual"])))
    html = replace_id(html, "kpi-revenue-budget", money_m(float(k["revenue_budget"])))
    html = replace_id(html, "kpi-revenue-variance", f"{money_k_signed(revenue_var)} · {signed_pct(revenue_var / float(k['revenue_budget']) * 100)} vs budget")
    html = replace_id(html, "kpi-profit-actual", money_m(float(k["operating_profit_actual"])))
    html = replace_id(html, "kpi-profit-budget", money_m(float(k["operating_profit_budget"])) )
    html = replace_id(html, "kpi-profit-variance", f"{money_k_signed(profit_var)} · {signed_pct(profit_var_pct)} vs budget")
    html = replace_id(html, "kpi-margin-actual", f"{float(k['operating_margin_actual_pct']):.2f}%")
    html = replace_id(html, "kpi-margin-budget", f"{float(k['operating_margin_budget_pct']):.2f}%")
    html = replace_id(html, "kpi-margin-variance", f"{margin_gap:+.2f} percentage points".replace("-", "−"))

    best = depts.loc[depts.operating_profit_variance.idxmax()]
    worst = depts.loc[depts.operating_profit_variance.idxmin()]
    worst_exp = accounts[accounts.account_type.eq("Operating Expense")].loc[accounts[accounts.account_type.eq("Operating Expense")].variance_amount.idxmax()]
    html = replace_id(html, "finding-revenue-title", "Revenue finished above budget" if revenue_var >= 0 else "Revenue finished below budget")
    html = replace_id(html, "finding-revenue-text", f"Actual revenue was {money_m(float(k['revenue_actual']))} against {money_m(float(k['revenue_budget']))} budget; the gap was {money_k_signed(revenue_var)} ({signed_pct(revenue_var/float(k['revenue_budget'])*100)}).")
    html = replace_id(html, "finding-profit-text", f"Operating profit was {money_m(float(k['operating_profit_actual']))} against {money_m(float(k['operating_profit_budget']))} budget: {money_k_signed(profit_var)} ({signed_pct(profit_var_pct)}). Revenue can beat plan while profit misses if costs rise faster.")
    html = replace_id(html, "finding-department-text", f"Largest favourable department variance: {best.department_name} ({money_k_signed(float(best.operating_profit_variance))}); largest adverse: {worst.department_name} ({money_k_signed(float(worst.operating_profit_variance))}). Investigate drivers; do not assume cause.")
    html = replace_id(html, "finding-account-title", f"Start with {worst_exp.account_name}")
    html = replace_id(html, "finding-account-text", f"Largest operating-expense variance was {money_k_signed(float(worst_exp.variance_amount))}. Validate volume, rates, timing and coding with the owner before recommending action.")

    html = replace_svg(html, "Monthly actual revenue and budget revenue from the synthetic finance data", revenue_svg(monthly))
    html = replace_svg(html, "Operating profit variance by department, actual minus budget", department_svg(depts))
    html = replace_svg(html, "Operating expense variance by account, actual minus budget", expense_svg(accounts))
    html = replace_svg(html, "Monthly actual revenue versus actual operating margin using observed monthly values", scatter_svg(monthly))
    HTML_PATH.write_text(html, encoding="utf-8")
    print(f"Dashboard built: {HTML_PATH} ({html.count('<svg')} embedded charts; KPI source = outputs/executive_kpis.csv)")


if __name__ == "__main__":
    build()
