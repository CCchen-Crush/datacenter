#!/usr/bin/env python3
"""Word files for the Applied Energy submission, built from paper/manuscript.md with pandoc (>= 3).

Usage: python3 tools/build_word.py                          (writes paper/word/)
  manuscript.docx              title page, highlights, abstract, nomenclature, text with native Word equations
                               (numbers right-aligned), tables, Algorithm 1, figures at their first citation,
                               declarations and references; A4, Times New Roman 12 pt, double spacing,
                               continuous line numbers and page numbers
  highlights.docx              the highlights as a separate file
  supplementary_material.docx  Figs. S1-S7 with their captions
  graphical_abstract.*         copied from paper/figures (python3 tools/plot_paper.py GA)
Author details and declarations are placeholders shaded in yellow. Figures are taken from paper/figures.
"""
import glob, hashlib, os, re, shutil, subprocess, tempfile, zipfile
from PIL import Image, ImageFont

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MD, FIG, OUT = (os.path.join(ROOT, "paper", p) for p in ("manuscript.md", "figures", "word"))
MAX_W_CM = 15.9                                   # A4 with 2.5 cm margins: 16 cm text width
FIGREF = re.compile(r"(Figs?\.\s*)((?:S?\d+)(?:[a-f](?:–[a-f])?)?(?:(?:,\s*|\s+and\s+)(?:S?\d+(?:[a-f](?:–[a-f])?)?|[a-f](?:–[a-f])?)(?!\w))*)")

# ------------------------------------------------------------------ reference document: styles, page, line numbers
FONT = '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="Times New Roman" w:cs="Times New Roman"/>'
SZ = lambda pt: f'<w:sz w:val="{int(2 * pt)}"/><w:szCs w:val="{int(2 * pt)}"/>'
BORDER = lambda side, sz: f'<w:{side} w:val="single" w:sz="{sz}" w:space="0" w:color="000000"/>'


def spacing(before=0, after=0, line=480):
    return f'<w:spacing w:before="{before}" w:after="{after}" w:line="{line}" w:lineRule="auto"/>'


def style(sid, name, kind="paragraph", based="Normal", nxt=None, ppr="", rpr="", custom=True, extra=""):
    return (f'<w:style w:type="{kind}"' + (' w:customStyle="1"' if custom else "") + f' w:styleId="{sid}"><w:name w:val="{name}"/>'
            + (f'<w:basedOn w:val="{based}"/>' if based else "") + (f'<w:next w:val="{nxt}"/>' if nxt else "") + "<w:qFormat/>"
            + (f"<w:pPr>{ppr}</w:pPr>" if ppr else "") + (f"<w:rPr>{rpr}</w:rPr>" if rpr else "") + extra + "</w:style>")


STYLES = [
    style("BodyText", "Body Text", custom=False, ppr=spacing() + '<w:jc w:val="both"/>'),
    style("FirstParagraph", "First Paragraph", based="BodyText", nxt="BodyText"),
    style("Compact", "Compact", based="BodyText", ppr='<w:jc w:val="left"/>'),
    style("Title", "Title", custom=False, nxt="BodyText", ppr="<w:keepNext/>" + spacing(0, 360, 360) + '<w:jc w:val="center"/>',
          rpr="<w:b/><w:bCs/>" + SZ(16)),
    style("Subtitle", "Subtitle", custom=False, nxt="BodyText", ppr=spacing(0, 360, 360) + '<w:jc w:val="center"/>', rpr="<w:i/><w:iCs/>" + SZ(12)),
    style("Author", "Author", nxt="BodyText", ppr=spacing(0, 120, 360) + '<w:jc w:val="center"/>'),
    style("AbstractTitle", "Abstract Title", based="Normal", nxt="Abstract", ppr="<w:keepNext/>" + spacing(240, 120, 276), rpr="<w:b/><w:bCs/>"),
    style("Abstract", "Abstract", based="BodyText"),
    style("Heading1", "Heading 1", custom=False, nxt="BodyText", ppr="<w:keepNext/><w:keepLines/>" + spacing(360, 120, 276) + '<w:outlineLvl w:val="0"/>',
          rpr="<w:b/><w:bCs/>" + SZ(12)),
    style("Heading2", "Heading 2", custom=False, nxt="BodyText", ppr="<w:keepNext/><w:keepLines/>" + spacing(240, 120, 276) + '<w:outlineLvl w:val="1"/>',
          rpr="<w:b/><w:bCs/><w:i/><w:iCs/>" + SZ(12)),
    style("Heading3", "Heading 3", custom=False, nxt="BodyText", ppr="<w:keepNext/><w:keepLines/>" + spacing(240, 60, 276) + '<w:outlineLvl w:val="2"/>',
          rpr="<w:i/><w:iCs/>" + SZ(12)),
    style("Bibliography", "Bibliography", custom=False, nxt="Bibliography", ppr=spacing() + '<w:ind w:left="567" w:hanging="567"/>'),
    style("Caption", "Caption", custom=False, ppr=spacing(0, 120, 276) + '<w:jc w:val="both"/>', rpr=SZ(11)),
    style("TableCaption", "Table Caption", based="Caption", ppr="<w:keepNext/>" + spacing(240, 120, 276)),
    style("FigureCaption", "Figure Caption", based="Caption", ppr=spacing(60, 240, 276)),
    style("ImageCaption", "Image Caption", based="FigureCaption"),
    style("Figure", "Figure", ppr="<w:keepNext/>" + spacing(240, 60, 240) + '<w:jc w:val="center"/>'),
    style("CaptionedFigure", "Captioned Figure", based="Figure"),
    style("Equation", "Equation", ppr='<w:keepLines/><w:tabs><w:tab w:val="center" w:pos="4535"/><w:tab w:val="right" w:pos="9070"/></w:tabs>'
          + spacing(120, 120, 276)),
    style("TableText", "Table Text", ppr=spacing(20, 20, 240) + '<w:jc w:val="left"/>', rpr=SZ(10)),
    style("Placeholder", "Placeholder", kind="character", based="DefaultParagraphFont", rpr='<w:shd w:val="clear" w:color="auto" w:fill="FFFF00"/>'),
    style("Hyperlink", "Hyperlink", kind="character", custom=False, based="DefaultParagraphFont", rpr='<w:color w:val="1F4E79"/>'),
    ('<w:style w:type="table" w:default="1" w:styleId="Table"><w:name w:val="Table"/><w:basedOn w:val="TableNormal"/><w:qFormat/>'
     '<w:tblPr><w:tblInd w:w="0" w:type="dxa"/><w:tblBorders>' + BORDER("top", 8) + BORDER("bottom", 8) + "</w:tblBorders>"
     '<w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="85" w:type="dxa"/><w:bottom w:w="0" w:type="dxa"/>'
     '<w:right w:w="85" w:type="dxa"/></w:tblCellMar></w:tblPr>'
     '<w:tblStylePr w:type="firstRow"><w:tcPr><w:tcBorders>' + BORDER("bottom", 4) + "</w:tcBorders></w:tcPr></w:tblStylePr></w:style>"),
]
DOCDEFAULTS = ("<w:docDefaults><w:rPrDefault><w:rPr>" + FONT + SZ(12) + '<w:lang w:val="en-GB" w:eastAsia="zh-CN" w:bidi="ar-SA"/>'
               "</w:rPr></w:rPrDefault><w:pPrDefault><w:pPr>" + spacing() + "</w:pPr></w:pPrDefault></w:docDefaults>")
SECTPR = ('<w:sectPr><w:footerReference w:type="default" r:id="rIdPageFooter"/><w:pgSz w:w="11906" w:h="16838"/>'
          '<w:pgMar w:top="1418" w:right="1418" w:bottom="1418" w:left="1418" w:header="709" w:footer="709" w:gutter="0"/>'
          '<w:lnNumType w:countBy="1" w:distance="284" w:restart="continuous"/><w:cols w:space="708"/></w:sectPr>')
FOOTER = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
          '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
          'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:p><w:pPr><w:suppressLineNumbers/>'
          + spacing(0, 0, 240) + '<w:jc w:val="center"/></w:pPr><w:r><w:fldChar w:fldCharType="begin"/></w:r>'
          '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r>'
          '<w:r><w:t>1</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>')


def reference_docx(path):
    subprocess.run(["pandoc", "-o", path, "--print-default-data-file", "reference.docx"], check=True)
    with zipfile.ZipFile(path) as z: files = {n: z.read(n) for n in z.namelist()}
    st = files["word/styles.xml"].decode()
    st = re.sub(r"<w:docDefaults>.*?</w:docDefaults>", DOCDEFAULTS, st, count=1, flags=re.S)
    for new in STYLES:
        sid = re.search(r'w:styleId="([^"]+)"', new).group(1)
        pat = re.compile(r'<w:style [^>]*w:styleId="%s">.*?</w:style>' % re.escape(sid), re.S)
        st = pat.sub(lambda m: new, st, count=1) if pat.search(st) else st.replace("</w:styles>", new + "</w:styles>")
    files["word/styles.xml"] = st.encode()
    doc = files["word/document.xml"].decode(); assert "<w:sectPr />" in doc
    files["word/document.xml"] = doc.replace("<w:sectPr />", SECTPR).encode()
    files["word/footer1.xml"] = FOOTER.encode()
    rel = ('<Relationship Id="rIdPageFooter" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" '
           'Target="footer1.xml"/>')
    files["word/_rels/document.xml.rels"] = files["word/_rels/document.xml.rels"].decode().replace("</Relationships>", rel + "</Relationships>").encode()
    ct = '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
    files["[Content_Types].xml"] = files["[Content_Types].xml"].decode().replace("</Types>", ct + "</Types>").encode()
    write_zip(path, files)


def write_zip(path, files):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for n, b in files.items(): z.writestr(n, b)


# ------------------------------------------------------------------ numbered equations (pandoc drops \tag)
LUA = r"""
-- display equation with \tag{n}: equation at the centre tab, "(n)" at the right tab (paragraph style Equation)
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
ALGORITHM_MD5 = "adfcce69c5d1f277bf87da3b609ddfc6"     # code block of Algorithm 1 that ALGORITHM reproduces
ALGORITHM = r"""| | **Algorithm 1** |
|---|------------------------------------------------------------------------------------------|
| | **Input:** historical days $\Omega^{DA}$, operating days $\Omega$, commitment grid $\mathcal G$, reliability $\rho$, event set $\mathcal K$, horizon $H$, plant parameters |
| | **Output:** commitment $C^*$, firm capacity $\hat C^{firm}_\rho$, closed-loop trajectories |
| 1 | **Day-ahead recovery-aware commitment** (Eqs. (15)–(19)) |
| 2 | &emsp;for $C\in\mathcal G$ in increasing order and every day $d\in\Omega^{DA}$ that delivered all smaller $C$: run the closed loop (steps 7–12) → cost $J_d(C)$ and full delivery; capability $\xi_d$ (15) |
| 3 | &emsp;$\varepsilon\leftarrow\varepsilon_N$ (18); $C^{DRO}_\rho\leftarrow\max\{C:\ \Phi_\rho(C)\ge\varepsilon\}$ (17); $C^*\leftarrow\arg\min\{\bar J(C):\ C\le C^{DRO}_\rho\}$ (19) |
| 4 | **Firm capacity on the operating days** (SAA, Eq. (13)) |
| 5 | &emsp;for every $C\in\mathcal G$ and $\omega\in\Omega$: run the closed loop (steps 7–12) with commitment $C$ |
| 6 | &emsp;$\hat C^{firm}_\rho\leftarrow$ largest $C$ whose full-delivery share is at least $\rho$ for all $C'\le C$; bootstrap confidence intervals over days |
| 7 | **Intraday operation** (every $\Delta t$ = 15 min) |
| 8 | &emsp;measure $\mathbf x_t=(B_{1..3,t},E_t,S_t)$, the gas-engine state, the event status and the loads |
| 9 | &emsp;correct the forecasts with the latest observed errors (or build the scenario tree, JR-S) |
| 10 | &emsp;solve the joint recovery MILP (2)–(11) over $t,\dots,t+H$ with all confirmed events |
| 11 | &emsp;apply the first-step decisions; replay the plant (storage → TES → compute throttling) |
| 12 | &emsp;update the backlogs by earliest-deadline-first execution and the settlement records |
| 13 | **return** $C^*$, $\hat C^{firm}_\rho$ and the trajectories |"""

PH = lambda text: "[" + text + ']{custom-style="Placeholder"}'
TITLE_PAGE = "\n\n".join(f'::: {{custom-style="Author"}}\n{PH(t)}\n:::' for t in (
    "Author names (affiliation letters as superscripts; an asterisk marks the corresponding author)",
    "Affiliations", "\\* Corresponding author. E-mail address")) + "\n\n```{=openxml}\n<w:p><w:r><w:br w:type=\"page\"/></w:r></w:p>\n```"
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


def _cells(row):
    """Cells of a pipe-table row; a | inside $...$ belongs to the cell."""
    row = row.strip(); assert row.startswith("|") and row.endswith("|"), row
    cells, cur, math = [], "", False
    for ch in row[1:-1]:
        if ch == "$": math = not math
        if ch == "|" and not math: cells.append(cur); cur = ""
        else: cur += ch
    return cells + [cur]


def _visible(cell):
    """Approximate printed length of a Markdown cell: a LaTeX command prints as one character."""
    t = re.sub(r"\$([^$]*)\$", lambda m: re.sub(r"[{}^_]|\\[ ,;!]", "", re.sub(r"\\[A-Za-z]+", "x", m.group(1))), cell)
    return re.sub(r"\*\*|\\(?=\*)", "", t.replace("&emsp;", "  ")).strip()


def _font():
    """Times New Roman or its metric twin, to size the table columns; None if neither is installed."""
    for name in ("LiberationSerif-Regular.ttf", "times.ttf", "Times New Roman.ttf"):
        try: return ImageFont.truetype(name, 100)
        except OSError: pass


_F = _font()
text_pt = (lambda s: _F.getlength(s) / 10) if _F else (lambda s: 5.0 * len(s))      # printed width at 10 pt (points)


def column_widths(block, text=453.5, pad=12.0):
    """Pipe table whose relative column widths (dashes of the separator) follow its content at 10 pt: every column
    holds its longest word and, if they are short, its cells on one line; the remaining width goes to the columns
    whose text would otherwise wrap most."""
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
    return "\n".join(rows)


def two_lines_11(block):
    """Objective (11) in two aligned lines: it is wider than the text."""
    for a, b in [("$$J=", "$$\\begin{aligned}J=&"), ("\\Big]\\Delta t-\\sum_k", "\\Big]\\Delta t\\\\&-\\sum_k"),
                 ("J^{term}, \\tag{11}$$", "J^{term},\\end{aligned} \\tag{11}$$")]:
        assert block.count(a) == 1, a; block = block.replace(a, b)
    return block


def figure(label, caption):
    f = glob.glob(os.path.join(FIG, f"Fig{label}_*.png")); assert len(f) == 1, (label, f)
    w = min(Image.open(f[0]).size[0] / 300 * 2.54, MAX_W_CM)
    return div("Figure", f"![]({f[0]}){{width={w:.2f}cm}}") + "\n\n" + div("Figure Caption", f"**Fig. {label}.** {caption}")


def parse(src):
    """Title, body (Highlights ... Appendix B), figure captions and references of the Markdown manuscript."""
    first, rest = src.split("\n", 1); assert first.startswith("# ")
    rest = re.sub(r"\A\s*> Draft for[^\n]*\n", "", rest)                  # editorial note of the Markdown draft
    body, tail = rest.split("## Figure captions\n"); caps, refs = tail.split("## References\n")
    caps = dict(re.findall(r"^\*\*Fig\. (S?\d+)\.\*\* (.+)$", caps, re.M))
    refs = [l for l in refs.strip().split("\n") if l.strip()]
    assert len(caps) == 21 and all(re.match(r"\[\d+\] ", l) for l in refs) and len(refs) == 38
    return first[2:].strip(), body, caps, refs


def manuscript_md(src):
    title, body, caps, refs = parse(src)
    blocks = [b for b in body.strip("\n").split("\n\n") if b.strip()]
    cited = {}                                                           # main figure -> block of its first citation
    for i, b in enumerate(blocks):
        if b.startswith(("#", "|", "```")): continue
        for m in FIGREF.finditer(b):
            for n in re.findall(r"S?\d+", m.group(2)):
                if not n.startswith("S"): cited.setdefault(n, i)
    assert sorted(map(int, cited)) == list(range(1, 15)), sorted(cited)
    out = [f'---\ntitle: "{title}"\nlang: en-GB\n---', TITLE_PAGE]
    for i, b in enumerate(blocks):
        if b.startswith("```") and "Algorithm 1" in b:
            code = b.split("\n", 1)[1].rsplit("```", 1)[0]
            assert hashlib.md5(code.encode()).hexdigest() == ALGORITHM_MD5, "Algorithm 1 changed: update ALGORITHM in build_word.py"
            b = column_widths(ALGORITHM)
        elif b.startswith("|"):
            b = column_widths(b)
        elif "\\tag{11}" in b:
            b = two_lines_11(b)
        elif b.startswith("**Table "):
            b = div("Table Caption", b)
        elif b.startswith("## Appendix A."):
            out.append(DECLARATIONS)
        out.append(b)
        for n in sorted((k for k, v in cited.items() if v == i), key=int):
            out.append(figure(n, caps[n]))
    out += ["## References", div("Bibliography", "\n\n".join(refs))]
    return "\n\n".join(out) + "\n"


def supplementary_md(src):
    title, _, caps, _ = parse(src)
    out = [f'---\ntitle: "Supplementary material"\nsubtitle: "{title}"\nlang: en-GB\n---']
    out += [figure(f"S{k}", caps[f"S{k}"]) for k in range(1, 8)]
    return "\n\n".join(out) + "\n"


def highlights_md(src):
    hl = re.search(r"^## Highlights\n\n((?:- .+\n)+)", src, re.M).group(1)
    assert all(len(l[2:]) <= 85 for l in hl.strip().split("\n")), "a highlight exceeds 85 characters"
    return '---\ntitle: "Highlights"\nlang: en-GB\n---\n\n' + hl


# ------------------------------------------------------------------ pandoc and post-processing
TEXT_W = 9070                                     # text width in twentieths of a point (16 cm)


def fix_table(m):
    """Three-line table (rules above and below the table and below the header; none for the headerless nomenclature),
    fixed column widths from the Markdown separator scaled to the text width, 10-pt single-spaced cell text."""
    t = m.group(0)
    head = "<w:tblHeader" in t
    g = [int(x) for x in re.findall(r'<w:gridCol w:w="(\d+)"', t)]
    g = [1814, TEXT_W - 1814] if not head and len(g) == 2 else [round(x * TEXT_W / sum(g)) for x in g]   # nomenclature 20/80 %
    g[-1] += TEXT_W - sum(g)
    t = re.sub(r"<w:tblGrid>.*?</w:tblGrid>", "<w:tblGrid>" + "".join(f'<w:gridCol w:w="{x}"/>' for x in g) + "</w:tblGrid>", t, count=1, flags=re.S)
    nil = "".join(f'<w:{s} w:val="nil"/>' for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
    pr = "<w:tblBorders>" + (BORDER("top", 8) + BORDER("bottom", 8) if head else nil) + '</w:tblBorders><w:tblLayout w:type="fixed"/>'
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
    for parent in ("m:rPr", "m:dPr", "m:mcPr"): doc = reorder(doc, parent)
    files["word/document.xml"] = doc.encode()
    num = files["word/numbering.xml"].decode()
    files["word/numbering.xml"] = re.sub(r'(<w:nsid w:val=")([0-9A-F]{1,7})"', lambda m: m.group(1) + m.group(2).rjust(8, "0") + '"', num).encode()
    files["word/settings.xml"] = reorder(files["word/settings.xml"].decode(), "w:settings").encode()
    ct = files["[Content_Types].xml"].decode()
    if 'Extension="png"' not in ct:
        ct = ct.replace('<Default Extension="xml"', '<Default Extension="png" ContentType="image/png" /><Default Extension="xml"', 1)
    files["[Content_Types].xml"] = ct.encode()


def _first(ppr, pat):
    m = re.search(pat, ppr)
    return m.group(0) + ppr[:m.start()] + ppr[m.end():] if m else ppr


def _after_tblw(tblpr):
    m = re.search(r"<w:jc [^>]*/>", tblpr); w = re.search(r"<w:tblW [^>]*/>", tblpr)
    if not (m and w) or m.start() < w.start(): return tblpr
    rest = tblpr[:m.start()] + tblpr[m.end():]; k = rest.index(w.group(0)) + len(w.group(0))
    return rest[:k] + m.group(0) + rest[k:]


def pandoc(md_text, out, ref, lua, work):
    src = os.path.join(work, os.path.basename(out) + ".md")
    open(src, "w").write(md_text)
    subprocess.run(["pandoc", src, "-f", "markdown", "-o", out, f"--reference-doc={ref}", f"--lua-filter={lua}",
                    "--shift-heading-level-by=-1", "--columns=1"], check=True)      # --columns=1: relative widths for all pipe tables
    with zipfile.ZipFile(out) as z: files = {n: z.read(n) for n in z.namelist()}
    doc = files["word/document.xml"].decode()
    doc = re.sub(r"<w:tbl>.*?</w:tbl>", fix_table, doc, flags=re.S)
    assert "<w:lnNumType" in doc and "<w:footerReference" in doc, "page setup of the reference document was not applied"
    files["word/document.xml"] = doc.encode()
    sanitize(files)
    write_zip(out, files)


def main():
    os.makedirs(OUT, exist_ok=True)
    src = open(MD).read()
    with tempfile.TemporaryDirectory() as work:
        ref, lua = os.path.join(work, "reference.docx"), os.path.join(work, "equations.lua")
        reference_docx(ref); open(lua, "w").write(LUA)
        for name, md in [("manuscript.docx", manuscript_md(src)), ("supplementary_material.docx", supplementary_md(src)),
                         ("highlights.docx", highlights_md(src))]:
            pandoc(md, os.path.join(OUT, name), ref, lua, work); print("wrote", name)
    for ext in ("pdf", "png"):
        f = os.path.join(FIG, f"GraphicalAbstract.{ext}")
        if os.path.exists(f): shutil.copy2(f, os.path.join(OUT, f"graphical_abstract.{ext}"))
    f = os.path.join(FIG, "GraphicalAbstract.png")
    if os.path.exists(f):
        Image.open(f).convert("RGB").save(os.path.join(OUT, "graphical_abstract.tif"), compression="tiff_lzw", dpi=(600, 600))
        print("wrote graphical_abstract.{pdf,png,tif}")


if __name__ == "__main__":
    main()
