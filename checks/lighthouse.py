"""Section 9: 3 cold mobile Lighthouse runs per key route; report medians."""
import argparse, json, os, statistics, subprocess, urllib.request, urllib.error, time
from common import *
KEY={'home':'index.html','admission':'admission.html','catalog':'catalog.html','program':'Program.html?id=9797','campus':'campus.html','schedule':'schedule.html','search':'search.html?q=общага','concept':'concept.html'}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pages',nargs='+',choices=list(KEY),default=list(KEY));parser.add_argument('--skip-public',action='store_true');args=parser.parse_args()
    cli=os.environ.get('LIGHTHOUSE_CLI','/tmp/urfu-audit/node_modules/lighthouse/cli/index.js');rows=[]
    for label in args.pages:
        path=KEY[label]
        runs=[]
        for i in range(3):
            output=RESULTS/f'lh-{label}-{i+1}.json';env={**os.environ,'CHROME_PATH':'/usr/bin/chromium'}
            r=subprocess.run(['node',cli,BASE+path,"--chrome-flags=--headless --no-sandbox",'--output=json','--output-path='+str(output),'--only-categories=performance,accessibility,best-practices,seo','--quiet'],env=env,capture_output=True,text=True)
            if r.returncode:runs.append({'error':r.stderr[-500:]});continue
            d=json.loads(output.read_text());a=d['audits'];runs.append({'scores':{k:round(v['score']*100) for k,v in d['categories'].items()},'LCP':a['largest-contentful-paint']['numericValue'],'CLS':a['cumulative-layout-shift']['numericValue'],'TBT':a['total-blocking-time']['numericValue'],'transfer':a['total-byte-weight']['numericValue'],'time':d['fetchTime']})
            print(label,i+1,runs[-1],flush=True)
            # Keep detailed failures, not megabytes of duplicate traces and screenshots.
            output.write_text(json.dumps({'lighthouseVersion':d['lighthouseVersion'],'requestedUrl':d['requestedUrl'],'fetchTime':d['fetchTime'],'configSettings':d['configSettings'],'categories':d['categories'],'audits':{k:v for k,v in a.items() if v.get('score') not in [1,None] or k in ['largest-contentful-paint','cumulative-layout-shift','total-blocking-time','total-byte-weight']}},ensure_ascii=False,indent=2))
        valid=[r for r in runs if 'scores'in r]
        med={'scores':{k:statistics.median(r['scores'][k] for r in valid) for k in valid[0]['scores']},**{k:statistics.median(r[k] for r in valid)for k in ['LCP','CLS','TBT','transfer']}} if valid else {}
        rows.append({'page':path,'runs':runs,'median':med})
    save('09-lighthouse',{'server':'Local gzip HTTP server; not public PageSpeed Insights','pages':rows})
    if args.skip_public:return
    # Public PSI is a separate service and can be unavailable without an API quota.
    url='https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url='+urllib.parse.quote(PUBLIC,safe='')+'&strategy=mobile&category=performance&category=accessibility&category=best-practices&category=seo'
    try:
        with urllib.request.urlopen(url,timeout=55) as r:d=json.load(r)
        save('09-pagespeed',{'url':url,'status':'passed','report':d})
    except Exception as e:save('09-pagespeed',{'url':url,'status':'unavailable','reason':str(e),'manual_report':'https://pagespeed.web.dev/analysis?url='+urllib.parse.quote(PUBLIC,safe='')+'&form_factor=mobile'})
if __name__=='__main__':main()
