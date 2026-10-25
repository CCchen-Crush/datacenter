#!/usr/bin/env python3
"""Word files for the Applied Energy manuscript, built from paper/manuscript.md with pandoc (>= 3).

Usage: python3 tools/build_word.py                          (writes paper/word/)
  manuscript.docx              two-column layout of a typeset journal article, without line numbers: title, authors,
                               highlights and an article-information / abstract block across the page, then two
                               columns with the nomenclature, the text with native Word equations (left-aligned,
                               numbers at the right edge of the column), tables, figures, declarations and references.
                               Figures and tables wider than a column span both columns in a one-column section where
                               they are cited (WORD_LAYOUT=floats: anchored text boxes at the top of a page instead);
                               A4, Cambria 9.5 pt
  highlights.docx              the highlights as a separate file
  supplementary_material.docx  Figs. S1-S7 with their captions (one column)
  graphical_abstract.*         copied from paper/figures (python3 tools/plot_paper.py GA)
Author details and declarations are placeholders shaded in yellow. Figures are taken from paper/figures.
"""
import glob, math, os, re, shutil, subprocess, tempfile, zipfile
from PIL import Image, ImageFont

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MD, FIG, OUT = (os.path.join(ROOT, "paper", p) for p in ("manuscript.md", "figures", "word"))
FIGREF = re.compile(r"(Figs?\.\s*)((?:S?\d+)(?:[a-f](?:–[a-f])?)?(?:(?:,\s*|\s+and\s+)(?:S?\d+(?:[a-f](?:–[a-f])?)?|[a-f](?:–[a-f])?)(?!\w))*)")
SHORT_TITLE = "Recovery-aware scheduling for consecutive demand response of AI data centers"
N_FIG, N_SUPP, N_REF = 16, 7, 52
LAYOUT = os.environ.get("WORD_LAYOUT", "sections")      # "sections": one-column sections where cited; "floats": text boxes at the top of a page

# ------------------------------------------------------------------ page geometry (twentieths of a point)
PAGE_W, PAGE_H, MARG_LR, MARG_TB, GAP = 11906, 16838, 850, 1077, 369
TEXT_W = PAGE_W - 2 * MARG_LR                     # 18.0 cm
COL_W = (TEXT_W - GAP) // 2                       # 8.67 cm
SINGLE_W = PAGE_W - 2 * 1418                      # supplementary material: one column, 2.5 cm margins
EMU = 635                                         # EMU per twip

# ------------------------------------------------------------------ reference document: styles, page
FONT = '<w:rFonts w:ascii="Cambria" w:hAnsi="Cambria" w:eastAsia="Cambria" w:cs="Cambria"/>'
SZ = lambda pt: f'<w:sz w:val="{int(round(2 * pt))}"/><w:szCs w:val="{int(round(2 * pt))}"/>'
BORDER = lambda side, sz, color="000000": f'<w:{side} w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
GRAY = "7F7F7F"


def spacing(before=0, after=0, line=240, rule="auto"):
    return f'<w:spacing w:before="{before}" w:after="{after}" w:line="{line}" w:lineRule="{rule}"/>'


def style(sid, name, kind="paragraph", based="Normal", nxt=None, ppr="", rpr="", custom=True, extra=""):
    return (f'<w:style w:type="{kind}"' + (' w:customStyle="1"' if custom else "") + f' w:styleId="{sid}"><w:name w:val="{name}"/>'
            + (f'<w:basedOn w:val="{based}"/>' if based else "") + (f'<w:next w:val="{nxt}"/>' if nxt else "") + "<w:qFormat/>"
            + (f"<w:pPr>{ppr}</w:pPr>" if ppr else "") + (f"<w:rPr>{rpr}</w:rPr>" if rpr else "") + extra + "</w:style>")


def styles(col_w):
    eq_tabs = f'<w:tabs><w:tab w:val="left" w:pos="284"/><w:tab w:val="right" w:pos="{col_w}"/></w:tabs>'
    return [
        style("BodyText", "Body Text", custom=False, ppr=spacing() + '<w:ind w:firstLine="227"/><w:jc w:val="both"/>'),
        style("FirstParagraph", "First Paragraph", based="BodyText", nxt="BodyText", ppr='<w:ind w:firstLine="0"/>'),
        style("Compact", "Compact", based="BodyText", ppr='<w:ind w:firstLine="0"/><w:jc w:val="left"/>'),
        style("Title", "Title", custom=False, nxt="BodyText", ppr="<w:keepNext/>" + spacing(120, 200, 252) + '<w:jc w:val="left"/>', rpr=SZ(16)),
        style("Subtitle", "Subtitle", custom=False, nxt="BodyText", ppr=spacing(0, 240, 240) + '<w:jc w:val="left"/>', rpr="<w:i/><w:iCs/>" + SZ(11)),
        style("Author", "Author", nxt="BodyText", ppr=spacing(0, 60, 240) + '<w:jc w:val="left"/>', rpr=SZ(11)),
        style("Affiliation", "Affiliation", nxt="BodyText", ppr=spacing(0, 40, 240) + '<w:jc w:val="left"/>', rpr=SZ(7.5)),
        style("FrontHead", "Front Head", nxt="BodyText", ppr="<w:keepNext/>" + spacing(160, 60, 240),
              rpr='<w:caps/><w:spacing w:val="30"/>' + SZ(7.5)),
        style("FrontText", "Front Text", based="BodyText", ppr='<w:ind w:firstLine="0"/>' + spacing(0, 0, 240), rpr=SZ(8.5)),
        style("HighlightItem", "Highlight Item", based="BodyText", ppr='<w:ind w:left="170" w:hanging="170" w:firstLine="0"/><w:jc w:val="left"/>', rpr=SZ(8)),
        style("Rule", "Rule", ppr=spacing(40, 40, 240) + '<w:pBdr>' + BORDER("bottom", 4, GRAY) + "</w:pBdr>", rpr=SZ(4)),
        style("Heading1", "Heading 1", custom=False, nxt="FirstParagraph", ppr="<w:keepNext/><w:keepLines/>" + spacing(240, 100, 240) + '<w:outlineLvl w:val="0"/>',
              rpr="<w:b/><w:bCs/>" + SZ(9.5)),
        style("Heading2", "Heading 2", custom=False, nxt="FirstParagraph", ppr="<w:keepNext/><w:keepLines/>" + spacing(180, 80, 240) + '<w:outlineLvl w:val="1"/>',
              rpr="<w:i/><w:iCs/>" + SZ(9.5)),
        style("Heading3", "Heading 3", custom=False, nxt="FirstParagraph", ppr="<w:keepNext/><w:keepLines/>" + spacing(140, 60, 240) + '<w:outlineLvl w:val="2"/>',
              rpr="<w:i/><w:iCs/>" + SZ(9.5)),
        style("Bibliography", "Bibliography", custom=False, nxt="Bibliography", ppr=spacing(0, 20, 240) + '<w:ind w:left="397" w:hanging="397"/><w:jc w:val="left"/>',
              rpr=SZ(7.5)),
        style("Caption", "Caption", custom=False, ppr=spacing(0, 0, 240) + '<w:jc w:val="both"/>', rpr=SZ(7.5)),
        style("TableCaption", "Table Caption", based="Caption", ppr="<w:keepNext/>" + spacing(120, 60, 240) + '<w:jc w:val="left"/>'),
        style("FigureCaption", "Figure Caption", based="Caption", ppr=spacing(60, 0, 240)),
        style("FigureCaptionCentered", "Figure Caption Centered", based="FigureCaption", ppr='<w:jc w:val="center"/>'),
        style("ImageCaption", "Image Caption", based="FigureCaption"),
        style("Figure", "Figure", ppr="<w:keepNext/>" + spacing(0, 0, 240) + '<w:jc w:val="center"/>'),
        style("CaptionedFigure", "Captioned Figure", based="Figure"),
        style("Equation", "Equation", ppr='<w:keepLines/>' + eq_tabs + spacing(80, 80, 240)),
        style("TableText", "Table Text", ppr=spacing(10, 10, 240) + '<w:jc w:val="left"/>', rpr=SZ(7.5)),
        style("TableNote", "Table Note", based="BodyText", ppr='<w:ind w:firstLine="0"/>' + spacing(40, 0, 240), rpr=SZ(7)),
        style("NomHead", "Nomenclature Head", based="BodyText", nxt="BodyText", ppr="<w:keepNext/>" + '<w:ind w:firstLine="0"/>' + spacing(100, 20, 240),
              rpr="<w:i/><w:iCs/>" + SZ(8.5)),
        style("FootnoteText", "Footnote Text", custom=False, ppr=spacing(0, 0, 240), rpr=SZ(7.5)),
        style("Placeholder", "Placeholder", kind="character", based="DefaultParagraphFont", rpr='<w:shd w:val="clear" w:color="auto" w:fill="FFFF00"/>'),
        style("Hyperlink", "Hyperlink", kind="character", custom=False, based="DefaultParagraphFont", rpr='<w:color w:val="1F6FB4"/>'),
        ('<w:style w:type="table" w:default="1" w:styleId="Table"><w:name w:val="Table"/><w:basedOn w:val="TableNormal"/><w:qFormat/>'
         '<w:tblPr><w:tblInd w:w="0" w:type="dxa"/><w:tblBorders>' + BORDER("top", 6) + BORDER("bottom", 6) + "</w:tblBorders>"
         '<w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="57" w:type="dxa"/><w:bottom w:w="0" w:type="dxa"/>'
         '<w:right w:w="57" w:type="dxa"/></w:tblCellMar></w:tblPr>'
         '<w:tblStylePr w:type="firstRow"><w:tcPr><w:tcBorders>' + BORDER("bottom", 4) + "</w:tcBorders></w:tcPr></w:tblStylePr></w:style>"),
    ]


DOCDEFAULTS = ("<w:docDefaults><w:rPrDefault><w:rPr>" + FONT + SZ(9.5) + '<w:lang w:val="en-GB" w:eastAsia="zh-CN" w:bidi="ar-SA"/>'
               "</w:rPr></w:rPrDefault><w:pPrDefault><w:pPr>" + spacing() + "</w:pPr></w:pPrDefault></w:docDefaults>")


def sectpr(cols, marg_lr, kind="continuous", hdr=True, title_pg=False):
    refs = ('<w:headerReference w:type="default" r:id="rIdPageHeader"/><w:footerReference w:type="default" r:id="rIdPageFooter"/>'
            '<w:footerReference w:type="first" r:id="rIdPageFooter"/>' if hdr else '<w:footerReference w:type="default" r:id="rIdPageFooter"/>')
    return (f'<w:sectPr>{refs}<w:type w:val="{kind}"/><w:pgSz w:w="{PAGE_W}" w:h="{PAGE_H}"/>'
            f'<w:pgMar w:top="{MARG_TB}" w:right="{marg_lr}" w:bottom="{MARG_TB}" w:left="{marg_lr}" w:header="567" w:footer="510" w:gutter="0"/>'
            + (f'<w:cols w:num="2" w:space="{GAP}"/>' if cols == 2 else '<w:cols w:space="708"/>') + ("<w:titlePg/>" if title_pg else "") + "</w:sectPr>")


FIRST_SECTION = sectpr(1, MARG_LR, kind="nextPage", title_pg=True)          # title block across the page (ends with a paragraph-level sectPr)
PART = lambda body: ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + body)
NS_W = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')
FOOTER = PART(f'<w:ftr {NS_W}><w:p><w:pPr>' + spacing(0, 0, 240) + '<w:jc w:val="center"/><w:rPr>' + SZ(8) + '</w:rPr></w:pPr>'
              '<w:r><w:rPr>' + SZ(8) + '</w:rPr><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:rPr>' + SZ(8) + '</w:rPr><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
              '<w:r><w:rPr>' + SZ(8) + '</w:rPr><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:rPr>' + SZ(8) + '</w:rPr><w:t>1</w:t></w:r>'
              '<w:r><w:rPr>' + SZ(8) + '</w:rPr><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>')
HEADER = PART(f'<w:hdr {NS_W}><w:p><w:pPr>' + spacing(0, 0, 240) + '<w:jc w:val="left"/></w:pPr>'
              '<w:r><w:rPr><w:i/><w:iCs/>' + SZ(7.5) + f'</w:rPr><w:t>{SHORT_TITLE}</w:t></w:r></w:p></w:hdr>')


def reference_docx(path, journal=True):
    subprocess.run(["pandoc", "-o", path, "--print-default-data-file", "reference.docx"], check=True)
    with zipfile.ZipFile(path) as z: files = {n: z.read(n) for n in z.namelist()}
    st = files["word/styles.xml"].decode()
    st = re.sub(r"<w:docDefaults>.*?</w:docDefaults>", DOCDEFAULTS, st, count=1, flags=re.S)
    for new in styles(COL_W if journal else SINGLE_W):
        sid = re.search(r'w:styleId="([^"]+)"', new).group(1)
        pat = re.compile(r'<w:style [^>]*w:styleId="%s">.*?</w:style>' % re.escape(sid), re.S)
        st = pat.sub(lambda m: new, st, count=1) if pat.search(st) else st.replace("</w:styles>", new + "</w:styles>")
    files["word/styles.xml"] = st.encode()
    doc = files["word/document.xml"].decode(); assert "<w:sectPr />" in doc
    final = sectpr(2, MARG_LR) if journal else sectpr(1, 1418, kind="nextPage", hdr=False)
    files["word/document.xml"] = doc.replace("<w:sectPr />", final).encode()
    files["word/footer1.xml"] = FOOTER.encode(); files["word/header1.xml"] = HEADER.encode()
    rel = ('<Relationship Id="rIdPageFooter" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>'
           '<Relationship Id="rIdPageHeader" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>')
    files["word/_rels/document.xml.rels"] = files["word/_rels/document.xml.rels"].decode().replace("</Relationships>", rel + "</Relationships>").encode()
    ct = ('<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
          '<Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>')
    files["[Content_Types].xml"] = files["[Content_Types].xml"].decode().replace("</Types>", ct + "</Types>").encode()
    write_zip(path, files)


def write_zip(path, files):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for n, b in files.items(): z.writestr(n, b)


# ------------------------------------------------------------------ numbered equations (pandoc drops \tag)
LUA = r"""
-- display equation with \tag{n}: equation after the first tab (left-aligned), "(n)" at the right tab (paragraph style Equation)
local function blank(x) return x.t == 'Space' or x.t == 'SoftBreak' or x.t == 'LineBreak' end
local function tab() return pandoc.RawInline('openxml', '<w:r><w:tab/></w:r>') end
function Para(el)
  local out, cur, found = {}, pandoc.List(), false
  local function flush()
    while #cur > 0 and blank(cur[1]) do cur:remove(1) end
    while #cur > 0 and blank(cur[#cur]) do cur:remove(#cur) end
    if #cur > 0 then out[#out + 1] = pandoc.Para(cur) end
    cur = pandoc.List()
  end
  for _, x in ipairs(el.content) do
    if x.t == 'Math' and x.mathtype == 'DisplayMath' then
      found = true; flush()
      local tex, tag = x.text:match('^(.-)%s*\\tag{([^}]*)}%s*$')
      if tag then
        out[#out + 1] = pandoc.Div({pandoc.Para({tab(), pandoc.Math('InlineMath', tex), tab(), pandoc.Str('(' .. tag .. ')')})},
                                   pandoc.Attr('', {}, {['custom-style'] = 'Equation'}))
      else
        out[#out + 1] = pandoc.Para({x})
      end
    else
      cur:insert(x)
    end
  end
  if not found then return nil end
  flush()
  return out
end
"""

# ------------------------------------------------------------------ Markdown of the Word manuscript
PH = lambda text: "[" + text + ']{custom-style="Placeholder"}'
FLOAT_START, FLOAT_END = "FLOATSTARTMARK", "FLOATENDMARK"
DECLARATIONS = "\n\n".join([
    "## CRediT authorship contribution statement",
    PH("Contribution of each author in the CRediT roles, e.g. Conceptualization, Methodology, Software, Formal analysis, "
       "Writing – original draft, Writing – review & editing, Supervision, Funding acquisition."),
    "## Declaration of competing interest",
    PH("Competing interests of the authors. If there are none, Elsevier’s standard wording is: “The authors declare that they have no "
       "known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.”"),
    "## Declaration of generative AI and AI-assisted technologies in the writing process",
    PH("Required by Elsevier when generative AI was used in preparing the manuscript, e.g. “During the preparation of this work the "
       "author(s) used *name of tool or service* in order to *reason*. After using this tool or service, the author(s) reviewed and "
       "edited the content as needed and take(s) full responsibility for the content of the published article.”"),
    "## Acknowledgements", PH("Funding sources with grant numbers."),
    "## Data availability", PH("Where the code and data can be obtained, e.g. a public repository, or “Data will be made available on request.”"),
])


def div(name, text):
    return f'::: {{custom-style="{name}"}}\n{text}\n:::'


def raw(xml):
    return "```{=openxml}\n" + xml + "\n```"


def _cells(row):
    """Cells of a pipe-table row; a | inside $...$ belongs to the cell."""
    row = row.strip(); assert row.startswith("|") and row.endswith("|"), row
    cells, cur, math_ = [], "", False
    for ch in row[1:-1]:
        if ch == "$": math_ = not math_
        if ch == "|" and not math_: cells.append(cur); cur = ""
        else: cur += ch
    return cells + [cur]


def _visible(cell):
    """Approximate printed text of a Markdown cell: a LaTeX command prints as one character."""
    t = re.sub(r"\$([^$]*)\$", lambda m: re.sub(r"[{}^_]|\\[ ,;!]", "", re.sub(r"\\[A-Za-z]+", "x", m.group(1))), cell)
    return re.sub(r"\*\*|\\(?=\*)", "", t.replace("&emsp;", "  ")).strip()


def _font():
    """Cambria or its metric twin Caladea, to size the table columns; None if neither is installed."""
    for name in ("Caladea-Regular.ttf", "cambria.ttc", "Cambria.ttf", "LiberationSerif-Regular.ttf"):
        try: return ImageFont.truetype(name, 100)
        except OSError: pass


_F = _font()
text_pt = (lambda s: _F.getlength(s) * 0.075) if _F else (lambda s: 3.9 * len(s))      # printed width at 7.5 pt (points)


def column_widths(block, width_tw, pad=7.0):
    """Pipe table whose relative column widths (dashes of the separator) follow its content at 7.5 pt: every column holds
    its longest word and, if they are short, its cells on one line; the remaining width goes to the columns whose text
    would otherwise wrap most. Returns the table and the estimated number of printed lines."""
    text = width_tw / 20
    rows = block.split("\n"); assert re.fullmatch(r"\|[-|]+\|", rows[1]), rows[1]
    cells = [_cells(r) for k, r in enumerate(rows) if k != 1]
    need, want = [], []
    for j in range(len(cells[0])):
        col = [_visible(r[j]) for r in cells]; body = col[1:] or [""]
        n = max(text_pt(x) for c in col for x in c.split() or [""]) + pad
        line = max(text_pt(c) for c in body) + pad
        need.append(max(n, line) if line <= 0.2 * text else n); want.append(max(n, line))
    extra = text - sum(need); gap = [b - a for a, b in zip(need, want)]
    w = [a * text / sum(need) for a in need] if extra <= 0 or not sum(gap) else [a + extra * g / sum(gap) for a, g in zip(need, gap)]
    rows[1] = "|" + "|".join("-" * max(3, round(300 * x / sum(w))) for x in w) + "|"
    lines = sum(max(math.ceil((text_pt(_visible(c)) + pad) / max(x, 1)) for c, x in zip(r, w)) for r in cells)
    return "\n".join(rows), lines


def natural_width(block):
    """Width (twips) a pipe table needs at 7.5 pt: every body cell on one line and every header word unbroken."""
    rows = [_cells(r) for k, r in enumerate(block.split("\n")) if k != 1]
    col = lambda j: max([text_pt(_visible(r[j])) for r in rows[1:] or rows] + [text_pt(x) for x in _visible(rows[0][j]).split() or [""]])
    return 20 * sum(col(j) + 8 for j in range(len(rows[0])))


def fig_width_cm(label):
    f = glob.glob(os.path.join(FIG, f"Fig{label}_*.png")); assert len(f) == 1, (label, f)
    return Image.open(f[0]).size[0] / 300 * 2.54


def figure(label, caption, width_cm):
    f = glob.glob(os.path.join(FIG, f"Fig{label}_*.png")); assert len(f) == 1, (label, f)
    w = min(fig_width_cm(label), width_cm)
    cap = "Figure Caption Centered" if len(caption) < 150 else "Figure Caption"
    return div("Figure", f"![]({f[0]}){{width={w:.2f}cm}}") + "\n\n" + div(cap, f"**Fig. {label}.** {caption}")


def parse(src):
    """Title, named sections, figure captions and references of the Markdown manuscript."""
    first, rest = src.split("\n", 1); assert first.startswith("# ")
    rest = re.sub(r"\A\s*> Draft for[^\n]*\n", "", rest)                  # editorial note of the Markdown draft
    body, tail = rest.split("## Figure captions\n"); caps, refs = tail.split("## References\n")
    caps = dict(re.findall(r"^\*\*Fig\. (S?\d+)\.\*\* (.+)$", caps, re.M))
    refs = [l for l in refs.strip().split("\n") if l.strip()]
    assert len(caps) == N_FIG + N_SUPP and all(re.match(r"\[\d+\] ", l) for l in refs) and len(refs) == N_REF, (len(caps), len(refs))
    secs = re.split(r"^## ", body, flags=re.M)
    sections = [(s.split("\n", 1)[0].strip(), s.split("\n", 1)[1] if "\n" in s else "") for s in secs if s.strip()]
    return first[2:].strip(), sections, caps, refs


def front_md(title, sections):
    """Title block across the page: title, authors, highlights, article information and abstract."""
    sec = dict(sections)
    hl = re.findall(r"^- (.+)$", sec["Highlights"], re.M)
    abstract, kw = sec["Abstract"].strip().split("\n\n")
    kws = [k.strip() for k in re.sub(r"^\*\*Keywords:\*\*\s*", "", kw).split(";")]
    out = [div("Title", title), div("Author", PH("Author names") + "^a,\\*^"),
           div("Affiliation", "^a^ " + PH("Affiliation, city, postcode, country")),
           div("Affiliation", "^\\*^ Corresponding author. E-mail address: " + PH("e-mail")),
           div("Rule", "\u00a0"), div("Front Head", "Highlights")]
    out += [div("Highlight Item", "• " + h) for h in hl]
    out += [div("Rule", "\u00a0")]
    # article information (keywords) and abstract side by side: a two-column table without borders
    left = div("Front Head", "Article info") + "\n\n" + div("Front Text", "*Keywords:*") + "\n\n" + "\n\n".join(div("Front Text", k) for k in kws)
    right = div("Front Head", "Abstract") + "\n\n" + div("Front Text", abstract)
    out.append(f"FRONTTABLE\n\n{left}\n\nFRONTCELL\n\n{right}\n\nFRONTTABLEEND")
    out.append(raw(f"<w:p><w:pPr>{FIRST_SECTION}</w:pPr></w:p>"))
    return out


def manuscript_md(src):
    title, sections, caps, refs = parse(src)
    names = [n for n, _ in sections]
    out = ['---\nlang: en-GB\n---'] + front_md(title, sections)
    cited, figs_done, fig_order = {}, set(), []
    for name, text in sections:
        if name in ("Highlights", "Abstract"): continue
        if name.startswith("Appendix A."): out.append(DECLARATIONS)
        out.append(f"## {name}")
        bl = [b for b in text.strip("\n").split("\n\n") if b.strip()]
        k = 0
        while k < len(bl):
            b = bl[k]
            if name == "Nomenclature":
                if b.startswith("**") and b.endswith("**"): out.append(div("Nomenclature Head", b.strip("*"))); k += 1; continue
                if b.startswith("|"): out.append(column_widths(b, COL_W)[0]); k += 1; continue
            if b.startswith("**Table "):
                num, cap = re.match(r"\*\*Table (A?\d+)\.\*\*\s*(.*)", b, re.S).groups()
                tab = bl[k + 1]; notes = []
                if k + 2 < len(bl) and bl[k + 2].startswith("^a^"): notes = [bl[k + 2]]
                algo = tab.split("\n", 1)[0].lstrip("| ").startswith("**Algorithm")          # pseudocode table
                wide = natural_width(tab) > COL_W or algo or num == "A1"
                table, lines = column_widths(tab, TEXT_W if wide else COL_W)
                cap_md = div("Table Caption", f"**Table {num}**\\\n{cap}")
                body = [cap_md, table] + [div("Table Note", n) for n in notes]
                if wide: body = [FLOAT_START + f"T{lines}"] + body + [FLOAT_END]
                out += body; k += 2 + len(notes); continue
            out.append(b)
            if not b.startswith(("#", "|")):
                for m in FIGREF.finditer(b):
                    for n in re.findall(r"S?\d+", m.group(2)):
                        if not n.startswith("S") and n not in cited:
                            cited[n] = True
                            col_cm = COL_W / 20 * 2.54 / 72
                            if fig_width_cm(n) <= col_cm: out.append(figure(n, caps[n], col_cm))      # fits in a column
                            else: out += [FLOAT_START + "F", figure(n, caps[n], TEXT_W / 20 * 2.54 / 72), FLOAT_END]
            k += 1
    assert sorted(map(int, cited)) == list(range(1, N_FIG + 1)), sorted(cited)
    out += ["## References", div("Bibliography", "\n\n".join(refs))]
    return "\n\n".join(out) + "\n"


def supplementary_md(src):
    title, _, caps, _ = parse(src)
    out = [f'---\ntitle: "Supplementary material"\nsubtitle: "{title}"\nlang: en-GB\n---']
    out += [figure(f"S{k}", caps[f"S{k}"], SINGLE_W / 20 * 2.54 / 72) for k in range(1, N_SUPP + 1)]
    return "\n\n".join(out) + "\n"


def highlights_md(src):
    hl = re.search(r"^## Highlights\n\n((?:- .+\n)+)", src, re.M).group(1)
    assert all(len(l[2:]) <= 85 for l in hl.strip().split("\n")), "a highlight exceeds 85 characters"
    return '---\ntitle: "Highlights"\nlang: en-GB\n---\n\n' + hl


# ------------------------------------------------------------------ pandoc and post-processing
def fix_table(m, widths):
    """Three-line table (rules above and below the table and below the header; none for the headerless nomenclature),
    fixed column widths from the Markdown separator scaled to the target width, 7.5-pt single-spaced cell text."""
    t = m.group(0)
    if "FrontTable" in t: return t
    head = "<w:tblHeader" in t
    g = [int(x) for x in re.findall(r'<w:gridCol w:w="(\d+)"', t)]
    W = next(widths)
    g = [1020, W - 1020] if not head and len(g) == 2 else [round(x * W / sum(g)) for x in g]     # nomenclature: 1.8 cm symbols
    g[-1] += W - sum(g)
    t = re.sub(r"<w:tblGrid>.*?</w:tblGrid>", "<w:tblGrid>" + "".join(f'<w:gridCol w:w="{x}"/>' for x in g) + "</w:tblGrid>", t, count=1, flags=re.S)
    t = re.sub(r'<w:tblW [^>]*/>', f'<w:tblW w:w="{W}" w:type="dxa"/>', t, count=1)
    nil = "".join(f'<w:{s} w:val="nil"/>' for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
    pr = "<w:tblBorders>" + (BORDER("top", 6) + BORDER("bottom", 6) if head else nil) + '</w:tblBorders><w:tblLayout w:type="fixed"/>'
    t = re.sub(r"<w:tblBorders>.*?</w:tblBorders>|<w:tblLayout [^>]*/>", "", t, flags=re.S)
    t = re.sub(r"(<w:tblPr>.*?)(<w:tblCellMar|<w:tblLook|</w:tblPr>)", lambda k: k.group(1) + pr + k.group(2), t, count=1, flags=re.S)
    for k, r0 in enumerate(re.findall(r"<w:tr>.*?</w:tr>", t, re.S)):
        r1 = re.sub(r"<w:tc>(?!<w:tcPr)", "<w:tc><w:tcPr></w:tcPr>", re.sub(r"<w:tcPr\s*/>", "<w:tcPr></w:tcPr>", r0))
        if head and k == 0:                                              # rule below the header row
            r1 = re.sub(r"<w:tcPr>(.*?)</w:tcPr>", lambda q: "<w:tcPr>" + _tc_bottom(q.group(1)) + "</w:tcPr>", r1, flags=re.S)
        cols = iter(g)
        r1 = re.sub(r"<w:tcPr>", lambda q: f'<w:tcPr><w:tcW w:w="{next(cols)}" w:type="dxa"/>', r1)
        t = t.replace(r0, r1, 1)
    return t.replace('<w:pStyle w:val="Compact" />', '<w:pStyle w:val="TableText" />').replace('<w:pStyle w:val="Compact"/>', '<w:pStyle w:val="TableText"/>')


def _tc_bottom(tcpr):
    tcpr = re.sub(r"<w:tcBorders>.*?</w:tcBorders>", "", tcpr, flags=re.S)
    k = re.search(r"<w:(shd|noWrap|tcMar|textDirection|tcFitText|vAlign|hideMark)\b", tcpr)
    b = "<w:tcBorders>" + BORDER("bottom", 4) + "</w:tcBorders>"
    return tcpr[:k.start()] + b + tcpr[k.start():] if k else tcpr + b


MARK_P = lambda word: re.compile(r"<w:p>(?:(?!</w:p>).)*?" + word + r"(\w*)(?:(?!</w:p>).)*?</w:p>", re.S)
DRAW_NS = {"wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape", "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
           "wp14": "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing", "w14": "http://schemas.microsoft.com/office/word/2010/wordml"}


def floats(doc):
    """Content between the markers FLOAT_START<kind> and FLOAT_END -> an anchored text box across both columns at the top of
    the page (top-and-bottom wrapping, no overlap). Its height is estimated from the picture or the table lines; Word
    and LibreOffice grow it to fit (auto-fit)."""
    root = re.search(r"<w:document[^>]*>", doc).group(0)
    add = "".join(f' xmlns:{k}="{v}"' for k, v in DRAW_NS.items() if f"xmlns:{k}=" not in root)
    if "mc:Ignorable" not in root: add += ' mc:Ignorable="w14 wp14"'
    doc = doc.replace(root, root[:-1] + add + ">")
    n = [0]
    def box(m):
        kind, inner = m.group(1), m.group(2)
        n[0] += 1
        if kind.startswith("F"):
            cy = sum(int(x) for x in re.findall(r'<wp:extent cx="\d+" cy="(\d+)"', inner))
            words = len(re.sub(r"<[^>]+>", "", inner)); h_pt = cy / 12700 + 14 + 9.2 * math.ceil(words * 3.75 / (TEXT_W / 20))
        else:
            h_pt = 9.6 * int(kind[1:]) + 34
        h = int(h_pt * 12700 * 1.04)
        if inner.rstrip().endswith("</w:tbl>"): inner += '<w:p><w:pPr><w:spacing w:before="0" w:after="0"/></w:pPr></w:p>'
        return (f'<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/></w:pPr><w:r><mc:AlternateContent><mc:Choice Requires="wps"><w:drawing>'
                f'<wp:anchor distT="0" distB="200000" distL="0" distR="0" simplePos="0" relativeHeight="{251659264 + n[0]}" behindDoc="0" locked="0" layoutInCell="1" allowOverlap="0">'
                '<wp:simplePos x="0" y="0"/><wp:positionH relativeFrom="margin"><wp:align>center</wp:align></wp:positionH>'
                '<wp:positionV relativeFrom="margin"><wp:align>top</wp:align></wp:positionV>'
                f'<wp:extent cx="{TEXT_W * EMU}" cy="{h}"/><wp:effectExtent l="0" t="0" r="0" b="0"/><wp:wrapTopAndBottom/>'
                f'<wp:docPr id="{5000 + n[0]}" name="Float {n[0]}"/><wp:cNvGraphicFramePr/>'
                '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">'
                '<wps:wsp><wps:cNvSpPr txBox="1"/><wps:spPr><a:xfrm><a:off x="0" y="0"/>'
                f'<a:ext cx="{TEXT_W * EMU}" cy="{h}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></wps:spPr>'
                f'<wps:txbx><w:txbxContent>{inner}</w:txbxContent></wps:txbx>'
                '<wps:bodyPr rot="0" vert="horz" wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" anchor="t" anchorCtr="0"><a:spAutoFit/></wps:bodyPr></wps:wsp>'
                '</a:graphicData></a:graphic></wp:anchor></w:drawing></mc:Choice><mc:Fallback/></mc:AlternateContent></w:r></w:p>')
    pat = re.compile(r"<w:p>(?:(?!</w:p>).)*?" + FLOAT_START + r"(\w+)(?:(?!</w:p>).)*?</w:p>(.*?)<w:p>(?:(?!</w:p>).)*?" + FLOAT_END + r"(?:(?!</w:p>).)*?</w:p>", re.S)
    doc, k = pat.subn(box, doc)
    assert FLOAT_START not in doc and FLOAT_END not in doc
    return doc, k


def sections(doc):
    """Content between FLOAT_START<kind> and FLOAT_END -> its own one-column section (continuous section breaks before and
    after), so that it spans both columns at the place where it is cited."""
    two, one = sectpr(2, MARG_LR), sectpr(1, MARG_LR)
    brk = lambda sp: f'<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/>{sp}</w:pPr></w:p>'
    pat = re.compile(r"<w:p>(?:(?!</w:p>).)*?" + FLOAT_START + r"(\w+)(?:(?!</w:p>).)*?</w:p>(.*?)<w:p>(?:(?!</w:p>).)*?" + FLOAT_END + r"(?:(?!</w:p>).)*?</w:p>", re.S)
    doc, k = pat.subn(lambda m: brk(two) + m.group(2) + brk(one), doc)
    assert FLOAT_START not in doc and FLOAT_END not in doc
    return doc, k


def front_table(doc):
    """Paragraphs between FRONTTABLE, FRONTCELL and FRONTTABLEEND -> a borderless two-column table (article info | abstract)."""
    pat = re.compile(r"<w:p>(?:(?!</w:p>).)*?FRONTTABLE(?!END)(?:(?!</w:p>).)*?</w:p>(.*?)<w:p>(?:(?!</w:p>).)*?FRONTCELL(?:(?!</w:p>).)*?</w:p>(.*?)"
                     r"<w:p>(?:(?!</w:p>).)*?FRONTTABLEEND(?:(?!</w:p>).)*?</w:p>", re.S)
    w1 = int(TEXT_W * 0.27); w2 = TEXT_W - w1 - 284
    def tab(m):
        left, right = m.group(1), m.group(2)
        cell = lambda w, body, extra="": (f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{extra}</w:tcPr>{body}</w:tc>')
        return ('<w:tbl><w:tblPr><w:tblStyle w:val="FrontTable"/><w:tblW w:w="' + str(TEXT_W) + '" w:type="dxa"/><w:tblLayout w:type="fixed"/>'
                '<w:tblBorders>' + "".join(f'<w:{s} w:val="nil"/>' for s in ("top", "left", "bottom", "right", "insideH", "insideV")) + '</w:tblBorders>'
                '<w:tblCellMar><w:left w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tblCellMar><w:tblLook w:val="0000"/></w:tblPr>'
                f'<w:tblGrid><w:gridCol w:w="{w1}"/><w:gridCol w:w="284"/><w:gridCol w:w="{w2}"/></w:tblGrid><w:tr>'
                + cell(w1, left) + cell(284, "<w:p/>") + cell(w2, right) + '</w:tr></w:tbl><w:p><w:pPr><w:spacing w:before="0" w:after="120"/></w:pPr></w:p>')
    doc, k = pat.subn(tab, doc); assert k == 1, "front table"
    return doc


SCHEMA_ORDER = {      # child order of the elements that pandoc 3.1 / texmath write out of schema order
    "w:settings": ["w:writeProtection", "w:view", "w:zoom", "w:embedTrueTypeFonts", "w:embedSystemFonts", "w:saveSubsetFonts", "w:proofState",
                   "w:attachedTemplate", "w:stylePaneFormatFilter", "w:trackRevisions", "w:doNotTrackMoves", "w:defaultTabStop",
                   "w:autoHyphenation", "w:evenAndOddHeaders", "w:drawingGridHorizontalSpacing", "w:drawingGridVerticalSpacing",
                   "w:displayHorizontalDrawingGridEvery", "w:displayVerticalDrawingGridEvery", "w:characterSpacingControl",
                   "w:savePreviewPicture", "w:updateFields", "w:hdrShapeDefaults", "w:footnotePr", "w:endnotePr", "w:compat", "w:docVars",
                   "w:rsids", "m:mathPr", "w:attachedSchema", "w:themeFontLang", "w:clrSchemeMapping", "w:doNotIncludeSubdocsInStats",
                   "w:shapeDefaults", "w:decimalSymbol", "w:listSeparator"],
    "m:rPr": ["m:lit", "m:nor", "m:scr", "m:sty", "m:brk", "m:aln"],
    "m:dPr": ["m:begChr", "m:sepChr", "m:endChr", "m:grow", "m:shp", "m:ctrlPr"],
    "m:mcPr": ["m:count", "m:mcJc"],
}
CHILD = re.compile(r"<([\w:]+)\b[^>]*?/>|<([\w:]+)\b[^>]*>.*?</\2>", re.S)


def reorder(xml, parent):
    order = SCHEMA_ORDER[parent]
    def fix(m):
        kids = [k.group(0) for k in CHILD.finditer(m.group(2))]
        flat = lambda x: re.sub(r">\s+<", "><", x.strip())
        assert flat("".join(kids)) == flat(m.group(2)), parent             # nothing but child elements
        rank = lambda k: order.index(re.match(r"<([\w:]+)", k).group(1)) if re.match(r"<([\w:]+)", k).group(1) in order else len(order)
        return m.group(1) + "".join(sorted(kids, key=rank)) + m.group(3)
    return re.sub(r"(<%s(?:\s[^>]*)?>)(.*?)(</%s>)" % (parent, parent), fix, xml, flags=re.S)


def sanitize(files):
    """Schema order and values that pandoc 3.1 gets wrong (Word tolerates them, validators do not)."""
    doc = files["word/document.xml"].decode()
    doc = re.sub(r"<w:pPr>(.*?)</w:pPr>", lambda m: "<w:pPr>" + _first(m.group(1), r"<w:pStyle [^>]*/>") + "</w:pPr>", doc, flags=re.S)
    doc = re.sub(r"<w:tblPr>(.*?)</w:tblPr>", lambda m: "<w:tblPr>" + _after_tblw(m.group(1)) + "</w:tblPr>", doc, flags=re.S)
    doc = literal_runs(doc)
    for parent in ("m:rPr", "m:dPr", "m:mcPr"): doc = reorder(doc, parent)
    files["word/document.xml"] = doc.encode()
    if "word/numbering.xml" in files:
        num = files["word/numbering.xml"].decode()
        files["word/numbering.xml"] = re.sub(r'(<w:nsid w:val=")([0-9A-F]{1,7})"', lambda m: m.group(1) + m.group(2).rjust(8, "0") + '"', num).encode()
    files["word/settings.xml"] = reorder(files["word/settings.xml"].decode(), "w:settings").encode()
    ct = files["[Content_Types].xml"].decode()
    if 'Extension="png"' not in ct:
        ct = ct.replace('<Default Extension="xml"', '<Default Extension="png" ContentType="image/png" /><Default Extension="xml"', 1)
    files["[Content_Types].xml"] = ct.encode()


LONE_OP = re.compile(r"(<m:(sup|sub)>)<m:r>(?:<m:rPr>((?:(?!</m:rPr>).)*?)</m:rPr>)?(<w:rPr>(?:(?!</w:rPr>).)*?</w:rPr>)?<m:t>([*+∗′−])</m:t></m:r>(</m:\2>)", re.S)
KEYWORD = re.compile(r"<m:r>(?:<m:rPr>((?:(?!</m:rPr>).)*?)</m:rPr>)?(<w:rPr>(?:(?!</w:rPr>).)*?</w:rPr>)?<m:t>(sup|inf)</m:t></m:r>", re.S)


def literal_runs(doc):
    """Literal (m:lit) runs for an operator alone in a script (c*, x+) and for the operator names sup and inf. Word draws
    them unchanged; importers that re-parse the run text as a formula language (LibreOffice) otherwise read an operator
    without operand or a keyword."""
    doc = LONE_OP.sub(lambda m: f"{m.group(1)}<m:r><m:rPr><m:lit />{m.group(3) or ''}</m:rPr>{m.group(4) or ''}<m:t>{m.group(5)}</m:t></m:r>{m.group(6)}", doc)
    return KEYWORD.sub(lambda m: f"<m:r><m:rPr><m:lit />{m.group(1) or ''}</m:rPr>{m.group(2) or ''}<m:t>{m.group(3)}</m:t></m:r>", doc)


MATH_PT = {"TableText": 7.5, "Compact": 7.5, "Caption": 7.5, "FigureCaption": 7.5, "FigureCaptionCentered": 7.5, "ImageCaption": 7.5,
           "TableCaption": 7.5, "Bibliography": 7.5, "TableNote": 7, "FrontText": 8.5, "HighlightItem": 8, "NomHead": 8.5}


def math_sizes(doc, default=9.5):
    """Explicit font (Cambria Math) and size of every math run, from the style of its paragraph: Word sizes an equation by
    the run properties, so equations follow the 7.5-pt table and caption text and the 9.5-pt body text."""
    def para(m):
        p = m.group(0)
        if "<m:r>" not in p: return p
        st = re.search(r'<w:pStyle w:val="([^"]+)"', p)
        rpr = '<w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/>' + SZ(MATH_PT.get(st.group(1) if st else "", default)) + "</w:rPr>"
        return re.sub(r"<m:r>(<m:rPr>(?:(?!</m:rPr>).)*?</m:rPr>)?(?!<w:rPr>)", lambda k: "<m:r>" + (k.group(1) or "") + rpr, p, flags=re.S)
    return re.sub(r"<w:p>(?:(?!</w:p>).)*?</w:p>|<w:p [^>]*>(?:(?!</w:p>).)*?</w:p>", para, doc, flags=re.S)


def _first(ppr, pat):
    m = re.search(pat, ppr)
    return m.group(0) + ppr[:m.start()] + ppr[m.end():] if m else ppr


def _after_tblw(tblpr):
    m = re.search(r"<w:jc [^>]*/>", tblpr); w = re.search(r"<w:tblW [^>]*/>", tblpr)
    if not (m and w) or m.start() < w.start(): return tblpr
    rest = tblpr[:m.start()] + tblpr[m.end():]; k = rest.index(w.group(0)) + len(w.group(0))
    return rest[:k] + m.group(0) + rest[k:]


def table_widths(md_text):
    """Target width of every pipe table in document order: the text width inside a float, else the column width."""
    out, in_float = [], False
    for b in md_text.split("\n\n"):
        if b.startswith(FLOAT_START): in_float = True
        elif b.startswith(FLOAT_END): in_float = False
        elif b.startswith("|"): out.append(TEXT_W if in_float else COL_W)
    return out


def pandoc(md_text, out, ref, lua, work, journal=True):
    src = os.path.join(work, os.path.basename(out) + ".md")
    open(src, "w").write(md_text)
    subprocess.run(["pandoc", src, "-f", "markdown", "-o", out, f"--reference-doc={ref}", f"--lua-filter={lua}",
                    "--shift-heading-level-by=-1", "--columns=1"], check=True)      # --columns=1: relative widths for all pipe tables
    with zipfile.ZipFile(out) as z: files = {n: z.read(n) for n in z.namelist()}
    doc = files["word/document.xml"].decode()
    widths = iter(table_widths(md_text) if journal else [SINGLE_W] * 100)
    doc = re.sub(r"<w:tbl>.*?</w:tbl>", lambda m: fix_table(m, widths), doc, flags=re.S)
    doc = math_sizes(doc, 9.5 if journal else 11)
    if journal and "FRONTTABLE" in doc:
        last = doc[doc.rindex("<w:sectPr"):]                         # pandoc renames the header and footer relationships
        hid = re.search(r'<w:headerReference[^>]*r:id="(\w+)"', last).group(1); fid = re.search(r'<w:footerReference[^>]*r:id="(\w+)"', last).group(1)
        doc = front_table(doc); doc, nf = (sections if LAYOUT == "sections" else floats)(doc)
        doc = doc.replace('r:id="rIdPageHeader"', f'r:id="{hid}"').replace('r:id="rIdPageFooter"', f'r:id="{fid}"')
        print(f"  {nf} figures and tables across both columns ({LAYOUT})")
    assert "<w:lnNumType" not in doc and "<w:footerReference" in doc, "page setup of the reference document was not applied"
    files["word/document.xml"] = doc.encode()
    sanitize(files)
    write_zip(out, files)


def main():
    os.makedirs(OUT, exist_ok=True)
    src = open(MD).read()
    with tempfile.TemporaryDirectory() as work:
        ref_j, ref_s, lua = (os.path.join(work, f) for f in ("ref_journal.docx", "ref_single.docx", "equations.lua"))
        reference_docx(ref_j, journal=True); reference_docx(ref_s, journal=False); open(lua, "w").write(LUA)
        for name, md, journal in [("manuscript.docx", manuscript_md(src), True), ("supplementary_material.docx", supplementary_md(src), False),
                                  ("highlights.docx", highlights_md(src), False)]:
            pandoc(md, os.path.join(OUT, name), ref_j if journal else ref_s, lua, work, journal); print("wrote", name)
    for ext in ("pdf", "png"):
        f = os.path.join(FIG, f"GraphicalAbstract.{ext}")
        if os.path.exists(f): shutil.copy2(f, os.path.join(OUT, f"graphical_abstract.{ext}"))
    f = os.path.join(FIG, "GraphicalAbstract.png")
    if os.path.exists(f):
        Image.open(f).convert("RGB").save(os.path.join(OUT, "graphical_abstract.tif"), compression="tiff_lzw", dpi=(600, 600))
        print("wrote graphical_abstract.{pdf,png,tif}")


if __name__ == "__main__":
    main()
