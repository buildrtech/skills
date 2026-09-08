"""Independent paired-A check. Usage: python check-output.py WORKSPACE EVIDENCE_DIR.

Money/content checks are deterministic. Review PDF images and trace separately.
Expected data and this checker stay outside the agent workspace.
"""
import csv
from collections import Counter
from decimal import Decimal
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys

job=Path(sys.argv[1]).resolve(); evidence=Path(sys.argv[2]).resolve();evidence.mkdir(parents=True,exist_ok=True)
class Text(HTMLParser):
 def __init__(self): super().__init__();self.skip=0;self.parts=[]
 def handle_starttag(self,t,a):
  if t in ('head','style','script'):self.skip+=1
 def handle_endtag(self,t):
  if t in ('head','style','script') and self.skip:self.skip-=1
 def handle_data(self,d):
  if not self.skip:self.parts.append(d)

html=(job/'output/budget-export.html').read_text();parser=Text();parser.feed(html);visible=' '.join(parser.parts)
pattern=re.compile(r'(-?)\$\s*([\d,]+\.\d{2})')
def amounts(text):return Counter(Decimal(sign+number.replace(',','')) for sign,number in pattern.findall(text))
with (job/'input/budget.csv').open() as f: expected=Counter(Decimal(r['Amount']) for r in csv.DictReader(f))
notes='\n'.join(p.read_text() for p in (job/'output').glob('*.md'))
checks={'all_exported_money_html':not (expected-amounts(visible)), 'project':'Juniper & Ash Community Workshop' in visible, 'gap_reported':all(s in visible+notes for s in ['6,799.43','6,800.43','1.00']), 'no_sample_text':not any(s in visible.lower() for s in ['riverside','cedar hollow','owner name','contractor name']), 'all_required_notes':all(s in visible.lower() for s in ['2026-09-01','benches','loose equipment','alternates']), 'pdf_exists':(job/'output/budget-export.pdf').is_file()}
if checks['pdf_exists']:
 subprocess.run(['pdftotext','-layout',str(job/'output/budget-export.pdf'),str(evidence/'pdf-text.txt')],check=True)
 text=(evidence/'pdf-text.txt').read_text();checks['all_exported_money_pdf']=not(expected-amounts(text))
 subprocess.run(['pdftoppm','-scale-to','1200','-png',str(job/'output/budget-export.pdf'),str(evidence/'page')],check=True)
 info=subprocess.check_output(['pdfinfo',str(job/'output/budget-export.pdf')],text=True);(evidence/'pdfinfo.txt').write_text(info)
 checks['letter_pdf']='612 x 792 pts (letter)' in info
script='''<script>
const proof=document.createElement('pre');proof.id='independent-proof';
proof.textContent=JSON.stringify({color:getComputedStyle(document.querySelector('h1')).color,font:getComputedStyle(document.querySelector('h1')).fontFamily,overflow:document.documentElement.scrollWidth>innerWidth});document.body.append(proof);
</script>'''
# Preserve relative assets by using an absolute file base; never rewrite agent output.
probe=html.replace('<head>','<head><base href="'+(job/'output').as_uri()+'/">',1).replace('</body>',script+'</body>')
(evidence/'probe.html').write_text(probe)
with (evidence/'chrome.log').open('w') as err:
 dom=subprocess.check_output(['google-chrome','--headless','--disable-gpu','--disable-background-networking','--user-data-dir=/tmp/precon-check-chrome','--dump-dom','--window-size=1000,1400',(evidence/'probe.html').as_uri()],stderr=err,text=True)
m=re.search(r'<pre id="independent-proof">(.*?)</pre>',dom);browser=json.loads(m.group(1));checks['warm_heading']=browser['color']=='rgb(63, 46, 36)';checks['no_horizontal_overflow']=not browser['overflow']
result={'checks':checks,'browser':browser,'passed':all(checks.values()),'manual_checks_required':['all PDF pages legible with no overlap/clipping','alternates excluded and deduct identified','trace confirms actual render and inspection; script usage separate from outcome']}
(evidence/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
