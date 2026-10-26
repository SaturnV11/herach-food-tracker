from pypdf import PdfReader
from pathlib import Path
import re,json,shutil,sys
root=Path(__file__).resolve().parent/'public'
source=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else root/'cardapio.pdf'
text='\n'.join(p.extract_text() for p in PdfReader(source).pages)
days=['SEGUNDA','TERÇA','QUARTA','QUINTA','SEXTA','SÁBADO','DOMINGO']
meals=['Café da manhã','Almoço','Lanche','Jantar']
foods={}; menu=[]
for d in days:
 section=text.split(d+'\n')[1]
 rows=[]
 for m in meals:
  match=re.search(re.escape(m)+r'\n(.*?)\n~(\d+) g',section,re.S)
  items=[]
  for s in match[1].split(';'):
   s=s.strip().replace('\n',' ')
   egg=re.fullmatch(r'(\d+) ovos',s)
   part=re.fullmatch(r'(.*?) (\d+) (g|ml)',s)
   if egg: name='Ovos'; qty=int(egg[1]); unit='un'
   elif part: name=part[1].capitalize(); qty=int(part[2]); unit=part[3]
   else: raise ValueError(s)
   fid=name.lower().replace(' ','-')
   foods[fid]={'id':fid,'name':name,'unit':unit,'base':100 if unit!='un' else 1,'nutrients':{'kcal':None,'protein':None,'carbs':None,'fat':None,'fiber':None},'source':'Cardápio Herach: nutrientes por alimento não informados','milk':name=='Leite','version':1}
   items.append({'id':str(len(items)),'foodId':fid,'quantity':qty})
  rows.append({'name':m,'estimatedCarbs':int(match[2]),'items':items})
 menu.append(rows)
(root/'seed.json').write_text(json.dumps({'foods':foods,'menu':menu,'source':'Herach_Cardapio_Semanal_Enxuto.pdf'},ensure_ascii=False),encoding='utf-8')
if source.resolve()!=(root/'cardapio.pdf').resolve():
 shutil.copyfile(source,root/'cardapio.pdf')
