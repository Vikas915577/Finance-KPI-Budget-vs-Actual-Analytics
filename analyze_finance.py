#!/usr/bin/env python3
"""Reproducible finance KPI analysis for synthetic portfolio data."""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

KEY = ["month_start", "region_id", "department_id", "account_id"]

def load_data(data_dir: Path):
    fact = pd.read_csv(data_dir / "fact_finance_monthly.csv", parse_dates=["month_start"])
    account = pd.read_csv(data_dir / "dim_account.csv")
    region = pd.read_csv(data_dir / "dim_region.csv")
    dept = pd.read_csv(data_dir / "dim_department.csv")
    return fact, account, region, dept

def validate(fact, account, region, dept):
    if fact.duplicated(KEY).any():
        raise ValueError("Duplicate fact grain: month × region × department × account")
    if fact[KEY].isna().any().any():
        raise ValueError("Missing key values in fact table")
    if fact[["budget_amount", "actual_amount"]].isna().any().any():
        raise ValueError("Missing financial amounts")
    if (fact[["budget_amount", "actual_amount"]] < 0).any().any():
        raise ValueError("Negative line-item amounts are outside this demo's model assumptions")
    for col, dim, key in [
        ("account_id", account, "account_id"),
        ("region_id", region, "region_id"),
        ("department_id", dept, "department_id"),
    ]:
        if not set(fact[col]).issubset(set(dim[key])):
            raise ValueError(f"Unmatched {col} foreign key")
    if fact["month_start"].nunique() != 12:
        raise ValueError("Expected 12 monthly periods for this portfolio dataset")
    return True

def enrich(fact, account, region, dept):
    df = (fact.merge(account, on="account_id", validate="many_to_one")
              .merge(region, on="region_id", validate="many_to_one")
              .merge(dept, on="department_id", validate="many_to_one"))
    df["variance_amount"] = df["actual_amount"] - df["budget_amount"]
    df["variance_pct"] = np.where(df["budget_amount"] != 0,
                                  df["variance_amount"] / df["budget_amount"] * 100, np.nan)
    return df

def pnl_by_period(df, dimensions):
    keys = dimensions
    def sums(kind, prefix):
        sub = df[df.account_type == kind].groupby(keys, as_index=False).agg(
            **{f"{prefix}_actual": ("actual_amount", "sum"),
               f"{prefix}_budget": ("budget_amount", "sum")})
        return sub
    rev=sums("Revenue","revenue")
    cogs=sums("COGS","cogs")
    opex=sums("Operating Expense","opex")
    out=rev.merge(cogs,on=keys,validate="one_to_one").merge(opex,on=keys,validate="one_to_one")
    out["operating_profit_actual"]=out.revenue_actual-out.cogs_actual-out.opex_actual
    out["operating_profit_budget"]=out.revenue_budget-out.cogs_budget-out.opex_budget
    out["revenue_variance"]=out.revenue_actual-out.revenue_budget
    out["opex_variance"]=out.opex_actual-out.opex_budget
    out["operating_profit_variance"]=out.operating_profit_actual-out.operating_profit_budget
    out["operating_margin_actual_pct"]=np.where(out.revenue_actual!=0,out.operating_profit_actual/out.revenue_actual*100,np.nan)
    out["operating_margin_budget_pct"]=np.where(out.revenue_budget!=0,out.operating_profit_budget/out.revenue_budget*100,np.nan)
    return out

def run(data_dir: Path, output_dir: Path):
    output_dir.mkdir(parents=True,exist_ok=True)
    charts=output_dir/"charts"; charts.mkdir(parents=True,exist_ok=True)
    fact,account,region,dept=load_data(data_dir)
    validate(fact,account,region,dept)
    df=enrich(fact,account,region,dept)
    monthly=pnl_by_period(df,["month_start"])
    monthly.to_csv(output_dir/"monthly_pnl_summary.csv",index=False,date_format="%Y-%m-%d")
    department=pnl_by_period(df,["department_id","department_name"])
    department.to_csv(output_dir/"department_profit_variance.csv",index=False)
    region_pnl=pnl_by_period(df,["region_id","region_name"])
    region_pnl["revenue_variance_pct"]=np.where(region_pnl.revenue_budget!=0,region_pnl.revenue_variance/region_pnl.revenue_budget*100,np.nan)
    region_pnl.to_csv(output_dir/"region_performance.csv",index=False)
    account_summary=df.groupby(["account_id","account_name","account_type"],as_index=False).agg(
        actual_amount=("actual_amount","sum"),budget_amount=("budget_amount","sum"),variance_amount=("variance_amount","sum"))
    account_summary["variance_pct"]=np.where(account_summary.budget_amount!=0,account_summary.variance_amount/account_summary.budget_amount*100,np.nan)
    account_summary["interpretation"]=np.where(account_summary.account_type=="Revenue",
        np.where(account_summary.variance_amount>=0,"Favourable revenue variance","Unfavourable revenue variance"),
        np.where(account_summary.variance_amount>=0,"Unfavourable cost variance","Favourable cost variance"))
    account_summary.to_csv(output_dir/"account_variance_summary.csv",index=False)
    total={}
    for kind, label in [("Revenue","revenue"),("COGS","cogs"),("Operating Expense","opex")]:
        sub=df[df.account_type==kind]
        total[f"{label}_actual"]=float(sub.actual_amount.sum())
        total[f"{label}_budget"]=float(sub.budget_amount.sum())
    total["operating_profit_actual"]=total["revenue_actual"]-total["cogs_actual"]-total["opex_actual"]
    total["operating_profit_budget"]=total["revenue_budget"]-total["cogs_budget"]-total["opex_budget"]
    total["revenue_variance"]=total["revenue_actual"]-total["revenue_budget"]
    total["operating_profit_variance"]=total["operating_profit_actual"]-total["operating_profit_budget"]
    total["operating_margin_actual_pct"]=total["operating_profit_actual"]/total["revenue_actual"]*100
    total["operating_margin_budget_pct"]=total["operating_profit_budget"]/total["revenue_budget"]*100
    pd.DataFrame([{"metric":k,"value":round(v,2)} for k,v in total.items()]).to_csv(output_dir/"executive_kpis.csv",index=False)
    # Charts: each chart compares performance to a plan or explains a variance.
    m=monthly.copy(); m["period"]=pd.to_datetime(m.month_start).dt.strftime("%b")
    plt.figure(figsize=(10,4.8))
    plt.plot(m.period,m.revenue_actual,marker="o",label="Actual revenue")
    plt.plot(m.period,m.revenue_budget,marker="o",label="Budget revenue")
    plt.title("Display | Monthly revenue vs budget"); plt.xlabel("Month"); plt.ylabel("Amount (USD)")
    plt.legend(); plt.tight_layout(); plt.savefig(charts/"01_monthly_revenue_actual_vs_budget.png",dpi=150); plt.close()
    d=department.sort_values("operating_profit_variance")
    plt.figure(figsize=(9,4.8)); plt.bar(d.department_name,d.operating_profit_variance)
    plt.axhline(0,linewidth=1); plt.title("Diagnose | Operating-profit variance by department")
    plt.xlabel("Department"); plt.ylabel("Actual operating profit − budget (USD)")
    plt.xticks(rotation=18,ha="right"); plt.tight_layout(); plt.savefig(charts/"02_operating_profit_variance_by_department.png",dpi=150); plt.close()
    e=account_summary[account_summary.account_type=="Operating Expense"].sort_values("variance_amount")
    plt.figure(figsize=(9,4.8)); plt.bar(e.account_name,e.variance_amount)
    plt.axhline(0,linewidth=1); plt.title("Diagnose | Expense variance by account")
    plt.xlabel("Expense account"); plt.ylabel("Actual − budget (USD)")
    plt.xticks(rotation=18,ha="right"); plt.tight_layout(); plt.savefig(charts/"03_expense_variance_by_account.png",dpi=150); plt.close()
    plt.figure(figsize=(8,4.8)); plt.scatter(monthly.revenue_actual,monthly.operating_margin_actual_pct)
    plt.title("Diagnose | Revenue vs operating margin by month"); plt.xlabel("Actual revenue (USD)"); plt.ylabel("Operating margin (%)")
    plt.tight_layout(); plt.savefig(charts/"04_revenue_vs_operating_margin.png",dpi=150); plt.close()
    best=department.sort_values("operating_profit_variance",ascending=False).iloc[0]
    worst=department.sort_values("operating_profit_variance").iloc[0]
    top_exp=e.sort_values("variance_amount",ascending=False).iloc[0]
    rev_var=total["revenue_variance"]
    findings=[
      "SYNTHETIC PORTFOLIO DATA — not actual company results.",
      f"DISPLAY: Revenue was ${total['revenue_actual']:,.0f} against budget ${total['revenue_budget']:,.0f}; variance ${rev_var:,.0f} ({rev_var/total['revenue_budget']*100:.2f}% of budget).",
      f"DISPLAY: Operating profit was ${total['operating_profit_actual']:,.0f} against budget ${total['operating_profit_budget']:,.0f}; variance ${total['operating_profit_variance']:,.0f}.",
      f"DIAGNOSE: {best.department_name} had the strongest operating-profit variance (${best.operating_profit_variance:,.0f}); {worst.department_name} had the weakest (${worst.operating_profit_variance:,.0f}).",
      f"DIAGNOSE: {top_exp.account_name} had the largest positive expense variance (${top_exp.variance_amount:,.0f}); validate volume, price, timing, and coding before assigning cause.",
      "DECIDE: Assign the variance owner to validate the largest driver, agree a corrective action and due date, then monitor next month's actual-vs-budget result. This is a proposed workflow, not proof of causation."
    ]
    (output_dir/"findings.txt").write_text("\\n".join(findings)+"\\n",encoding="utf-8")
    return {"rows":len(fact),"months":fact.month_start.nunique(),"departments":fact.department_id.nunique(),
            "regions":fact.region_id.nunique(),"revenue_actual":total["revenue_actual"],
            "revenue_budget":total["revenue_budget"],"op_profit_variance":total["operating_profit_variance"]}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--data-dir",default="data/synthetic")
    parser.add_argument("--output-dir",default="outputs")
    args=parser.parse_args()
    summary=run(Path(args.data_dir),Path(args.output_dir))
    print("Analysis complete:",summary)
