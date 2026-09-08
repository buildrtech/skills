"""Generate truthful Markdown companions from shipped JSON and rendered HTML."""
from html.parser import HTMLParser
from pathlib import Path

samples = Path(__file__).resolve().parents[3] / 'skills/precon-pdf-templates/samples'
class Preview(HTMLParser):
    def __init__(self):
        super().__init__(); self.lines=[]; self.capture=None; self.parts=[]; self.row=[]; self.rows=[]; self.span=1
    def handle_starttag(self, tag, attrs):
        if tag == 'table': self.rows=[]
        if tag == 'tr': self.row=[]
        if tag in ('h1','h2','p','li','th','td'):
            self.capture=tag; self.parts=[]; self.span=int(dict(attrs).get('colspan','1'))
    def handle_data(self, data):
        if self.capture: self.parts.append(data)
    def handle_endtag(self, tag):
        if self.capture == tag:
            text=' '.join(''.join(self.parts).split()).replace('|',r'\|')
            if tag in ('th','td'): self.row += [text]+['']*(self.span-1)
            elif text: self.lines.append(({'h1':'# ','h2':'## ','li':'- '}.get(tag,'')+text)+'\n')
            self.capture=None
        if tag == 'tr': self.rows.append(self.row)
        if tag == 'table' and self.rows:
            width=max(map(len,self.rows)); rows=[r+['']*(width-len(r)) for r in self.rows]
            self.lines.append('| '+' | '.join(rows[0])+' |')
            self.lines.append('| '+' | '.join(['---']*width)+' |')
            self.lines.extend('| '+' | '.join(r)+' |' for r in rows[1:]);self.lines.append('')

raw=(samples/'input-budget-data.json').read_text()
(samples/'input-budget-data.md').write_text('# Sample input: construction budget export\n\nSynthetic Cedar Hollow library data, for this example budget.\nAll money fields are integer cents. This is an example, not a live estimate.\n\n[Source JSON](input-budget-data.json)\n\n```json\n'+raw+'```\n')
p=Preview();p.feed((samples/'output-budget-export.html').read_text())
heading = next(i for i, line in enumerate(p.lines) if line.startswith('# '))
(samples/'output-budget-export.md').write_text(
    p.lines[heading] + '\nIllustrative budget content; open the HTML for the document layout.\n\n'
    '[Rendered HTML](output-budget-export.html) · [Source data](input-budget-data.json)\n\n'
    + '\n'.join(p.lines[heading + 1:]))
