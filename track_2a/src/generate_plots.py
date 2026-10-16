#!/usr/bin/env python3
"""
@NOTE: MOSTLY LLM GENERATED REPORT PLOT

Regenerate token score CSV and interactive HTML plot from result.jsonl.

Run from this folder: py -3 generate_plots.py
Optional input path: py -3 generate_plots.py path/to/result.jsonl
"""
import csv
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from my_folders import RESULTS_PATH

ROOT = Path(__file__).resolve().parent
SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else RESULTS_PATH / "result_on_test.jsonl"
if not SOURCE.is_absolute():
    SOURCE = (Path.cwd() / SOURCE).resolve()
CSV_PATH = RESULTS_PATH / "label_scores_by_token.csv"
HTML_PATH = RESULTS_PATH / "label_score_plot.html"

points = []
rows = []
raw_scores = []
by_label = defaultdict(list)
label_counts = Counter()
scored = unscored = records = result_groups = 0

with SOURCE.open(encoding="utf-8") as source:
    for line_no, line in enumerate(source, 1):
        if not line.strip():
            continue
        record = json.loads(line)
        records += 1
        entry = record["entry"]
        side = record["side"]
        labels = entry[f"labels_{side}"]
        language = entry[f"lang_{side}_id"]
        language_pair = "|".join(sorted((entry["lang_A_id"], entry["lang_B_id"])))
        entry_id = entry.get("id", f"line_{line_no}")
        sums = [0.0] * len(labels)
        counts = [0] * len(labels)

        for result in record.get("result", []):
            result_groups += 1
            score = float(result["score"])
            raw_scores.append(score)
            for index in result.get("tks_idx", []):
                index = int(index)
                if 0 <= index < len(labels):
                    sums[index] += score
                    counts[index] += 1

        for index, raw_label in enumerate(labels):
            label = float(raw_label)
            label_counts[label] += 1
            score = sums[index] / counts[index] if counts[index] else -1.0
            row = {
                "entry_id": entry_id,
                "side": side,
                "language": language,
                "language_pair": language_pair,
                "tks_idx": index,
                "label": label,
                "score": score,
                "score_count": counts[index],
                "score_sum": sums[index],
            }
            rows.append(row)
            if counts[index]:
                scored += 1
                by_label[label].append(score)
                points.append({**{k: row[k] for k in ("entry_id", "side", "language", "language_pair", "tks_idx", "label", "score", "score_count")}})
            else:
                unscored += 1

with CSV_PATH.open("w", newline="", encoding="utf-8") as output:
    writer = csv.DictWriter(output, fieldnames=["entry_id", "side", "language", "language_pair", "tks_idx", "label", "score", "score_count", "score_sum"])
    writer.writeheader()
    writer.writerows(rows)

mean = statistics.mean
median = statistics.median
visible = [p for p in points if p["label"] != -1]
x = [p["label"] for p in visible]
y = [p["score"] for p in visible]
if len(x) > 1:
    x_mean, y_mean = mean(x), mean(y)
    covariance = sum((a - x_mean) * (b - y_mean) for a, b in zip(x, y)) / (len(x) - 1)
    pearson = covariance / (statistics.stdev(x) * statistics.stdev(y))
else:
    pearson = float("nan")
label_stats = []
for label in sorted(label_counts):
    values = by_label.get(label, [])
    label_stats.append({
        "label": label,
        "all_tokens": label_counts[label],
        "scored_tokens": len(values),
        "mean": mean(values) if values else None,
        "median": median(values) if values else None,
    })
stats = {
    "records": records,
    "result_groups": result_groups,
    "token_rows": len(rows),
    "scored_tokens": scored,
    "unscored_tokens": unscored,
    "raw_min": min(raw_scores),
    "raw_max": max(raw_scores),
    "raw_mean": mean(raw_scores),
    "pearson": pearson,
    "labels": label_stats,
}

# Data is embedded so the plot works locally without a server or CDN.
data_json = json.dumps(points, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
stats_json = json.dumps(stats, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
html_template = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Label vs token score</title><style>
:root{color-scheme:light;--ink:#172333;--muted:#637184;--line:#dce3eb;--panel:#fff;--bg:#f4f7fb}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,-apple-system,Segoe UI,sans-serif}main{max-width:1200px;margin:auto;padding:28px 22px 40px}h1{font-size:clamp(25px,3vw,35px);letter-spacing:-.03em;margin:0 0 5px}.sub{color:var(--muted);margin-bottom:18px}.grid{display:grid;grid-template-columns:repeat(4,minmax(130px,1fr));gap:11px;margin:0 0 16px}.stat,.card{background:var(--panel);border:1px solid var(--line);border-radius:13px;box-shadow:0 5px 20px #23364d0a}.stat{padding:13px 15px}.stat .k{font-size:12px;color:var(--muted)}.stat .v{font-size:21px;font-weight:650;margin-top:2px}.card{padding:17px;margin-bottom:15px}.controls{display:flex;gap:14px;align-items:end;flex-wrap:wrap;margin-bottom:9px}.control{display:grid;gap:5px;color:var(--muted);font-size:13px}select{min-width:170px;padding:9px 32px 9px 10px;border:1px solid var(--line);border-radius:8px;background:white;color:var(--ink);font:inherit}.summary{margin-left:auto;color:var(--muted);font-size:13px}canvas{display:block;width:100%;height:510px}.legend{display:flex;gap:16px;flex-wrap:wrap;color:var(--muted);font-size:13px;margin:8px 2px}.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:right;padding:9px 10px;border-bottom:1px solid var(--line)}th:first-child,td:first-child{text-align:left}th{color:var(--muted);font-weight:600}.note{color:var(--muted);font-size:13px;margin:10px 2px 0}.section-title{font-size:17px;margin:0 0 10px}@media(max-width:760px){.grid{grid-template-columns:repeat(2,1fr)}canvas{height:400px}}@media(max-width:430px){.grid{grid-template-columns:1fr 1fr}.stat .v{font-size:17px}}
</style></head><body><main><h1>Label vs token score</h1><div class="sub">Full available dataset. Each plotted point is a token index with its result-group scores averaged.</div>
<div id="stats" class="grid"></div><section class="card"><h2 class="section-title">Score by label</h2><table><thead><tr><th>Label</th><th>All tokens</th><th>Scored</th><th>Mean score</th><th>Median score</th></tr></thead><tbody id="labelTable"></tbody></table><p class="note">The plot excludes label −1 and unscored tokens. The CSV retains every index; missing scores are stored as −1. Raw result scores are all ≤ 0, though grouped averages can approach zero without reaching exactly zero.</p></section>
<section class="card"><div class="controls"><label class="control">Language pair (order ignored)<select id="language"><option value="*">All pairs</option></select></label><label class="control">Side<select id="side"><option value="*">A and B</option><option>A</option><option>B</option></select></label><div id="summary" class="summary"></div></div><canvas id="plot" aria-label="Scatter plot of label versus average score"></canvas><div class="legend"><span><i class="dot" style="background:#2563eb"></i>label 0.0</span><span><i class="dot" style="background:#f97316"></i>label 0.2–0.8</span><span><i class="dot" style="background:#059669"></i>label 1.0</span><span><i class="dot" style="background:#111827"></i>mean per label</span><span><i class="dot" style="background:#a855f7"></i>median per label</span></div><p class="note">Hover over a point for its entry, side, language pair, token index, score and number of scores averaged. Black circles and line show means; purple dashed line shows medians for each label under current filters. Pearson correlation across plotted token means: <b id="corr"></b>.</p></section></main>
<script>const data=__DATA__,stats=__STATS__;const langSel=document.getElementById('language'),sideSel=document.getElementById('side'),canvas=document.getElementById('plot'),ctx=canvas.getContext('2d');const fmt=(v,n=3)=>Number(v).toFixed(n);document.getElementById('stats').innerHTML=[['Records',stats.records],['Score groups',stats.result_groups],['Token indices',stats.token_rows],['Scored / plotted',stats.scored_tokens.toLocaleString()],['Unscored indices',stats.unscored_tokens.toLocaleString()],['Raw score range',`${fmt(stats.raw_min,2)} to ${fmt(stats.raw_max,5)}`],['Raw score mean',fmt(stats.raw_mean,3)],['Pearson r (label ≠ −1)',fmt(stats.pearson,3)]].map(a=>`<div class="stat"><div class="k">${a[0]}</div><div class="v">${a[1]}</div></div>`).join('');document.getElementById('labelTable').innerHTML=stats.labels.map(s=>`<tr><td>${s.label}</td><td>${s.all_tokens.toLocaleString()}</td><td>${s.scored_tokens.toLocaleString()}</td><td>${s.mean===null?'—':fmt(s.mean,3)}</td><td>${s.median===null?'—':fmt(s.median,3)}</td></tr>`).join('');document.getElementById('corr').textContent=fmt(stats.pearson,3);[...new Set(data.map(p=>p.language_pair))].sort().forEach(l=>{let o=document.createElement('option');o.value=l;o.textContent=l.split('|').join(' ↔ ');langSel.appendChild(o)});const color=v=>v===0?'#2563eb':v===1?'#059669':'#f97316';let plotted=[];
function draw(){const r=canvas.getBoundingClientRect(),dpr=devicePixelRatio||1;canvas.width=Math.round(r.width*dpr);canvas.height=Math.round(r.height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);const W=r.width,H=r.height,L=68,R=20,T=20,B=52;const f=data.filter(p=>p.label!==-1&&(langSel.value==='*'||p.language_pair===langSel.value)&&(sideSel.value==='*'||p.side===sideSel.value));plotted=[];const ys=f.map(p=>p.score),ymin=Math.min(0,...ys),ymax=Math.max(0,...ys),pad=(ymax-ymin)*.06||1;const lo=ymin-pad,hi=0,xmin=0,xmax=1;const X=v=>L+(v-xmin)/(xmax-xmin)*(W-L-R),Y=v=>T+(hi-v)/(hi-lo)*(H-T-B);ctx.clearRect(0,0,W,H);ctx.font='12px system-ui';ctx.lineWidth=1;ctx.strokeStyle='#e6ebf1';ctx.fillStyle='#637184';ctx.textAlign='right';ctx.textBaseline='middle';for(let k=0;k<=5;k++){let v=lo+(hi-lo)*k/5,yy=Y(v);ctx.beginPath();ctx.moveTo(L,yy);ctx.lineTo(W-R,yy);ctx.stroke();ctx.fillText(v.toFixed(1),L-9,yy)}ctx.textAlign='center';ctx.textBaseline='top';for(const v of [0,.2,.4,.6,.8,1]){let xx=X(v);ctx.beginPath();ctx.moveTo(xx,T);ctx.lineTo(xx,H-B);ctx.stroke();ctx.fillText(v.toFixed(1),xx,H-B+9)}ctx.strokeStyle='#718096';ctx.beginPath();ctx.moveTo(L,T);ctx.lineTo(L,H-B);ctx.lineTo(W-R,H-B);ctx.stroke();ctx.fillStyle='#344256';ctx.font='13px system-ui';ctx.fillText('label_x[i]',(L+W-R)/2,H-18);ctx.save();ctx.translate(17,(T+H-B)/2);ctx.rotate(-Math.PI/2);ctx.fillText('this_created_array[i] (mean score)',0,0);ctx.restore();const means=[...new Set(f.map(p=>p.label))].sort((a,b)=>a-b).map(label=>{const group=f.filter(p=>p.label===label);const vals=group.map(p=>p.score).sort((a,b)=>a-b);const mid=Math.floor(vals.length/2);return {label,score:group.reduce((s,p)=>s+p.score,0)/group.length,median:vals.length%2?vals[mid]:(vals[mid-1]+vals[mid])/2,n:group.length}});if(means.length>1){ctx.save();ctx.strokeStyle='#111827';ctx.lineWidth=2.5;ctx.beginPath();means.forEach((m,i)=>{const px=X(m.label),py=Y(m.score);if(i===0)ctx.moveTo(px,py);else ctx.lineTo(px,py)});ctx.stroke();ctx.strokeStyle='#a855f7';ctx.lineWidth=2.5;ctx.setLineDash([7,5]);ctx.beginPath();means.forEach((m,i)=>{const px=X(m.label),py=Y(m.median);if(i===0)ctx.moveTo(px,py);else ctx.lineTo(px,py)});ctx.stroke();ctx.setLineDash([]);ctx.restore()}for(const p of f){let px=X(p.label),py=Y(p.score);ctx.globalAlpha=.6;ctx.fillStyle=color(p.label);ctx.beginPath();ctx.arc(px,py,3.3,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;plotted.push({p,px,py})}for(const m of means){let px=X(m.label),py=Y(m.score),my=Y(m.median);ctx.fillStyle='#111827';ctx.strokeStyle='white';ctx.lineWidth=2;ctx.beginPath();ctx.arc(px,py,6,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.fillStyle='#a855f7';ctx.beginPath();ctx.arc(px,my,5,0,Math.PI*2);ctx.fill();ctx.stroke();plotted.push({p:{label:m.label,score:m.score,score_count:m.n,entry_id:'Mean per label (filtered)',side:'all',language_pair:langSel.value==='*'?'all':langSel.value,tks_idx:'all'},px,py},{p:{label:m.label,score:m.median,score_count:m.n,entry_id:'Median per label (filtered)',side:'all',language_pair:langSel.value==='*'?'all':langSel.value,tks_idx:'all'},px,py:my})}document.getElementById('summary').textContent=`${f.length.toLocaleString()} plotted tokens · ${new Set(f.map(p=>p.entry_id)).size} entries`}
canvas.addEventListener('mousemove',ev=>{let r=canvas.getBoundingClientRect(),mx=ev.clientX-r.left,my=ev.clientY-r.top,hit=null,dist=100;for(const q of plotted){let d=(q.px-mx)**2+(q.py-my)**2;if(d<dist){dist=d;hit=q}}canvas.title=hit&&dist<140?`${hit.p.entry_id} · side ${hit.p.side} · ${hit.p.language} · tks_idx ${hit.p.tks_idx} · label ${hit.p.label} · mean score ${hit.p.score.toFixed(5)} · ${hit.p.score_count} score(s)`:''});langSel.addEventListener('change',draw);sideSel.addEventListener('change',draw);new ResizeObserver(draw).observe(canvas);draw();</script></body></html>'''
HTML_PATH.write_text(html_template.replace("__DATA__", data_json).replace("__STATS__", stats_json), encoding="utf-8")
print(f"Read {records} records, {result_groups} result groups and {len(rows)} token indices.")
print(f"Wrote {CSV_PATH.name} and {HTML_PATH.name}; plot omits label -1 and connects filtered per-label means.")
