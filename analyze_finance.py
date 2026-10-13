#!/usr/bin/env python3
"""Budget-vs-actual finance KPI analysis for synthetic portfolio data."""
from pathlib import Path
import argparse
import pandas as pd
import numpy as np
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
    if (fact[["budget_amount", "actual_amount"]] < 0).any().any():
        raise ValueError("Negative amounts are not expected in this simplified model")
    if not set(fact.account_id).issubset(set(account.account_id)):
        raise ValueError("Unknown account_id in fact data")
    if not set(fact.region_id).issubset(set(region.region_id)):
        raise ValueError("Unknown region_id in fact data")
    if not set(fact.department_id).issubset(set(dept.department_id)):
        raise ValueError("Unknown department_id in fact data")

def enrich(fact, account, region, dept):
    df = fact.merge(account, on="account_id", validate="many_to_one") \
             .merge(region, on="region_id", validate="many_to_one") \
             .merge(dept, on="department_id", validate="many_to_one")
    df["variance_amount"] = df["actual_amount"] - df["budget_amount"]
    df["variance_pct"] = np.where(df["budget_amount"] != 0,
                                   df["variance_amount"] / df["budget_amount"] * 100, np.nan)
    # Profit contribution is positive for revenue and negative for COGS/operating expenses.
    df["actual_profit_contribution"] = np.where(df.account_type == "Revenue", df.actual_amount, -df.actual_amount)
    df["budget_profit_contribution"] = np.where(df.account_type == "Revenue", df.budget_amount, -df.budget_amount)
    return df

def make_monthly(df):
    p = df.groupby("month_start", as_index=False).agg(
        actual_revenue=("actual_amount", lambda s: 0), budget_revenue=("budget_amount", lambda s: 0))
    # Explicitly build P&L totals by month to keep line semantics transparent.
    revenue = df[df.account_type == "Revenue"].groupby("month_start").agg(actual_revenue=("actual_amount","sum"), budget_revenue=("budget_amount","sum"))
    cogs = df[df.account_type == "COGS"].groupby("month_start").agg(actual_cogs=("actual_amount","sum"), budget_cogs=("budget_amount","sum"))
    opex = df[df.account_type == "Operating Expense"].groupby("month_start").agg(actual_opex=("actual_amount","sum"), budget_opex=("budget_amount","sum"))
    out = revenue.join(cogs).join(opex).reset_index()
    out["actual_gross_profit"] = out.actual_revenue - out.actual_cogs
    out["budget_gross_profit"] = out.budget_revenue - out.budget_cogs
    out["actual_operating_profit"] = out.actual_revenue - out.actual_cogs - out.actual_opex
    out["budget_operating_profit"] = out.budget_revenue - out.budget_cogs - out.budget_opex
    out["revenue_variance"] = out.actual_revenue - out.budget_revenue
    out["opex_variance"] = out.actual_opex - out.budget_opex
    out["operating_profit_variance"] = out.actual_operating_profit - out.budget_operating_profit
    out["actual_operating_margin_pct"] = np.where(out.actual_revenue != 0, out.actual_operating_profit/out.actual_revenue*100, np.nan)
    out["budget_operating_margin_pct"] = np.where(out.budget_revenue != 0, out.budget_operating_profit/out.budget_revenue*100, np.nan)
    return out

def make_org_variance(df):
    revenue = df[df.account_type == "Revenue"].groupby(["department_id","department_name"],as_index=False).agg(actual_revenue=("actual_amount","sum"),budget_revenue=("budget_amount","sum"))
    cogs = df[df.account_type == "COGS"].groupby(["department_id","department_name"],as_index=False).agg(actual_cogs=("actual_amount","sum"),budget_cogs=("budget_amount","sum"))
    opex = df[df.account_type == "Operating Expense"].groupby(["department_id","department_name"],as_index=False).agg(actual_opex=("actual_amount","sum"),budget_opex=("budget_amount","sum"))
    out = revenue.merge(cogs,on=["department_id","department_name"]).merge(opex,on=["department_id","department_name"])
    out["actual_operating_profit"] = out.actual_revenue-out.actual_cogs-out.actual_opex
    out["budget_operating_profit"] = out.budget_revenue-out.budget_cogs-out.budget_opex
    out["operating_profit_variance"] = out.actual_operating_profit-out.budget_operating_profit
    out["actual_operating_margin_pct"] = np.where(out.actual_revenue!=0,out.actual_operating_profit/out.actual_revenue*100,np.nan)
    out["budget_operating_margin_pct"] = np.where(out.budget_revenue!=0,out.budget_operating_profit/out.budget_revenue*100,np.nan)
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data-dir",default="data/synthetic")
    ap.add_argument("--output-dir",default="outputs")
    args=ap.parse_args()
    data_dir, outdir=Path(args.data_dir),Path(args.output_dir)
    outdir.mkdir(parents=True,exist_ok=True); (outdir/"charts").mkdir(parents=True,exist_ok=True)
    fact,account,region,dept=load_data(data_dir)
    validate(fact,account,region,dept)
    df=enrich(fact,account,region,dept)
    monthly=make_monthly(df); monthly.to_csv(outdir/"monthly_pnl_summary.csv",index=False,date_format="%Y-%m-%d")
    org=make_org_variance(df); org.to_csv(outdir/"department_profit_variance.csv",index=False)
    acct=df.groupby(["account_id","account_name","account_type"],as_index=False).agg(actual_amount=("actual_amount","sum"),budget_amount=("budget_amount","sum"),variance_amount=("variance_amount","sum"))
    acct["variance_pct"]=np.where(acct.budget_amount!=0,acct.variance_amount/acct.budget_amount*100,np.nan)
    acct.to_csv(outdir/"account_variance_summary.csv",index=False)
    region_sum=df[df.account_type=="Revenue"].groupby(["region_id","region_name"],as_index=False).agg(actual_revenue=("actual_amount","sum"),budget_revenue=("budget_amount","sum"))
    region_sum["revenue_variance"]=region_sum.actual_revenue-region_sum.budget_revenue
    region_sum.to_csv(outdir/"region_revenue_variance.csv",index=False)
    # KPI outputs: totals computed after joining details, with explicit account classifications.
    total_revenue_actual=float(df.loc[df.account_type=="Revenue","actual_amount"].sum())
    total_revenue_budget=float(df.loc[df.account_type=="Revenue","budget_amount"].sum())
    total_cogs_actual=float(df.loc[df.account_type=="COGS","actual_amount"].sum())
    total_cogs_budget=float(df.loc[df.account_type=="COGS","budget_amount"].sum())
    total_opex_actual=float(df.loc[df.account_type=="Operating Expense","actual_amount"].sum())
    total_opex_budget=float(df.loc[df.account_type=="Operating Expense","budget_amount"].sum())
    actual_op=total_revenue_actual-total_cogs_actual-total_opex_actual
    budget_op=total_revenue_budget-total_cogs_budget-total_opex_budget
    kpis=[
      ("Period start",str(df.month_start.min().date())),("Period end",str(df.month_start.max().date())),
      ("Fact rows",int(len(df))),("Unique departments",int(df.department_id.nunique())),("Regions",int(df.region_id.nunique())),
      ("Actual revenue",round(total_revenue_actual,2)),("Budget revenue",round(total_revenue_budget,2)),
      ("Revenue variance",round(total_revenue_actual-total_revenue_budget,2)),
      ("Actual COGS",round(total_cogs_actual,2)),("Budget COGS",round(total_cogs_budget,2)),
      ("Actual operating expenses",round(total_opex_actual,2)),("Budget operating expenses",round(total_opex_budget,2)),
      ("Actual operating profit",round(actual_op,2)),("Budget operating profit",round(budget_op,2)),
      ("Operating profit variance",round(actual_op-budget_op,2)),
      ("Actual operating margin pct",round(actual_op/total_revenue_actual*100,2) if total_revenue_actual else None),
      ("Budget operating margin pct",round(budget_op/total_revenue_budget*100,2) if total_revenue_budget else None),
    ]
    pd.DataFrame(kpis,columns=["metric","value"]).to_csv(outdir/"executive_kpis.csv",index=False)
    # Charts
    plot=monthly.copy(); plot["period"]=pd.to_datetime(plot.month_start).dt.strftime("%b")
    plt.figure(figsize=(10,5)); plt.plot(plot.period,plot.actual_revenue,marker="o",label="Actual Revenue"); plt.plot(plot.period,plot.budget_revenue,marker="o",label="Budget Revenue")
    plt.title("Monthly Revenue: Actual vs Budget"); plt.xlabel("Month"); plt.ylabel("Amount (USD)"); plt.legend(); plt.tight_layout(); plt.savefig(outdir/"charts/monthly_revenue_actual_vs_budget.png",dpi=150); plt.close()
    org_sorted=org.sort_values("operating_profit_variance")
    plt.figure(figsize=(9,5)); plt.bar(org_sorted.department_name,org_sorted.operating_profit_variance)
    plt.axhline(0,linewidth=1); plt.title("Operating Profit Variance by Department"); plt.xlabel("Department"); plt.ylabel("Actual Operating Profit − Budget (USD)"); plt.xticks(rotation=20,ha="right"); plt.tight_layout(); plt.savefig(outdir/"charts/operating_profit_variance_by_department.png",dpi=150); plt.close()
    exp=df[df.account_type=="Operating Expense"].groupby(["account_id","account_name"],as_index=False).agg(actual=("actual_amount","sum"),budget=("budget_amount","sum")); exp["variance"]=exp.actual-exp.budget; exp=exp.sort_values("variance")
    plt.figure(figsize=(10,5)); plt.bar(exp.account_name,exp.variance); plt.axhline(0,linewidth=1); plt.title("Operating Expense Variance by Account"); plt.xlabel("Expense Account"); plt.ylabel("Actual − Budget (USD)"); plt.xticks(rotation=25,ha="right"); plt.tight_layout(); plt.savefig(outdir/"charts/operating_expense_variance_by_account.png",dpi=150); plt.close()
    plt.figure(figsize=(9,5)); plt.scatter(monthly.actual_revenue,monthly.actual_operating_margin_pct); plt.xlabel("Actual Revenue (USD)"); plt.ylabel("Actual Operating Margin (%)"); plt.title("Revenue vs Operating Margin by Month"); plt.tight_layout(); plt.savefig(outdir/"charts/revenue_vs_operating_margin.png",dpi=150); plt.close()
    # Derive, don't hard-code, demo findings.
    best=org.sort_values("operating_profit_variance",ascending=False).iloc[0]; worst=org.sort_values("operating_profit_variance").iloc[0]
    rev_var=total_revenue_actual-total_revenue_budget; op_var=actual_op-budget_op
    over=exp.sort_values("variance",ascending=False).iloc[0]
    findings=[
      f"Actual revenue was ${total_revenue_actual:,.0f} against a budget of ${total_revenue_budget:,.0f}; the revenue variance was ${rev_var:,.0f} ({rev_var/total_revenue_budget*100:.2f}% of budget).",
      f"Actual operating profit was ${actual_op:,.0f} against a budget of ${budget_op:,.0f}; operating-profit variance was ${op_var:,.0f}.",
      f"{best.department_name} had the strongest operating-profit variance (${best.operating_profit_variance:,.0f}) in this synthetic dataset.",
      f"{worst.department_name} had the weakest operating-profit variance (${worst.operating_profit_variance:,.0f}) in this synthetic dataset.",
      f"{over.account_name} had the largest positive expense variance (actual above budget) at ${over.variance:,.0f}; review this result before drawing operational conclusions."
    ]
    (outdir/"findings.txt").write_text("SYNTHETIC DATA DEMO FINDINGS — not real company results\n\n"+"\n".join("- "+x for x in findings)+"\n",encoding="utf-8")
    print("Analysis complete")
    print("Rows:",len(df))
    print("Actual revenue:",round(total_revenue_actual,2),"Budget revenue:",round(total_revenue_budget,2))
    print("Operating profit variance:",round(op_var,2))
    print("Top department:",best.department_name,"Lowest department:",worst.department_name)

if __name__=="__main__": main()
