#!/usr/bin/env python3
"""Build seven review PDFs from Markdown, figures and complete appendices.

Install scripts/requirements-submission3.txt in an isolated environment.
Render PlantUML PNG/SVG first. No network resources are fetched by this build.
"""
import hashlib
import html
import json
import math
import re
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path

from markdown_it import MarkdownIt
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, LongTable, NextPageTemplate,
    PageBreak, PageTemplate, Paragraph, Spacer, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/report/submission_3'
TMP = ROOT / 'tmp/submission_3_build'
FONT_ROOT = Path('/usr/share/fonts/truetype/dejavu')
for name, filename in [('Body','DejaVuSans.ttf'),('Body-Bold','DejaVuSans-Bold.ttf'),('Body-Italic','DejaVuSans-Oblique.ttf'),('Body-BoldItalic','DejaVuSans-BoldOblique.ttf'),('Mono','DejaVuSansMono.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_ROOT / filename)))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='Body-Bold', italic='Body-Italic', boldItalic='Body-BoldItalic')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Text', fontName='Body', fontSize=9, leading=14, spaceAfter=7, wordWrap='CJK'))
styles.add(ParagraphStyle(name='Cell', parent=styles['Text'], fontSize=7.7, leading=11, spaceAfter=2))
styles.add(ParagraphStyle(name='CodeText', parent=styles['Text'], fontName='Mono', fontSize=7.5, leading=11, backColor=colors.HexColor('#f1f5f9'), borderPadding=5))
for level, size in [(1,18),(2,13),(3,10.5),(4,9.5)]:
    styles.add(ParagraphStyle(name=f'H{level}', fontName='Body-Bold', fontSize=size, leading=size+5, spaceBefore=12, spaceAfter=7, keepWithNext=True, wordWrap='CJK', textColor=colors.HexColor('#173653')))
styles.add(ParagraphStyle(name='Cover', fontName='Body-Bold', fontSize=24, leading=34, spaceAfter=18, alignment=TA_CENTER, textColor=colors.HexColor('#173653')))
styles.add(ParagraphStyle(name='Center', parent=styles['Text'], alignment=TA_CENTER, fontSize=12, leading=19))
MD = MarkdownIt('commonmark', {'html':True}).enable('table')
audit = []
SEEN_FIGURES = set()


def clean(text):
    # Strip unsupported decorative pictographs, retain Vietnamese and math.
    text = re.sub('[\U0001F000-\U0001FFFF\uFE0F\u200D\u2705\u274C\u26A0\u2611]', '', text)
    return text.replace('\u2011','-').replace('\u2013','-').replace('\u2014','-')


def inline(token):
    result = ''
    for child in token.children or []:
        if child.type == 'text': result += html.escape(clean(child.content))
        elif child.type == 'code_inline': result += '<font face="Mono" size="7.8">' + html.escape(clean(child.content)) + '</font>'
        elif child.type in ('softbreak','hardbreak'): result += '<br/>' if child.type=='hardbreak' else ' '
        elif child.type == 'strong_open': result += '<b>'
        elif child.type == 'strong_close': result += '</b>'
        elif child.type == 'em_open': result += '<i>'
        elif child.type == 'em_close': result += '</i>'
        elif child.type == 'html_inline':
            if re.match(r'<br\s*/?>',child.content):result+='<br/>'
            else:result+=html.escape(re.sub('<[^>]+>','',child.content))
        elif child.type == 'image': result += html.escape(child.content)
    return result or ' '


def page_footer(canvas, doc):
    width,height=canvas._pagesize
    canvas.setStrokeColor(colors.HexColor('#cbd5e1'))
    canvas.line(35,31,width-35,31)
    canvas.setFont('Body',7)
    canvas.setFillColor(colors.HexColor('#475569'))
    canvas.drawString(35,20,'Smart E-Mobility Hub | Submission 3 | Revision 06/11/2026 | Owner confirmation pending')
    canvas.drawRightString(width-35,20,str(doc.page))


def figure(src, caption, base, include_class_details=True):
    path=(base/src).resolve()
    if not path.is_file(): raise FileNotFoundError(path)
    if path in SEEN_FIGURES:
        return [Paragraph('Hình '+html.escape(clean(caption))+' đã trình bày ở phần trước; dùng cùng phiên bản nguồn.',styles['Text'])]
    SEEN_FIGURES.add(path)
    picture=PILImage.open(path).convert('RGB')
    w,h=picture.size
    portrait = w/h < 0.85
    result=[NextPageTemplate('Portrait' if portrait else 'Diagram'),PageBreak(),Paragraph(html.escape(clean(caption)),styles['H2'])]
    maxw,maxh=(A4[0]-80,A4[1]-120) if portrait else (landscape(A4)[0]-76,landscape(A4)[1]-110)
    scale=min(maxw/w,maxh/h)
    result.append(Image(str(path),w*scale,h*scale))
    # Show complete class boxes, never arbitrary tiles that cut a signature.
    # Relations remain on the full overview; prose/catalog supplies every detail.
    details=0
    svg=path.with_suffix('.svg')
    if include_class_details and scale<0.58 and path.name=='class_diagram.png' and svg.is_file():
        tree=ET.parse(svg)
        for group in tree.iter():
            if group.get('class')!='entity':continue
            rects=[r for r in group if r.tag.endswith('rect') and r.get('x') and r.get('width')]
            if not rects:continue
            box=max(rects,key=lambda r:float(r.get('width'))*float(r.get('height')))
            x,y,bw,bh=[float(box.get(k)) for k in ('x','y','width','height')]
            if bh<65:continue
            tile=picture.crop((max(0,int(x)-7),max(0,int(y)-7),min(w,math.ceil(x+bw)+7),min(h,math.ceil(y+bh)+7)))
            digest=hashlib.sha256(str(path).encode()).hexdigest()[:10]
            target=TMP/f'{digest}-entity-{details}.png';tile.save(target)
            tw,th=tile.size;zoom=min(maxw/tw,maxh/th,1.15)
            labels=[t.text or '' for t in group if t.tag.endswith('text')]
            title=group.get('data-entity') or next((t for t in labels if t and not t.startswith(('«','+','-','#'))),'class')
            result += [PageBreak(),Paragraph('Chi tiết lớp: '+html.escape(title),styles['H2']),Image(str(target),tw*zoom,th*zoom)]
            details+=1
    audit.append({'figure':str(path.relative_to(ROOT)),'pixels':[w,h],'overview_scale':round(scale,3),'complete_class_panels':details})
    result += [NextPageTemplate('Portrait'),PageBreak()]
    return result


def markdown(path, include_figures=True, include_class_details=True):
    source=path.read_text()
    source=re.sub(r'^<div class="cover">.*?</div>\s*','',source,flags=re.S)
    source=re.sub(r'<img\s+src="([^"]+)"[^>]*alt="([^"]*)"[^>]*>',r'![\2](\1)',source)
    source=re.sub(r'<img\s+src="([^"]+)"[^>]*>',r'![Sơ đồ](\1)',source)
    source=re.sub(r'</?div[^>]*>','',source)
    tokens=MD.parse(source)
    out=[];i=0;listlevel=0
    while i<len(tokens):
        token=tokens[i]
        if token.type=='heading_open':
            level=min(int(token.tag[1:]),4);out.append(Paragraph(inline(tokens[i+1]),styles[f'H{level}']));i+=3;continue
        if token.type=='paragraph_open':
            nexttoken=tokens[i+1]
            images=[x for x in nexttoken.children or [] if x.type=='image']
            if images and include_figures:
                for img in images:out+=figure(img.attrGet('src'),img.content,path.parent,include_class_details=include_class_details)
            elif not images:
                prefix=('• ' if listlevel else '')
                out.append(Paragraph(prefix+inline(nexttoken),styles['Text']))
            i+=3;continue
        if token.type in ('bullet_list_open','ordered_list_open'):listlevel+=1
        elif token.type in ('bullet_list_close','ordered_list_close'):listlevel-=1
        elif token.type=='table_open':
            cells=[];row=[];i+=1
            while tokens[i].type!='table_close':
                t=tokens[i]
                if t.type=='tr_open':row=[]
                elif t.type=='inline':row.append(Paragraph(inline(t),styles['Cell']))
                elif t.type=='tr_close':cells.append(row)
                i+=1
            width=A4[0]-80
            count=max(len(row) for row in cells)
            if count==2:weights=[0.27,0.73]
            else:weights=[1/count]*count
            table=LongTable(cells,colWidths=[width*v for v in weights],repeatRows=1,splitByRow=1,splitInRow=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e2e8f0')),('GRID',(0,0),(-1,-1),0.35,colors.HexColor('#cbd5e1')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
            out+=[table,Spacer(1,9)]
        elif token.type in ('fence','code_block'):
            code=clean(token.content)
            lines=[]
            for line in code.splitlines():lines+=textwrap.wrap(line,95,replace_whitespace=False,drop_whitespace=False) or ['']
            # Each line is independently splittable, even very long code blocks.
            for line in lines:out.append(Paragraph(html.escape(line).replace(' ','&#160;') or ' ',styles['CodeText']))
        elif token.type=='hr':out.append(Spacer(1,8))
        i+=1
    return out


def build():
    OUT.mkdir(exist_ok=True,parents=True);TMP.mkdir(exist_ok=True,parents=True)
    data=json.loads((ROOT/'docs/traceability/submission_3.json').read_text())
    for n,(slug,name,mssv) in data['members'].items():
        SEEN_FIGURES.clear()
        member=ROOT/f'docs/report/submission_3/TV{n}_{slug}'
        target=OUT/f'REPORT_SUB3_{slug}_{mssv}.pdf'
        doc=BaseDocTemplate(str(target),pagesize=A4,leftMargin=40,rightMargin=40,topMargin=40,bottomMargin=45,title=f'Submission 3 - SS{n} - {name}',author=f'BEE BRAVE - {name}; integration with Codex assistance')
        doc.addPageTemplates([
            PageTemplate(id='Portrait',pagesize=A4,frames=[Frame(40,45,A4[0]-80,A4[1]-85,id='body',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=page_footer),
            PageTemplate(id='Diagram',pagesize=landscape(A4),frames=[Frame(38,45,landscape(A4)[0]-76,landscape(A4)[1]-85,id='diagram',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=page_footer)])
        story=[Spacer(1,100),Paragraph('SUBMISSION 3',styles['Cover']),Paragraph('SMART E-MOBILITY HUB',styles['Cover']),Paragraph(f'SS{n} - {html.escape(name)}',styles['Center']),Paragraph('MSSV: '+mssv,styles['Center']),Paragraph('CO3001 - HK261 | BEE BRAVE - Nhóm 7',styles['Center']),Spacer(1,45),Paragraph('Revision tích hợp: 06/11/2026',styles['Center']),Paragraph('Bản kỹ thuật để tác giả đọc và xác nhận trước nộp LMS',styles['Center']),PageBreak()]
        for filename in ['REPORT_SUB3.md','method_catalog.md','traceability.md','test_cases.md']:
            if filename!='REPORT_SUB3.md':story += [PageBreak(),Paragraph('PHỤ LỤC: '+filename,styles['H1'])]
            story+=markdown(member/filename,include_class_details=(slug!='NguyenThanhDat'))
        story += [PageBreak(),Paragraph('PHỤ LỤC KIẾN TRÚC HỆ THỐNG',styles['H1'])]
        story += markdown(ROOT/'docs/report/submission_3/shared/architecture.md',include_class_details=(slug!='NguyenThanhDat'))
        normalized=[]
        pending_break=False
        pending_template=None
        for item in story:
            if isinstance(item,NextPageTemplate):pending_template=item
            elif isinstance(item,PageBreak):pending_break=True
            else:
                if pending_template is not None:normalized.append(pending_template)
                if pending_break:normalized.append(PageBreak())
                pending_template=None;pending_break=False
                normalized.append(item)
        doc.build(normalized)
        print(target.relative_to(ROOT))
    (ROOT/'docs/audit/submission_3/review_20261106/pdf-figure-layout.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
    files=sorted(OUT.glob('REPORT_SUB3_*.pdf'))
    (OUT/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files))


if __name__=='__main__':build()
