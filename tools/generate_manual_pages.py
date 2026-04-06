from __future__ import annotations

import html
import re
from pathlib import Path


PROJECT_DIR = Path(r"C:\Users\monos\OneDrive\Desktop\workspace\IDN\manual\idn-manual-web")
SOURCE_DIR = PROJECT_DIR.parent
OUTPUT_DIR = PROJECT_DIR / "manuals"

ROLE_FILES = {
    "super-admin": "IDN2.0_매뉴얼초안_최고관리자.md",
    "group-admin": "IDN2.0_매뉴얼초안_그룹관리자.md",
    "user": "IDN2.0_매뉴얼초안_일반사용자.md",
}

ROLE_LABELS = {
    "super-admin": "최고 관리자",
    "group-admin": "그룹 관리자",
    "user": "일반 사용자",
}


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def slugify(text: str) -> str:
    slug = re.sub(r"[^\w가-힣]+", "-", text.strip().lower()).strip("-")
    return slug or "section"


def parse_table_row(line: str) -> list[str]:
    raw = line.strip()
    if raw.startswith("|"):
        raw = raw[1:]
    if raw.endswith("|"):
        raw = raw[:-1]
    return [cell.strip() for cell in raw.split("|")]


def is_sep_row(line: str) -> bool:
    cells = parse_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c or "---") for c in cells)


def table_to_html(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    classes = ["doc-table"]
    if rows[0][:2] in (["화면명", "이미지"], ["화면", "이미지 삽입 영역"]):
        classes.append("screenshot-table")
    header = "<thead><tr>" + "".join(f"<th>{esc(cell)}</th>" for cell in rows[0]) + "</tr></thead>"
    body_rows = []
    for row in rows[1:]:
        body_rows.append("<tr>" + "".join(f"<td>{esc(cell)}</td>" for cell in row) + "</tr>")
    body = "<tbody>" + "".join(body_rows) + "</tbody>"
    return f'<div class="table-wrap"><table class="{" ".join(classes)}">{header}{body}</table></div>'


def close_open_article(state: dict[str, bool], out: list[str]) -> None:
    if state["article_open"]:
        out.append("</article>")
        state["article_open"] = False


def close_open_section(state: dict[str, bool], out: list[str]) -> None:
    close_open_article(state, out)
    if state["section_open"]:
        out.append("</section>")
        state["section_open"] = False


def parse_heading_numbers(text: str) -> tuple[int, ...]:
    m = re.match(r"^(\d+(?:\.\d+)*)\.?(?:\s+|$)", text)
    if not m:
        return ()
    return tuple(int(part) for part in m.group(1).split("."))


def extract_headings(lines: list[str]) -> list[tuple[int, str, str]]:
    items: list[tuple[int, str, str, tuple[int, ...]]] = []
    for line in lines:
        stripped = line.strip()
        m = re.match(r"^(#{2,3})\s+(.*)$", stripped)
        if not m:
            continue
        level = len(m.group(1))
        text = m.group(2).strip()
        if text == "목차":
            continue
        if text.startswith("IDN 2.0 사용자 매뉴얼"):
            continue
        if text in {"최고 관리자", "그룹 관리자", "일반 사용자"}:
            continue
        if not re.match(r"^\d", text):
            continue
        items.append((level, text, slugify(text), parse_heading_numbers(text)))

    known_prefixes: set[tuple[int, ...]] = {numbers for _, _, _, numbers in items if numbers}
    depth_map: dict[tuple[int, ...], int] = {}
    resolved: list[tuple[int, str, str]] = []

    for fallback_level, text, anchor, numbers in items:
        toc_depth = fallback_level
        if numbers:
            ancestor_depth = 1
            for size in range(len(numbers) - 1, 0, -1):
                prefix = numbers[:size]
                if prefix in depth_map:
                    ancestor_depth = depth_map[prefix]
                    break
                if prefix in known_prefixes:
                    ancestor_depth = size + 1
                    break
            toc_depth = min(ancestor_depth + 1, 4)
            depth_map[numbers] = toc_depth
        resolved.append((toc_depth, text, anchor))

    return resolved


def render_manual(md_text: str, role_slug: str) -> tuple[str, str]:
    lines = md_text.splitlines()
    title = "IDN 2.0 사용자 매뉴얼"
    role = ROLE_LABELS[role_slug]
    toc_items = extract_headings(lines)

    out: list[str] = []
    state = {"section_open": False, "article_open": False}
    skip_toc_body = False

    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()

        if not line:
            i += 1
            continue

        if skip_toc_body:
            if line.startswith("#"):
                skip_toc_body = False
            else:
                i += 1
                continue

        if line.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            rows = [parse_table_row(x) for x in table_lines if not is_sep_row(x)]
            out.append(table_to_html(rows))
            continue

        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()

            if level == 1:
                title = text
                i += 1
                continue

            if level == 2 and text in {"최고 관리자", "그룹 관리자", "일반 사용자"}:
                role = text
                i += 1
                continue

            if level == 2 and text == "목차":
                skip_toc_body = True
                i += 1
                continue

            anchor = slugify(text)

            if level == 2:
                close_open_section(state, out)
                out.append(f'<section class="manual-section" id="{anchor}">')
                out.append(f"<h2>{esc(text)}</h2>")
                state["section_open"] = True
            elif level == 3:
                close_open_article(state, out)
                out.append(f'<article class="manual-article" id="{anchor}">')
                out.append(f"<h3>{esc(text)}</h3>")
                state["article_open"] = True

            i += 1
            continue

        if line.startswith("▶ "):
            body = line[2:].strip()
            if ":" in body:
                label, remainder = body.split(":", 1)
                out.append(
                    f'<p class="label-row"><span>▶</span><strong>{esc(label.strip())}:</strong> {esc(remainder.strip())}</p>'
                )
            else:
                out.append(f'<p class="label-row"><span>▶</span><strong>{esc(body)}</strong></p>')
            i += 1
            continue

        if re.match(r"^\d+\.\s+", line):
            out.append(f'<p class="step-line">{esc(line)}</p>')
            i += 1
            continue

        if line.startswith("- "):
            out.append(f'<p class="bullet-line">{esc(line[2:].strip())}</p>')
            i += 1
            continue

        out.append(f"<p>{esc(line)}</p>")
        i += 1

    close_open_section(state, out)

    toc_html = "".join(
        f'<a class="toc-link depth-{level}" href="#{anchor}">{esc(text)}</a>'
        for level, text, anchor in toc_items
    )
    hero_title = f"IDN 2.0 {role} 사용자 매뉴얼"
    body_html = "\n".join(out)

    page = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(hero_title)}</title>
  <link rel="stylesheet" href="../assets/css/tokens.css" />
  <link rel="stylesheet" href="../assets/css/base.css" />
  <link rel="stylesheet" href="../assets/css/layout.css" />
  <link rel="stylesheet" href="../assets/css/components.css" />
  <link rel="stylesheet" href="../assets/css/manual.css" />
</head>
<body data-manual-page>
  <div class="manual-app">
    <aside class="manual-sidebar" data-sidebar>
      <div class="manual-brand">
        <p class="eyebrow">IDN 2.0 Manual</p>
        <h1 class="manual-brand-title">{esc(role)}</h1>
        <div class="manual-brand-meta">
          <span class="meta-pill">Draft 0.1</span>
          <span class="meta-pill">웹 문서</span>
        </div>
      </div>
      <button class="sidebar-toggle" type="button" data-sidebar-toggle aria-expanded="false">목차 열기</button>
      <div class="manual-search" data-manual-search>
        <label class="manual-search-label" for="manual-search-input">목차 검색</label>
        <input
          id="manual-search-input"
          class="manual-search-input"
          type="search"
          placeholder="메뉴 또는 기능명 검색"
          data-search-input
        />
        <p class="manual-search-empty" data-search-empty hidden>검색 결과가 없습니다.</p>
      </div>
      <nav class="manual-toc" data-toc>
        {toc_html}
      </nav>
    </aside>
    <main class="manual-main">
      <header class="manual-hero">
        <p class="eyebrow">Operational Documentation</p>
        <h2>{esc(hero_title)}</h2>
        <p class="hero-copy">현재 운영 소스코드 기준으로 확인 가능한 메뉴와 기능을 정리한 웹 매뉴얼이다. 공통 스타일과 목차 구조를 유지한 정적 HTML 문서로 제공한다.</p>
      </header>
      <div class="manual-document">
        <div class="document-accent"></div>
        {body_html}
      </div>
    </main>
  </div>
  <script type="module" src="../assets/js/navigation.js"></script>
  <script type="module" src="../assets/js/toc.js"></script>
</body>
</html>
"""
    return hero_title, page


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for slug, filename in ROLE_FILES.items():
        src = SOURCE_DIR / filename
        md_text = src.read_text(encoding="utf-8")
        _, page = render_manual(md_text, slug)
        out = OUTPUT_DIR / f"{slug}.html"
        out.write_text(page, encoding="utf-8")
        print(f"CREATED: {out}")


if __name__ == "__main__":
    main()
