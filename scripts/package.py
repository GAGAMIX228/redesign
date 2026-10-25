"""Create a reviewable archive without Git metadata, caches or credentials."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
R=Path(__file__).resolve().parents[1];out=R.parent/'urfu-svoy-marshrut.zip'
with ZipFile(out,'w',compression=ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(R.rglob('*')):
  rel=p.relative_to(R)
  if not p.is_file() or any(part in ['.git','__pycache__','.playwright'] for part in rel.parts) or p.suffix=='.pyc':continue
  z.write(p,'urfu-svoy-marshrut/'+str(rel))
print(out,out.stat().st_size,'bytes')
