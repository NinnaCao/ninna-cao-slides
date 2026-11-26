#!/usr/bin/env python3
"""Audit a generated HTML deck. Does not replace a visual or browser check."""
from html.parser import HTMLParser
from pathlib import Path
import argparse, collections, json, re, sys, math

class DeckParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slides=[]; self.ids=[]; self.current=None; self.skip=0; self.section_depth=0
        self.images=[]; self.external=[]; self.blocks={}; self.block=None
        self.css=[]; self.in_style=False
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if a.get('id'): self.ids.append(a['id'])
        if tag=='section':
            if self.current is not None:self.section_depth+=1
            elif 'slide' in a.get('class','').split():
                self.current={'id':a.get('id'),'title':a.get('data-title',''),'appendix':a.get('data-appendix')=='true','text':'','duration':a.get('data-duration-seconds')}
                self.slides.append(self.current);self.section_depth=1
        if tag in ['script','style']: self.skip+=1
        if tag=='style':self.in_style=True
        if a.get('style'):self.css.append(a['style'])
        if tag=='script' and a.get('id') in ['deck-manifest','deck-notes']:
            self.block=a['id'];self.blocks[self.block]=''
        if tag in ['img','image','video','audio','source','track','script','link','use','iframe','embed','object']:
            for key in ['src','href','xlink:href','poster','data']:
                if a.get(key) and not a[key].startswith(('data:','#')):
                    self.external.append({'tag':tag,'attribute':key,'value':a[key]})
        if tag=='img':self.images.append(a)
    def handle_endtag(self,tag):
        if tag=='section' and self.current is not None:
            self.section_depth-=1
            if self.section_depth==0:self.current=None
        if tag in ['script','style']:
            self.skip=max(0,self.skip-1)
            if tag=='script':self.block=None
            else:self.in_style=False
    def handle_data(self,data):
        if self.block:self.blocks[self.block]+=data
        if self.in_style:self.css.append(data)
        if self.current is not None and not self.skip:self.current['text']+=' '+data

def audit(path):
    source=Path(path).read_text(encoding='utf-8');p=DeckParser();p.feed(source)
    errors=[];warnings=[]
    if not p.slides:errors.append('No .slide sections found.')
    duplicates=[key for key,n in collections.Counter(p.ids).items() if n>1]
    if duplicates:errors.append('Duplicate ids: '+', '.join(duplicates))
    if 'width: 1920px' not in source or 'height: 1080px' not in source:errors.append('Missing fixed 1920 by 1080 stage base.')
    if '@media print' not in source or '@page' not in source:errors.append('Missing final-state print styling.')
    if 'prefers-reduced-motion' not in source:errors.append('Missing reduced-motion support.')
    if p.external:errors.append('Non-embedded resources found: '+str(p.external[:5]))
    css=re.sub(r'/\*.*?\*/','','\n'.join(p.css),flags=re.S)
    css_resources=[m[1].strip() for m in re.findall(r'url\(\s*([\x22\x27]?)(.*?)\1\s*\)',css,re.I|re.S) if not m[1].strip().startswith(('data:','#'))]
    if css_resources:errors.append('Non-embedded CSS resources found: '+str(css_resources[:5]))
    if re.search(r'@import\b',css,re.I):errors.append('CSS imports found. Inline project styles instead.')
    missing_alt=[i+1 for i,a in enumerate(p.images) if 'alt' not in a]
    if missing_alt:errors.append('Images without alt attributes: '+str(missing_alt))
    appendix=False
    for slide in p.slides:
        if not slide['title']:errors.append('Missing title on '+str(slide['id']))
        if appendix and not slide['appendix']:errors.append('A main slide follows the appendix.')
        appendix |= slide['appendix']
        try:
            if not math.isfinite(float(slide['duration'])) or float(slide['duration'])<=0:raise ValueError()
        except (ValueError,TypeError):errors.append('Invalid duration on '+str(slide['id']))
        words=len(re.findall(r"[A-Za-z]+(?:[’'-][A-Za-z]+)?|\d+",slide['text']))
        slide['words']=words
        if words>135:warnings.append(str(slide['id'])+' has '+str(words)+' visible English words; inspect density.')
        if re.search(r'\b(TODO|TBD|lorem ipsum)\b',slide['text'],re.I):errors.append('Unresolved audience-visible placeholder on '+str(slide['id']))
    notes=[]
    try:
        model=json.loads(p.blocks.get('deck-manifest','null'))
        notes=json.loads(p.blocks.get('deck-notes','null'))
        if not isinstance(model,dict) or not isinstance(notes,list):raise ValueError()
        if len(notes)!=len(p.slides):errors.append('Note count does not match the slide count.')
    except (ValueError,TypeError):errors.append('Invalid or absent manifest/notes JSON.')
    return {'status':'pass' if not errors else 'fail','errors':errors,'warnings':warnings,'main_slides':sum(not s['appendix'] for s in p.slides),'appendix_slides':sum(s['appendix'] for s in p.slides),'embedded_images':len(p.images),'notes':len(notes or []),'slides':[{k:s[k] for k in ['id','title','appendix','words']} for s in p.slides],'claim_boundary':'Static structure only. Visual layout, image quality, factual accuracy and browser interaction require separate review.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('html');parser.add_argument('--out')
    args=parser.parse_args();result=audit(args.html);text=json.dumps(result,ensure_ascii=False,indent=2)
    if args.out:Path(args.out).write_text(text,encoding='utf-8')
    print(text);sys.exit(0 if result['status']=='pass' else 1)

if __name__=='__main__':main()
