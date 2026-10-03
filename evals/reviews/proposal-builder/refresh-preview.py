"""Regenerate the catalog preview from the actual rendered sample PDF. Requires Poppler."""
import base64
from pathlib import Path
import subprocess
import tempfile
ROOT = Path(__file__).resolve().parents[3]
SAMPLES = ROOT / 'skills/proposal-builder/samples'
with tempfile.TemporaryDirectory() as tmp:
    prefix = Path(tmp) / 'page'
    subprocess.run(['pdftoppm', '-scale-to', '700', '-jpeg', '-jpegopt', 'quality=60', str(SAMPLES / 'output-proposal.pdf'), str(prefix)], check=True)
    html = '<!doctype html><html lang="en"><meta charset="utf-8"><title>Cedar Hollow proposal — rendered PDF sample</title><style>body{margin:0;background:#e8ebe8;padding:16px}img{display:block;max-width:100%;width:696px;margin:0 auto 20px;box-shadow:0 2px 12px #0002}</style><body>'
    for i, path in enumerate(sorted(Path(tmp).glob('page-*.jpg'))):
        data = base64.b64encode(path.read_bytes()).decode()
        html += f'<img alt="Rendered proposal PDF page {i+1}" src="data:image/jpeg;base64,{data}">'
    (SAMPLES / 'output-proposal.html').write_text(html + '</body></html>')
