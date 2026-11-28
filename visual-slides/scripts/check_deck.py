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
                self.current={'id':a.get('id'),'title':a.get('data-title',''),'appendix':a.get('data-appendix')=='true','text':'','duration':a.get('data-duration-seconds'),'visuals':0,'images':0,'exempt':a.get('data-visual-exempt')}
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
        if self.current is not None and not self.skip:
            # A visual is a picture, video, canvas or a diagram-sized SVG (not an icon).
            if tag in ('img','video','canvas','picture'):self.current['visuals']+=1
            # A real image: a photo, render or screenshot (raster), not only a drawn diagram or SVG illustration.
            src=a.get('src','') or a.get('poster','') or ''
            if (tag=='img' and src and not re.match(r'data:image/svg|.*\.svg($|\?)',src,re.I)) or tag=='video':self.current['images']+=1
            if re.search(r'background-image\s*:\s*url\(\s*[\x22\x27]?data:image/(?!svg)',a.get('style',''),re.I):self.current['images']+=1
            elif tag=='svg':
                box=(a.get('viewbox') or a.get('viewBox') or '').split()
                wide=float(box[2]) if len(box)==4 else float(re.sub(r'[^0-9.]','',a.get('width','0')) or 0)
                if wide>=200 or a.get('role')=='img' or 'stage-svg' in a.get('class',''):self.current['visuals']+=1
            elif 'background-image' in a.get('style','') and 'url(' in a.get('style',''):self.current['visuals']+=1
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

MEDIA=Path(__file__).resolve().parents[1]/'assets'/'media'

def sameness(model,source):
    """Warn when a deck looks like every other deck: the stock example look or example photos."""
    out=[];style=model.get('style') or {}
    if style.get('preset')=='cinematic' and str(style.get('accent','#ff7338')).lower()=='#ff7338':
        out.append('Stock Cinematic Night (default orange, Barlow Condensed). Use it only when the user chose it; otherwise derive the look from this topic: scripts/make_theme.py --mood <mood> --images <topic images>, then style {"preset":"adaptive","theme":"theme/theme.json"}.')
    reused=[]
    for f in sorted(MEDIA.rglob('*')):
        if f.suffix.lower() in ('.webp','.jpg','.jpeg','.png') and f.is_file():
            import base64
            if base64.b64encode(f.read_bytes()).decode('ascii')[:4000] in source:reused.append(f.name)
    if reused:out.append('Bundled example photos reused: '+', '.join(reused)+'. Find images for this topic (find_images.py, the brand site or the user\'s files) instead.')
    return out

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
        cjk=len(re.findall(r'[\u3400-\u9fff\uf900-\ufaff]',slide['text']))
        slide['words']=words;slide['cjk_chars']=cjk
        generated=str(slide['exempt'] or '').startswith('Generated')
        if words>135 and not generated:warnings.append(str(slide['id'])+' has '+str(words)+' visible English words; inspect density.')
        if cjk>260:warnings.append(str(slide['id'])+' has '+str(cjk)+' visible Chinese characters; inspect density.')
        if not slide['visuals'] and not slide['exempt']:
            message=str(slide['id'])+' has no picture, diagram or video. Every slide needs a visual (or data-visual-exempt with a reason).'
            (warnings if slide['appendix'] else errors).append(message)
        elif not slide['images'] and not slide['exempt']:
            message=str(slide['id'])+' has no real image (photo, render or screenshot). Add one, or put one behind the content with backdrop place "ambient".'
            (warnings if slide['appendix'] else errors).append(message)
        if re.search(r'\b(TODO|TBD|lorem ipsum)\b',slide['text'],re.I):errors.append('Unresolved audience-visible placeholder on '+str(slide['id']))
    notes=[]
    try:
        model=json.loads(p.blocks.get('deck-manifest','null'))
        notes=json.loads(p.blocks.get('deck-notes','null'))
        if not isinstance(model,dict) or not isinstance(notes,list):raise ValueError()
        if len(notes)!=len(p.slides):errors.append('Note count does not match the slide count.')
        photos=len(re.findall(r'data:image/(?:webp|jpe?g|png|avif)',source))
        if photos and not (model.get('credits') or model.get('credits_slide') is False):
            warnings.append(str(photos)+' embedded raster images but no credits ledger in the manifest. Record creator, license and source for every image found online.')
        if not model.get('example'):warnings.extend(sameness(model,source))
    except (ValueError,TypeError):errors.append('Invalid or absent manifest/notes JSON.')
    return {'status':'pass' if not errors else 'fail','errors':errors,'warnings':warnings,'main_slides':sum(not s['appendix'] for s in p.slides),'appendix_slides':sum(s['appendix'] for s in p.slides),'embedded_images':len(p.images),'notes':len(notes or []),'slides':[{k:s[k] for k in ['id','title','appendix','words','cjk_chars','visuals','images']} for s in p.slides],'claim_boundary':'Static structure only. Visual layout, image quality, factual accuracy and browser interaction require separate review.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('html');parser.add_argument('--out')
    args=parser.parse_args();result=audit(args.html);text=json.dumps(result,ensure_ascii=False,indent=2)
    if args.out:Path(args.out).write_text(text,encoding='utf-8')
    print(text);sys.exit(0 if result['status']=='pass' else 1)

if __name__=='__main__':main()
