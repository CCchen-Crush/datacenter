#!/usr/bin/env python3
"""Two-column PDF of the manuscript in the layout of a typeset journal article, from paper/manuscript.md (pandoc + pdflatex).

Usage: python3 tools/build_latex.py          (writes paper/latex/manuscript.tex and paper/latex/manuscript.pdf)

Layout: A4, two columns, Charter text with Charter math letters, title block with highlights, article information and
abstract across the page, nomenclature in the column flow, numbered section heads (bold) and subsection heads (italic),
left-aligned equations numbered on the right, three-line tables, full-width figures at the top of a page with centred
captions, numbered references in a small font and blue cross-references. No line numbers. Author details are
placeholders. The text is converted by pandoc; tables, figures and the front matter are assembled here.
"""
import glob, os, re, subprocess, sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MD, FIG, OUT = os.path.join(ROOT, "paper", "manuscript.md"), os.path.join(ROOT, "paper", "figures"), os.path.join(ROOT, "paper", "latex")
SEP = "ZZSEPARATORZZ"
SHORT_TITLE = "Recovery-aware scheduling for consecutive demand response of AI data centers"
FIGREF = re.compile(r"(Figs?\.\s*)((?:S?\d+)(?:[a-f](?:–[a-f])?)?(?:(?:,\s*|\s+and\s+)(?:S?\d+(?:[a-f](?:–[a-f])?)?|[a-f](?:–[a-f])?)(?!\w))*)")
# the same in pandoc's LaTeX: "Fig.~3a--b"
FIGREF_TEX = re.compile(r"(Figs?\.(?:~|\\ |\s)*)((?:S?\d+)(?:[a-f](?:--[a-f])?)?(?:(?:,\s*|\s+and\s+)(?:S?\d+(?:[a-f](?:--[a-f])?)?|[a-f](?:--[a-f])?)(?!\w))*)")

PREAMBLE = r"""\documentclass[a4paper,twocolumn,fleqn,10pt]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb}
\usepackage{charter}
\usepackage[italic,defaultmathsizes]{mathastext}
\usepackage[a4paper,top=19mm,bottom=19mm,left=15mm,right=15mm,columnsep=6.5mm,headheight=12pt,headsep=5mm,footskip=8mm]{geometry}
\usepackage{graphicx,booktabs,tabularx,array,pifont,xcolor,enumitem,fancyhdr,titlesec,caption,microtype}
\usepackage[hyphens]{url}
\usepackage{flushend}
\usepackage[colorlinks=true,linkcolor=refblue,citecolor=refblue,urlcolor=refblue,bookmarks=true,pdfborder={0 0 0}]{hyperref}
\definecolor{refblue}{RGB}{0,110,190}
\definecolor{rulegray}{RGB}{120,120,120}
\makeatletter
\renewcommand\normalsize{\@setfontsize\normalsize{9.3}{11.6}\abovedisplayskip 6pt plus 2pt minus 2pt\belowdisplayskip 6pt plus 2pt minus 2pt
  \abovedisplayshortskip 3pt plus 1pt\belowdisplayshortskip 4pt plus 2pt}
\renewcommand\small{\@setfontsize\small{8.6}{10.6}}
\renewcommand\footnotesize{\@setfontsize\footnotesize{7.8}{9.4}}
\renewcommand\scriptsize{\@setfontsize\scriptsize{7}{8.4}}
\renewcommand\large{\@setfontsize\large{11}{13.5}}
\makeatother
\setlength{\mathindent}{1.2em}
\setlength{\parindent}{1.1em}
\setlength{\parskip}{0pt}
\emergencystretch=1.5em
\raggedbottom
\hyphenpenalty=600
\renewcommand{\topfraction}{0.9}\renewcommand{\bottomfraction}{0.6}\renewcommand{\textfraction}{0.08}
\renewcommand{\floatpagefraction}{0.75}\renewcommand{\dbltopfraction}{0.95}\renewcommand{\dblfloatpagefraction}{0.75}
\setcounter{topnumber}{3}\setcounter{dbltopnumber}{2}\setcounter{totalnumber}{5}
\setlength{\dbltextfloatsep}{12pt plus 3pt minus 2pt}\setlength{\textfloatsep}{10pt plus 3pt minus 2pt}
\titleformat{\section}{\normalsize\bfseries}{}{0pt}{}
\titleformat{\subsection}{\normalsize\itshape}{}{0pt}{}
\titleformat{\subsubsection}{\normalsize\itshape}{}{0pt}{}
\titlespacing*{\section}{0pt}{11pt plus 3pt minus 1pt}{5pt plus 1pt}
\titlespacing*{\subsection}{0pt}{8pt plus 2pt minus 1pt}{4pt plus 1pt}
\titlespacing*{\subsubsection}{0pt}{7pt plus 2pt minus 1pt}{3pt plus 1pt}
\DeclareCaptionLabelFormat{figlab}{\textbf{Fig.~#2.}}
\DeclareCaptionLabelFormat{tablab}{\textbf{Table~#2}}
\captionsetup[figure]{font=footnotesize,labelformat=figlab,labelsep=space,justification=justified,singlelinecheck=true,skip=4pt}
\captionsetup[table]{font=footnotesize,labelformat=tablab,labelsep=newline,justification=raggedright,singlelinecheck=false,skip=3pt,position=top}
\newlist{nomlist}{description}{1}
\setlist[nomlist]{font=\normalfont,leftmargin=5.6em,labelwidth=5.2em,labelsep=0.4em,align=left,itemsep=0pt,parsep=0pt,topsep=1pt,partopsep=0pt}
\setlist[itemize]{leftmargin=1.2em,itemsep=1pt,parsep=0pt,topsep=2pt}
\setlist[enumerate]{leftmargin=2em,itemsep=2pt,parsep=0pt,topsep=2pt}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\DeclareUnicodeCharacter{2212}{\ensuremath{-}}
\DeclareUnicodeCharacter{2264}{\ensuremath{\leq}}
\DeclareUnicodeCharacter{2265}{\ensuremath{\geq}}
\DeclareUnicodeCharacter{2192}{\ensuremath{\rightarrow}}
\DeclareUnicodeCharacter{03C4}{\ensuremath{\tau}}
\DeclareUnicodeCharacter{03B3}{\ensuremath{\gamma}}
\DeclareUnicodeCharacter{220E}{\ensuremath{\blacksquare}}
\DeclareUnicodeCharacter{2713}{\ding{51}}
\newcommand{\spaced}[1]{{\scriptsize\textls[200]{\MakeUppercase{#1}}}}
\newcommand{\placeholder}[1]{\textcolor{rulegray}{[#1]}}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\footnotesize\itshape SHORTTITLE}
\fancyfoot[C]{\footnotesize\thepage}
\renewcommand{\headrulewidth}{0pt}
\fancypagestyle{plain}{\fancyhf{}\fancyfoot[C]{\footnotesize\thepage}\renewcommand{\headrulewidth}{0pt}}
\hypersetup{pdftitle={TITLE},pdfsubject={Manuscript submitted to Applied Energy}}
\graphicspath{{FIGDIR/}}
"""


def blocks(text):
    return [b for b in text.strip("\n").split("\n\n") if b.strip()]


class Pandoc:
    """Markdown snippets converted to LaTeX in one pandoc call."""
    def __init__(self): self.items = []
    def add(self, md): self.items.append(md); return len(self.items) - 1
    def run(self):
        src = f"\n\n{SEP}\n\n".join(self.items)
        out = subprocess.run(["pandoc", "-f", "markdown-auto_identifiers-implicit_figures", "-t", "latex", "--wrap=none"], input=src,
                             capture_output=True, text=True, check=True).stdout
        self.out = [p.strip() for p in re.split(r"\n*" + SEP + r"\n*", out)]
        assert len(self.out) == len(self.items), (len(self.out), len(self.items))
    def __getitem__(self, k): return self.out[k]


def cells(row):
    """Cells of a pipe-table row; a | inside $...$ belongs to the cell."""
    row = row.strip(); assert row.startswith("|") and row.endswith("|"), row
    out, cur, math = [], "", False
    for ch in row[1:-1]:
        if ch == "$": math = not math
        if ch == "|" and not math: out.append(cur.strip()); cur = ""
        else: cur += ch
    return out + [cur.strip()]


def visible(cell):
    """Approximate printed length of a Markdown cell (a LaTeX command prints as one character)."""
    t = re.sub(r"\$([^$]*)\$", lambda m: re.sub(r"[{}^_]|\\[ ,;!]", "", re.sub(r"\\[A-Za-z]+", "x", m.group(1))), cell)
    return len(re.sub(r"\*\*|\\(?=\*)", "", t).strip())


def link_refs(tex, nref):
    """Numeric citations {[}n,m–k{]} -> blue hyperlinks to the reference list; figure and table references -> links."""
    def cite(m):
        parts = []
        for tok in m.group(1).split(","):
            ends = tok.split("--")
            if not all(e.isdigit() and 1 <= int(e) <= nref for e in ends): return m.group(0)
            parts.append("--".join(f"\\hyperlink{{ref{e}}}{{{e}}}" for e in ends))
        return "[" + ",".join(parts) + "]"
    tex = re.sub(r"\{\[\}(\d+(?:(?:--|,)\d+)*)\{\]\}", cite, tex)
    def figs(m):
        body = re.sub(r"(?<![\w.])(\d+)", lambda k: f"\\hyperref[fig{k.group(1)}]{{{k.group(1)}}}", m.group(2))
        return m.group(1) + body
    tex = FIGREF_TEX.sub(figs, tex)
    tex = re.sub(r"Table~?\s?(A?\d+)", lambda m: f"\\hyperref[tab{m.group(1)}]{{Table~{m.group(1)}}}", tex)
    return tex


class Builder:
    def __init__(self, src):
        self.pd = Pandoc()
        first, rest = src.split("\n", 1); assert first.startswith("# ")
        self.title = first[2:].strip()
        rest = re.sub(r"\A\s*> Draft for[^\n]*\n", "", rest)
        body, tail = rest.split("## Figure captions\n"); caps, refs = tail.split("## References\n")
        self.caps = dict(re.findall(r"^\*\*Fig\. (S?\d+)\.\*\* (.+)$", caps, re.M))
        self.refs = [re.match(r"\[(\d+)\] (.+)$", l).groups() for l in refs.strip().split("\n") if l.strip()]
        sec = re.split(r"^## ", body, flags=re.M)
        self.sections = {s.split("\n", 1)[0].strip(): s.split("\n", 1)[1] for s in sec if s.strip()}
        self.parts = []                                     # (kind, payload) in document order

    # ---------------------------------------------------------------- front matter
    def front(self):
        hl = re.findall(r"^- (.+)$", self.sections["Highlights"], re.M)
        abstract, kw = self.sections["Abstract"].strip().split("\n\n")
        kws = [k.strip() for k in re.sub(r"^\*\*Keywords:\*\*\s*", "", kw).split(";")]
        self.k_title = self.pd.add(self.title); self.k_hl = [self.pd.add(h) for h in hl]
        self.k_abs = self.pd.add(abstract); self.k_kw = [self.pd.add(k) for k in kws]

    def front_tex(self):
        hl = "\n".join(f"\\item {self.pd[k]}" for k in self.k_hl)
        kw = "\\\\\n".join(self.pd[k] for k in self.k_kw)
        return rf"""\twocolumn[{{%
\begin{{flushleft}}
{{\fontsize{{16.5}}{{20.5}}\selectfont {self.pd[self.k_title]}\par}}
\vspace{{9pt}}
{{\large \placeholder{{Author names}}\textsuperscript{{a,*}}\par}}
\vspace{{4pt}}
{{\scriptsize \textsuperscript{{a}}\placeholder{{Affiliation, city, postcode, country}}\par}}
\end{{flushleft}}
\vspace{{6pt}}{{\color{{rulegray}}\hrule height 0.4pt}}\vspace{{5pt}}
\spaced{{Highlights}}\par\vspace{{2pt}}
{{\footnotesize\begin{{itemize}}[leftmargin=0.9em,label=\textbullet,itemsep=0pt,topsep=0pt]
{hl}
\end{{itemize}}}}
\vspace{{5pt}}{{\color{{rulegray}}\hrule height 0.4pt}}\vspace{{8pt}}
\noindent\begin{{minipage}}[t]{{0.27\textwidth}}
\spaced{{Article info}}\par\vspace{{2pt}}{{\color{{rulegray}}\hrule height 0.4pt}}\vspace{{4pt}}
{{\footnotesize\raggedright\textit{{Keywords:}}\\
{kw}\par}}
\end{{minipage}}\hfill
\begin{{minipage}}[t]{{0.70\textwidth}}
\spaced{{Abstract}}\par\vspace{{2pt}}{{\color{{rulegray}}\hrule height 0.4pt}}\vspace{{4pt}}
{{\small {self.pd[self.k_abs]}\par}}
\end{{minipage}}
\vspace{{14pt}}
}}]
{{\renewcommand{{\thefootnote}}{{}}\footnotetext{{\textsuperscript{{*}}\,Corresponding author. E-mail address: \placeholder{{e-mail}}.}}}}
"""

    # ---------------------------------------------------------------- nomenclature
    def nomenclature(self):
        txt = self.sections["Nomenclature"]
        self.k_nomnote = None; self.nom = []
        for b in blocks(txt):
            if b.startswith("**") and b.endswith("**"): self.nom.append(("head", b.strip("*")))
            elif b.startswith("|"):
                rows = [cells(r) for r in b.split("\n")[2:]]
                self.nom.append(("rows", [(self.pd.add(a), self.pd.add(d)) for a, d in rows]))
            else: self.k_nomnote = self.pd.add(b)

    def nomenclature_tex(self):
        out = ["\\section*{Nomenclature}", "{\\footnotesize"]
        if self.k_nomnote is not None: out.append("\\noindent " + self.pd[self.k_nomnote] + "\\par")
        for kind, val in self.nom:
            if kind == "head": out.append(f"\\par\\vspace{{3pt}}\\noindent\\textit{{{val}}}\\par")
            else: out.append("\\begin{nomlist}\n" + "\n".join(f"\\item[{{{self.pd[a]}}}] {self.pd[d]}" for a, d in val) + "\n\\end{nomlist}")
        out.append("}")
        return "\n".join(out)

    # ---------------------------------------------------------------- body
    def body(self):
        order = [k for k in self.sections if re.match(r"\d+\. |Appendix [AB]\. ", k)]
        cited = {}
        for name in order:
            head = self.pd.add(re.sub(r"^(\d+\.|Appendix [AB]\.)\s*", "", name))
            num = re.match(r"(\d+\.|Appendix [AB]\.)", name).group(1)
            self.parts.append(("h2", (num, head)))
            if name.startswith("Appendix A."): self.parts.append(("appendix", None))
            bl = blocks(self.sections[name]); i = 0
            while i < len(bl):
                b = bl[i]
                m = re.match(r"(#{3,4}) ((?:\d+\.)+)\s*(.*)", b)
                if m:
                    self.parts.append(("h3" if m.group(1) == "###" else "h4", (m.group(2), self.pd.add(m.group(3))))); i += 1; continue
                if b.startswith("**Table "):
                    num, cap = re.match(r"\*\*Table (A?\d+)\.\*\*\s*(.*)", b, re.S).groups()
                    tab = bl[i + 1]; assert tab.startswith("|"), num
                    notes = []
                    if i + 2 < len(bl) and bl[i + 2].startswith("^a^"): notes = [self.pd.add(bl[i + 2])]
                    rows = [cells(r) for r in tab.split("\n")]
                    self.parts.append(("table", dict(num=num, cap=self.pd.add(cap), head=[self.pd.add(c) for c in rows[0]],
                                                     rows=[[self.pd.add(c) for c in r] for r in rows[2:]], raw=rows, notes=notes)))
                    i += 2 + len(notes); continue
                self.parts.append(("text", self.pd.add(b)))
                if not b.startswith(("#", "|")):
                    for mm in FIGREF.finditer(b):
                        for n in re.findall(r"S?\d+", mm.group(2)):
                            if not n.startswith("S") and n not in cited:
                                cited[n] = True; self.parts.append(("figure", n))
                i += 1
        assert sorted(map(int, cited)) == list(range(1, 17)), sorted(cited)
        self.k_caps = {n: self.pd.add(c) for n, c in self.caps.items()}
        self.k_refs = [(n, self.pd.add(t)) for n, t in self.refs]

    def table_tex(self, t):
        raw = t["raw"]; ncol = len(raw[0]); head = t["head"]; body = t["rows"]
        lens = [max(visible(r[j]) for r in raw if len(r) == ncol) for j in range(ncol)]
        total = sum(lens) + 2 * ncol
        wide = total > 62 or t["num"] in ("1", "A1")
        env = "table*" if wide else "table"; width = "\\textwidth" if wide else "\\columnwidth"
        if t["num"] == "1":                                   # Algorithm 1: one column, header row bold
            spec = ">{\\raggedright\\arraybackslash}X"
        else:
            spec = ""
            for j, L in enumerate(lens):
                spec += ">{\\raggedright\\arraybackslash}X" if L > (24 if wide else 16) else "l"
            if "X" not in spec: spec = spec[:-1] + ">{\\raggedright\\arraybackslash}X"
        size = "\\scriptsize" if (wide and ncol >= 6) or t["num"] in ("A1",) else "\\footnotesize"
        rows = " & ".join(self.pd[c] for c in head) + " \\\\\n\\midrule\n"
        rows += "\n".join(" & ".join(self.pd[c] for c in r) + " \\\\" for r in body)
        notes = "".join(f"\n\\par\\vspace{{2pt}}{{\\scriptsize {self.pd[k]}\\par}}" for k in t["notes"])
        setnum = (f"\\renewcommand{{\\thetable}}{{A\\arabic{{table}}}}\\setcounter{{table}}{{{int(t['num'][1:]) - 1}}}" if t["num"].startswith("A")
                  else f"\\setcounter{{table}}{{{int(t['num']) - 1}}}")
        return (f"\\begin{{{env}}}[!t]\n{setnum}\n\\caption{{{self.pd[t['cap']]}}}\\label{{tab{t['num']}}}\n{size}\\setlength{{\\tabcolsep}}{{4pt}}\n"
                f"\\begin{{tabularx}}{{{width}}}{{{spec}}}\n\\toprule\n{rows}\n\\bottomrule\n\\end{{tabularx}}{notes}\n\\end{{{env}}}")

    def figure_tex(self, n):
        """Figure at its natural size (never enlarged): one column if it fits, else across the page."""
        f = glob.glob(os.path.join(FIG, f"Fig{n}_*.pdf")); assert len(f) == 1, (n, f)
        from PIL import Image
        w_in = Image.open(f[0][:-4] + ".png").size[0] / 300
        env, width = ("figure", f"{min(w_in, 3.4):.2f}in") if w_in <= 3.6 else ("figure*", f"{min(w_in, 7.05):.2f}in")
        return (f"\\begin{{{env}}}[!t]\n\\setcounter{{figure}}{{{int(n) - 1}}}\n\\centering\n\\includegraphics[width={width}]{{{os.path.basename(f[0])}}}\n"
                f"\\caption{{{self.pd[self.k_caps[n]]}}}\\label{{fig{n}}}\n\\end{{{env}}}")

    def body_tex(self):
        out = []
        for kind, val in self.parts:
            if kind == "h2":
                num, k = val; title = self.pd[k]
                plain = re.sub(r"[\\{}$^_]", "", title)
                out.append(f"\\pdfbookmark[1]{{{num} {plain}}}{{s{len(out)}}}\\section*{{{num}~{title}}}")
            elif kind in ("h3", "h4"):
                num, k = val; cmd = "subsection" if kind == "h3" else "subsubsection"
                out.append(f"\\{cmd}*{{{num}~{self.pd[k]}}}")
            elif kind == "appendix": pass
            elif kind == "text": out.append(self.pd[val])
            elif kind == "table": out.append(self.table_tex(val))
            elif kind == "figure": out.append(self.figure_tex(val))
        return "\n\n".join(out)

    def refs_tex(self):
        items = "\n".join(f"\\item[{{\\hypertarget{{ref{n}}}{{[{n}]}}}}] {self.pd[k]}" for n, k in self.k_refs)
        return ("\\section*{References}\n{\\footnotesize\n\\begin{list}{}{\\setlength{\\leftmargin}{2.1em}\\setlength{\\labelwidth}{1.9em}"
                "\\setlength{\\labelsep}{0.3em}\\setlength{\\itemsep}{1pt}\\setlength{\\parsep}{0pt}\\setlength{\\topsep}{2pt}"
                "\\renewcommand{\\makelabel}[1]{#1\\hfill}}\n" + items + "\n\\end{list}}")

    def build(self):
        self.front(); self.nomenclature(); self.body(); self.pd.run()
        nref = len(self.refs)
        doc = (PREAMBLE.replace("SHORTTITLE", SHORT_TITLE).replace("TITLE", self.title).replace("FIGDIR", FIG.replace("\\", "/"))
               + "\\begin{document}\n\\thispagestyle{plain}\n" + self.front_tex() + "\n" + self.nomenclature_tex() + "\n\n"
               + link_refs(self.body_tex(), nref) + "\n\n" + self.refs_tex() + "\n\\end{document}\n")
        return doc


def main():
    os.makedirs(OUT, exist_ok=True)
    tex = Builder(open(MD).read()).build()
    path = os.path.join(OUT, "manuscript.tex"); open(path, "w").write(tex)
    for _ in range(2):
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "manuscript.tex"], cwd=OUT, capture_output=True, text=True)
        if r.returncode:
            print(r.stdout[-3000:]); sys.exit("pdflatex failed")
    for ext in ("aux", "log", "out"):
        p = os.path.join(OUT, f"manuscript.{ext}")
        if ext != "log" and os.path.exists(p): os.remove(p)
    print("wrote", os.path.relpath(path, ROOT), "and manuscript.pdf")


if __name__ == "__main__":
    main()
