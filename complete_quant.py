"""Generate the induction report, metrics and charts from adjusted daily OHLCV.
Run: python complete_quant.py --csv data/reliance_prices.csv
Or in Colab: exec(open('complete_quant.py').read()); complete_submission(data)
"""
from pathlib import Path
import json, hashlib, argparse, platform, importlib.metadata
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

INITIAL = 100_000.0
FRACTION, SLIPPAGE, FEE = .10, .0005, .001
PERIODS = 252

def prepare(data):
    d = data.copy()
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    d.index = pd.to_datetime(d.index)
    if d.index.tz is not None: d.index = d.index.tz_localize(None)
    d = d.sort_index().loc['2016-01-01':'2024-12-31']
    cols = ['Open','High','Low','Close','Volume']
    if d.empty or not set(cols).issubset(d.columns): raise ValueError('Missing OHLCV data')
    if d.index.has_duplicates: raise ValueError('Duplicate dates: inspect source before proceeding')
    d[cols] = d[cols].apply(pd.to_numeric, errors='raise')
    if not np.isfinite(d[cols].to_numpy()).all(): raise ValueError('Non-finite OHLCV values')
    if (d[['Open','High','Low','Close']] <= 0).any().any(): raise ValueError('Non-positive prices')
    if (d['Volume'] < 0).any(): raise ValueError('Negative volume')
    if (d['High'] < d[['Open','Low','Close']].max(axis=1)-1e-6).any() or (d['Low'] > d[['Open','High','Close']].min(axis=1)+1e-6).any():
        raise ValueError('OHLC inconsistency: inspect source')
    return d

def backtest(data, start, end, window=20, threshold=-2., stop=None, max_hold=None):
    """Close-based decisions filled at next Open. Optional stop is NOT intraday."""
    d = data.loc[:end].copy()  # Never include dates after the evaluated period.
    std = d.Close.rolling(window).std(ddof=1).replace(0,np.nan)
    d['Z'] = (d.Close-d.Close.rolling(window).mean())/std
    d = d.loc[start:end]
    if len(d)<2: raise ValueError('At least two sessions are required')
    cash, qty, entry, outlay = INITIAL, 0, None, 0.
    rows = [{'Date': d.index[0], 'Equity':cash, 'Cash':cash, 'Shares':0}]
    trades, events = [], []
    for i in range(1,len(d)):
        prev, today = d.iloc[i-1], d.iloc[i]
        reason = None
        if qty:
            held = (i-1)-entry['index']+1
            if stop is not None and prev.Close <= entry['fill']*(1-stop): reason='close-stop'
            elif max_hold is not None and held>=max_hold: reason='holding-limit'
            elif pd.notna(prev.Z) and prev.Z>=0: reason='mean-exit'
            if reason:
                fill = today.Open*(1-SLIPPAGE)
                proceeds = qty*fill*(1-FEE)
                cash += proceeds
                trades.append({'Entry date':entry['date'], 'Exit date':d.index[i], 'Shares':qty,
                               'Entry fill':entry['fill'], 'Exit fill':fill, 'Net P&L':proceeds-outlay,
                               'Holding sessions':i-entry['index'],'Exit reason':reason})
                events.append({'Date':d.index[i],'Side':'SELL','Fill':fill,'Shares':qty,'Reason':reason})
                qty=0; entry=None; outlay=0.
        elif pd.notna(prev.Z) and prev.Z<threshold:
            fill=today.Open*(1+SLIPPAGE)
            qty=int(cash*FRACTION/(fill*(1+FEE)))
            if qty:
                outlay=qty*fill*(1+FEE); cash-=outlay
                entry={'date':d.index[i], 'fill':fill, 'index':i}
                events.append({'Date':d.index[i],'Side':'BUY','Fill':fill,'Shares':qty,'Reason':'z-entry'})
        rows.append({'Date':d.index[i],'Equity':cash+qty*today.Close,'Cash':cash,'Shares':qty})
    eq=pd.DataFrame(rows).set_index('Date')
    eq['Drawdown']=eq.Equity/eq.Equity.cummax()-1
    benchmark=INITIAL*d.Close/d.Close.iloc[0]
    t=pd.DataFrame(trades,columns=['Entry date','Exit date','Shares','Entry fill','Exit fill','Net P&L','Holding sessions','Exit reason'])
    e=pd.DataFrame(events,columns=['Date','Side','Fill','Shares','Reason'])
    liquidation=cash+qty*d.Close.iloc[-1]*(1-SLIPPAGE)*(1-FEE)
    return {'prices':d,'equity':eq,'trades':t,'events':e,'benchmark':benchmark,'liquidation':liquidation}

def metrics(run):
    eq=run['equity']; r=eq.Equity.pct_change().dropna()
    years=(eq.index[-1]-eq.index[0]).days/365.25
    sd=r.std(ddof=1); downside=np.sqrt(np.mean(np.minimum(r,0)**2))
    pnl=run['trades']['Net P&L']; wins=pnl[pnl>0]; losses=pnl[pnl<0]
    return {
      'Cumulative return (%)':100*(eq.Equity.iloc[-1]/INITIAL-1),
      'Annualized return / CAGR (%)':100*((eq.Equity.iloc[-1]/INITIAL)**(1/years)-1) if years>0 else np.nan,
      'Sharpe ratio':np.sqrt(PERIODS)*r.mean()/sd if sd>0 else np.nan,
      'Sortino ratio':np.sqrt(PERIODS)*r.mean()/downside if downside>0 else np.nan,
      'Maximum drawdown (%)':100*eq.Drawdown.min(),
      'Win rate (%)':100*(pnl>0).mean() if len(pnl) else np.nan,
      'Completed trades':len(pnl),
      'Profit factor':wins.sum()/abs(losses.sum()) if len(losses) else np.nan,
      'Average winning trade (INR)':wins.mean(),
      'Average losing trade (INR)':losses.mean(),
      'Maximum winning trade (INR)':wins.max(),
      'Maximum losing trade (INR)':losses.min(),
      'Benchmark return (%)':100*(run['benchmark'].iloc[-1]/INITIAL-1),
      'Average invested exposure (%)':100*(eq.Shares*run['prices'].Close/eq.Equity).mean(),
      'Ending equity (INR)':eq.Equity.iloc[-1],
      'Open adjusted-price units':eq.Shares.iloc[-1],
      'Estimated liquidation return (%)':100*(run['liquidation']/INITIAL-1)
    }

def save_charts(run,label,directory):
    d=run['prices']; eq=run['equity']; bh=run['benchmark']; ev=run['events']
    paths=[]
    for kind in ['equity','drawdown','trades']:
        fig,ax=plt.subplots(figsize=(10,3.4))
        if kind=='equity':
            ax.plot(eq.index,(eq.Equity/INITIAL-1)*100,label='Strategy, after costs',color='#1565a8')
            ax.plot(bh.index,(bh/INITIAL-1)*100,label='Reliance buy-and-hold, before costs',color='#db7a24')
            ax.set_ylabel('Cumulative return (%)')
        elif kind=='drawdown':
            ax.plot(eq.index,eq.Drawdown*100,label='Strategy',color='#1565a8')
            ax.plot(bh.index,(bh/bh.cummax()-1)*100,label='Buy-and-hold',color='#db7a24')
            ax.set_ylabel('Drawdown (%)')
        else:
            ax.plot(d.index,d.Close,label='Adjusted close',color='#50677f',linewidth=.9)
            for side,marker,color in [('BUY','^','#168045'),('SELL','v','#c33141')]:
                e=ev.loc[ev.Side==side]
                ax.scatter(e.Date,e.Fill,marker=marker,color=color,s=40,label=side+' at adjusted Open + slippage',zorder=3)
            ax.set_ylabel('Adjusted price (INR)')
        ax.set_title(label+' | '+kind.capitalize());ax.set_xlabel('Date');ax.grid(alpha=.2);ax.legend(fontsize=8)
        fig.tight_layout();path=directory/(label.split()[0].lower()+'_'+kind+'.png')
        fig.savefig(path,dpi=180);plt.close(fig);paths.append(path)
    return paths

def fmt(v):
    return 'N/A' if pd.isna(v) or not np.isfinite(v) else f'{v:,.2f}'

def create_report(out, runs, table, sensitivity, regimes, risk, data, metadata):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from xml.sax.saxutils import escape
    styles=getSampleStyleSheet()
    styles['BodyText'].fontSize=9;styles['BodyText'].leading=12
    styles['Heading1'].fontSize=18;styles['Heading1'].textColor=colors.HexColor('#163a5f')
    story=[]
    def p(text):story.append(Paragraph(escape(text),styles['BodyText']));story.append(Spacer(1,7))
    def h(text):story.append(Paragraph(escape(text),styles['Heading1']));story.append(Spacer(1,8))
    def chart(path):story.append(Image(str(path),width=475,height=161.5));story.append(Spacer(1,6))
    def tbl(rows,widths):
        wrapped=[[Paragraph(escape(str(c)),styles['BodyText']) for c in row] for row in rows]
        t=Table(wrapped,colWidths=widths,repeatRows=1)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7eef5')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),4),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#163a5f')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f7f9fb')])]))
        story.append(t);story.append(Spacer(1,8))
    test=table['Final test 2024'];dev=table['Development 2016-2022']
    h('Reliance: testing a mean-reversion idea')
    p('CFA Club, IIT Indore | Finance & Quant, Track 1 | Adrij Sarkar')
    p('Hypothesis: a large negative deviation from a recent average may be followed by a rebound. A 20-session mean and a -2 entry threshold provide a simple, interpretable starting rule. They are fixed baseline choices, not statistically proven optimal values. Stock-price mean reversion is a hypothesis to test, not an assumed property.')
    p('Reliance was selected as a widely traded Indian equity with a long daily price history. Daily OHLCV is sufficient to form closing-price signals and model next-session fills. The strategy does not model order-book liquidity or prove that quoted opens were executable.')
    p(f'Data: Yahoo Finance via yfinance, RELIANCE.NS; {len(data):,} sessions from {data.index[0].date()} to {data.index[-1].date()}. Prices are adjusted OHLC. The download is checked for missing/non-finite values, duplicates, non-positive prices and invalid OHLC ordering; suspicious data cause an error rather than automatic deletion. Extreme returns are retained absent evidence of a data error.')
    tbl([['Rule','Baseline specification'],['Signal','Z = (Close - trailing 20-session mean) / sample standard deviation (ddof=1).'],['Entry / exit','Buy when previous Z < -2; sell when previous Z >= 0; fill at current Open.'],['Capital / sizing','INR 100,000; 10% of available cash including entry fee; integer adjusted-price units; one long position; no leverage.'],['Costs','0.05% adverse slippage plus 0.10% fee on each buy and sell. Idle cash earns zero.'],['Risk control','Position-size cap only; baseline has no stop or time limit. It can hold a losing position indefinitely. A separate development-only experiment adds explicit exit controls.']],[90,385])
    p(f'Final-test outcome: {fmt(test["Cumulative return (%)"])}% strategy return versus {fmt(test["Benchmark return (%)"])}% buy-and-hold, with {int(test["Completed trades"])} completed trades. Lower exposure helps explain lower drawdown; this is not evidence of superior risk-adjusted performance across markets.')
    story.append(PageBreak());h('Performance metrics and conventions')
    p('Development: first session of 2016 through the last session of 2022. Final test: 29 December 2023 baseline through 31 December 2024. Each run starts flat with INR 100,000. Prior prices supply trailing indicators, but all order decisions use the preceding session only.')
    rows=[['Metric','Development','Final test']]+[[idx,fmt(row.iloc[0]),fmt(row.iloc[1])] for idx,row in table.iterrows()]
    tbl(rows,[265,105,105])
    p('Returns are daily close-to-close portfolio returns, including idle cash and simulated trading costs. CAGR uses actual elapsed days / 365.25. Sharpe = sqrt(252) x mean(daily return) / sample standard deviation. Risk-free rate is assumed 0% annually. Sortino uses the same numerator and the root mean square of min(daily return, 0) over ALL daily observations; the minimum acceptable return is 0%.')
    p('Trade statistics use completed trades only and net P&L after entry/exit costs. Open-position gains/losses enter equity metrics, but not completed-trade statistics. Loss amounts are negative. N/A denotes no applicable wins/losses/trades, or a zero risk denominator; profit factor is N/A without any losing trades. Estimated liquidation is a separate last-close scenario, not a counted strategy exit.')
    story.append(PageBreak());h('Development behaviour and validation')
    chart(out/'figures/development_equity.png');chart(out/'figures/development_drawdown.png')
    p(f'Development strategy return is {fmt(dev["Cumulative return (%)"])}%, compared with {fmt(dev["Benchmark return (%)"])}% for the benchmark. Average invested exposure is {fmt(dev["Average invested exposure (%)"])}%; interpreting the drawdown without this exposure would overstate the evidence for risk control.')
    p(f'Validation is a slice of a continuous 2016-2023 run: {metadata["validation"]["Return (%)"]:.2f}% strategy return, {metadata["validation"]["Benchmark (%)"]:.2f}% benchmark return and {metadata["validation"]["Drawdown (%)"]:.2f}% drawdown, with {metadata["validation"]["Completed trades entered in 2023"]} completed trades entered in 2023. This is NOT a reset portfolio. Original exploratory work included validation data, so validation was not fully unseen. The separately labelled 2024 baseline was evaluated after rules were fixed.')
    p('Post-review parameter and risk experiments use development data only. They were added after viewing the baseline final-test outcome and must be described as exploratory. No new variant is claimed to have an untouched 2024 test; further confirmation requires genuinely unseen data.')
    story.append(PageBreak());h('Final test: returns, drawdown and execution')
    chart(out/'figures/final_equity.png');chart(out/'figures/final_drawdown.png');chart(out/'figures/final_trades.png')
    p(f'Final marked equity: INR {fmt(test["Ending equity (INR)"])}. Units still held: {int(test["Open adjusted-price units"])}. Estimated liquidation return: {fmt(test["Estimated liquidation return (%)"])}%. Trade markers include the entry of an unfinished position; there is no fabricated year-end sell.')
    p('Benchmark rationale: holding the same stock isolates whether timing its entries/exits improves on passive ownership. This is a permitted alternative to an index benchmark, but is not a broad-market comparison. The benchmark is a fully invested adjusted-close ratio before costs; the strategy is partly invested and after costs.')
    story.append(PageBreak());h('Development-only robustness checks')
    p(f'Neighbouring returns range from {sensitivity.Return.min():.2f}% to {sensitivity.Return.max():.2f}%, showing sensitivity to the rule. The same development period and cost assumptions are used for every combination below. The original window=20 and entry=-2 remain the baseline regardless of this table. A small grid is a sensitivity diagnostic, not proof of robustness.')
    rows=[['Window','Entry Z','Return %','Max DD %','Trades']]+[[int(r.Window),r.Entry,fmt(r.Return),fmt(r.Drawdown),int(r.Trades)] for r in sensitivity.itertuples()]
    tbl(rows,[65,65,115,115,115])
    p('Market conditions are classified using the PREVIOUS session\'s trailing 60-session stock return: rising above +5%, falling below -5%, sideways otherwise. Unavailable warm-up observations are excluded. Conditional averages combine non-contiguous days and are descriptive, not separate investable backtests.')
    rows=[['Regime','Sessions','Mean daily strategy %','Mean daily benchmark %']]+[[r.Regime,int(r.Sessions),f'{r.StrategyMean:.4f}',f'{r.BenchmarkMean:.4f}'] for r in regimes.itertuples()]
    tbl(rows,[100,65,155,155])
    p('Explicit risk-control experiment: retain sizing and add a 5% loss trigger based on the preceding adjusted close versus entry fill, plus a maximum 20 held sessions. Both exits fill at the NEXT open with costs. A gap can produce a loss greater than 5%; this is not an intraday guaranteed stop.')
    rows=[['Development variant','Return %','Max DD %','Trades']]+[[r.Variant,fmt(r.Return),fmt(r.Drawdown),int(r.Trades)] for r in risk.itertuples()]
    tbl(rows,[205,90,90,90])
    p('The added exits reduced development return and made maximum drawdown worse in this sample. A stop does not automatically improve performance; this experiment is not adopted as the baseline.')
    story.append(PageBreak());h('Limitations, resources and assistance')
    p('Adjusted OHLC makes corporate-action handling consistent within this simplified price simulation, but is not a point-in-time reconstruction of actual share quantities, splits and dividend cash payments. Integer sizing on retrospectively adjusted prices can depend on future adjustment factors. These prices are research units rather than historical executable rupee quotes; a production study should use raw execution prices and explicit action accounting.')
    p('The strategy has one stock, few final-test trades, fixed costs, no interest on cash, no market-impact model, and no baseline stop/time limit. Exposure differs from the benchmark. A high win rate does not imply profitability: infrequent large losses can outweigh small wins. Lower loss than buy-and-hold in one year is not proof of persistent advantage.')
    p('Possible improvements: corporate-action accounting with raw fills; point-in-time data snapshots; development-only stop/time-limit assessment; broader stock universes; exposure-matched and cost-matched benchmarks; and a genuinely new held-out period. Do not retune parameters to the observed 2024 loss.')
    p('Resources actually used for this submission and completion work:')
    for s in SOURCES:p(s)
    p('Assistance acknowledgement: ChatGPT/Codex assisted with explanations, code drafting and debugging, repository review, metrics and chart implementation, and report preparation. The student must review the delivered work, disclose any other resources used, and be able to explain all code and conclusions. This acknowledgement does not claim independent authorship of assisted code.')
    p('Reproducibility: a dated adjusted-price CSV snapshot is included. The output includes a data fingerprint, actual package versions and generated metrics CSVs. Dependencies are listed in requirements.txt. The notebook can use a locally saved adjusted-price CSV or download again from Yahoo; provider revisions can change results. Original analysis cells are retained as an audit trail.')
    p('Data SHA-256: '+metadata['data_sha256'])
    def footer(canvas,doc):
        canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#64748b'))
        canvas.drawString(45,28,'CFA induction | Reliance mean reversion | Educational research')
        canvas.drawRightString(550,28,str(doc.page))
    SimpleDocTemplate(str(out/'quant_technical_report.pdf'),title='Reliance Mean-Reversion Backtest',author='Adrij Sarkar (with disclosed ChatGPT/Codex assistance)',pagesize=(595.28,841.89),rightMargin=50,leftMargin=50,topMargin=40,bottomMargin=45).build(story,onFirstPage=footer,onLaterPages=footer)

SOURCES=[
 'CFA Club, IIT Indore. Induction Task 2026, Finance & Quant, pp. 5-8 (user-supplied task PDF).',
 'Yahoo Finance, RELIANCE.NS historical prices: https://finance.yahoo.com/quote/RELIANCE.NS/history/',
 'yfinance download API: https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html',
 'pandas project (data frames and rolling calculations): https://pandas.pydata.org/docs/',
 'NumPy project (numerical calculations): https://numpy.org/doc/',
 'Matplotlib project (plots): https://matplotlib.org/stable/',
 'ReportLab project (PDF generation): https://docs.reportlab.com/',
 'Original student repository: https://github.com/adrijsarkar07/CFA-INDUCTION'
]

def complete_submission(data, output_dir='outputs'):
    data=prepare(data);out=Path(output_dir);(out/'figures').mkdir(parents=True,exist_ok=True)
    runs={'Development 2016-2022':backtest(data,'2016-01-01','2022-12-31'),
          'Final test 2024':backtest(data,'2023-12-29','2024-12-31')}
    table=pd.DataFrame({name:metrics(run) for name,run in runs.items()})
    table.to_csv(out/'performance_metrics.csv',na_rep='N/A')
    for name,run in runs.items():
        stem=name.split()[0].lower()
        run['equity'].to_csv(out/(stem+'_equity.csv'))
        run['trades'].to_csv(out/(stem+'_trades.csv'),index=False)
        run['events'].to_csv(out/(stem+'_events.csv'),index=False)
        save_charts(run,name,out/'figures')
    sensitivity=[]
    for w in [15,20,25]:
        for threshold in [-2.5,-2.,-1.5]:
            m=metrics(backtest(data,'2016-01-01','2022-12-31',window=w,threshold=threshold))
            sensitivity.append({'Window':w,'Entry':threshold,'Return':m['Cumulative return (%)'],'Drawdown':m['Maximum drawdown (%)'],'Trades':m['Completed trades']})
    sensitivity=pd.DataFrame(sensitivity);sensitivity.to_csv(out/'development_sensitivity.csv',index=False)
    dev=runs['Development 2016-2022'];trend=dev['prices'].Close.pct_change(60).shift(1)
    states=pd.Series(np.select([trend>.05,trend<-.05],['Rising','Falling'],default='Sideways'),index=trend.index)
    frame=pd.DataFrame({'Regime':states,'StrategyMean':dev['equity'].Equity.pct_change()*100,'BenchmarkMean':dev['benchmark'].pct_change()*100}).loc[trend.notna()].dropna()
    regimes=frame.groupby('Regime').agg(Sessions=('StrategyMean','size'),StrategyMean=('StrategyMean','mean'),BenchmarkMean=('BenchmarkMean','mean')).reset_index()
    regimes.to_csv(out/'development_regimes.csv',index=False)
    controlled=backtest(data,'2016-01-01','2022-12-31',stop=.05,max_hold=20)
    risk=[]
    for label,run in [('Baseline: sizing only',dev),('5% close-stop + 20 sessions',controlled)]:
        m=metrics(run);risk.append({'Variant':label,'Return':m['Cumulative return (%)'],'Drawdown':m['Maximum drawdown (%)'],'Trades':m['Completed trades']})
    risk=pd.DataFrame(risk);risk.to_csv(out/'development_risk_experiment.csv',index=False)
    controlled['trades'].to_csv(out/'development_risk_trades.csv',index=False)
    continuous=backtest(data,'2016-01-01','2023-12-31')
    ve=continuous['equity'].loc['2023', 'Equity']; vc=continuous['prices'].loc[ve.index,'Close']
    vt=continuous['trades']; vn=int((pd.to_datetime(vt['Entry date']).dt.year==2023).sum())
    val={'Return (%)':100*(ve.iloc[-1]/ve.iloc[0]-1),'Benchmark (%)':100*(vc.iloc[-1]/vc.iloc[0]-1),'Drawdown (%)':100*(ve/ve.cummax()-1).min(),'Completed trades entered in 2023':vn}
    pd.Series(val).to_csv(out/'validation_slice.csv',header=['Value'])
    metadata={'validation':val,'generated_utc':pd.Timestamp.now(tz='UTC').isoformat(),'data_sha256':hashlib.sha256(data.to_csv().encode()).hexdigest(),'rows':len(data),'first_date':str(data.index.min()),'last_date':str(data.index.max()),'python':platform.python_version(),'packages':{}}
    for package in ['pandas','numpy','matplotlib','yfinance','reportlab']:
        try:metadata['packages'][package]=importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:pass
    (out/'run_metadata.json').write_text(json.dumps(metadata,indent=2))
    create_report(out,runs,table,sensitivity,regimes,risk,data,metadata)
    print(table.to_string(na_rep='N/A',float_format=lambda x:f'{x:,.4f}'))
    print('\nReport, charts, trade logs and metrics saved to:',out.resolve())
    return table,runs

if __name__=='__main__' and '__file__' in globals():
    parser=argparse.ArgumentParser();parser.add_argument('--csv');parser.add_argument('--output',default='outputs');args=parser.parse_args()
    if args.csv: d=pd.read_csv(args.csv,index_col=0,parse_dates=True)
    else:
        import yfinance as yf
        d=yf.download('RELIANCE.NS',start='2016-01-01',end='2025-01-01',auto_adjust=True,actions=True,multi_level_index=False,progress=False)
    complete_submission(d,args.output)
