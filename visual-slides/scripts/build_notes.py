#!/usr/bin/env python3
"""Build a compact, color-indexed DOCX speaking sheet from a deck manifest."""
from pathlib import Path
import argparse, json, re

COLORS=['ECE7F6','E2EDF8','DFF1F1','E6F0DF','FFF0CC','FCE4D7','F8E1EB','E9E4F8','E3E9ED']

def build(manifest,output,speaker=None,include_appendix=False):
    try:
        from docx import Document
        from docx.shared import Inches,Pt,RGBColor
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
    except ImportError as exc:
        raise RuntimeError('This helper requires python-docx; use the available document tools or install that package in the active environment.') from exc
    model=json.loads(Path(manifest).read_text(encoding='utf-8'))
    rows=[(i,s) for i,s in enumerate(model['slides'],1) if (include_appendix or not s.get('appendix')) and (speaker is None or s.get('speaker',model.get('author','')).casefold()==speaker.casefold()) and (s.get('notes_en') or s.get('notes_zh'))]
    if not rows:raise ValueError('No speaking notes match that selection.')
    doc=Document();sec=doc.sections[0];sec.page_width=Inches(8.5);sec.page_height=Inches(11)
    sec.top_margin=sec.bottom_margin=Inches(.45);sec.left_margin=sec.right_margin=Inches(.52)
    for name in ['Normal','Title','Heading 1']:
        st=doc.styles[name];st.font.name='Liberation Sans';st.font.color.rgb=RGBColor(0,0,0)
        st._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'),'Noto Sans CJK SC')
        for border in list(st._element.xpath('.//w:pBdr')):border.getparent().remove(border)
    style=doc.styles['Normal'];style.font.size=Pt(11);style.paragraph_format.line_spacing=1.02;style.paragraph_format.space_after=Pt(3)
    p=doc.add_paragraph(model.get('title','Presentation')+' Speaking Notes','Title');p.paragraph_format.space_after=Pt(4)
    for r in p.runs:r.font.size=Pt(16);r.bold=True
    p=doc.add_paragraph((speaker or model.get('author',''))+'    Slides '+', '.join(str(i) for i,_ in rows));p.paragraph_format.space_after=Pt(6)
    for r in p.runs:r.font.size=Pt(9.5)
    missing=[];words=0
    for j,(number,s) in enumerate(rows):
        p=doc.add_paragraph(style='Heading 1');p.paragraph_format.space_before=Pt(3);p.paragraph_format.space_after=Pt(1);p.paragraph_format.keep_with_next=True
        shade=OxmlElement('w:shd');shade.set(qn('w:fill'),COLORS[j%len(COLORS)]);p._p.get_or_add_pPr().append(shade)
        r=p.add_run(f' {number}  '+s['title']);r.bold=True;r.font.size=Pt(10.5)
        cue=str(s.get('notes_zh','')).strip()
        if cue and len(cue)<45:
            r=p.add_run('    '+cue);r.font.size=Pt(9);r.font.color.rgb=RGBColor(64,64,64)
        en=str(s.get('notes_en',''));phrases=[str(x) for x in s.get('key_phrases',[]) if str(x)]
        words+=len(re.findall(r"[A-Za-z]+(?:[’'-][A-Za-z]+)?|\d+",en))
        missing.extend(f'{number}: {x}' for x in phrases if x not in en)
        p=doc.add_paragraph();p.paragraph_format.keep_together=True
        parts=re.split('('+'|'.join(re.escape(x) for x in sorted(set(phrases),key=len,reverse=True))+')',en) if phrases else [en]
        for part in parts:
            if not part:continue
            r=p.add_run(part)
            if part in phrases:
                r.bold=True;shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'FFF2B2');r._r.get_or_add_rPr().append(shade)
        if cue and len(cue)>=45:
            p=doc.add_paragraph(cue)
            for r in p.runs:r.font.size=Pt(10);r.font.color.rgb=RGBColor(64,64,64)
    doc.core_properties.title=model.get('title','Presentation')+' Speaking Notes';doc.core_properties.author=speaker or model.get('author','')
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True);doc.save(path)
    return {'file':str(path.resolve()),'slides':[i for i,_ in rows],'spoken_english_words':words,'unmatched_highlights':missing,'page_count':'Render and inspect the DOCX before claiming a one-page result.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest');p.add_argument('output');p.add_argument('--speaker');p.add_argument('--include-appendix',action='store_true');a=p.parse_args()
    try:print(json.dumps(build(a.manifest,a.output,a.speaker,a.include_appendix),ensure_ascii=False,indent=2))
    except (ValueError,OSError,RuntimeError) as exc:p.exit(1,str(exc)+'\n')

if __name__=='__main__':main()
