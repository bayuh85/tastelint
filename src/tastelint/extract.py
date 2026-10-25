"""Turn a UI source file into elements and CSS blocks.

The parser is deliberately small. It understands tags, class strings, and
style blocks well enough to point at a line. It does not execute JavaScript
and it does not lay the page out.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}

_CLASS_ATTR = re.compile(
    r"""(?:className|class)\s*=\s*(?:\{\s*)?(?P<q>["'`])(?P<value>.*?)(?P=q)""",
    re.DOTALL,
)
_STYLE_CLOSE = re.compile(r"</(style|script)\s*>", re.IGNORECASE)


@dataclass
class Element:
    tag: str
    classes: str
    line: int
    column: int
    children: list[Element] = field(default_factory=list)
    own_text: str = ""

    def full_text(self) -> str:
        parts = [self.own_text.strip()] if self.own_text.strip() else []
        for child in self.children:
            text = child.full_text()
            if text:
                parts.append(text)
        return re.sub(r"\s+", " ", " ".join(parts)).strip()


@dataclass
class CssBlock:
    selector: str
    body: str
    line: int


@dataclass
class Document:
    path: str
    text: str
    suffix: str
    lines: list[str]
    elements: list[Element]
    css_blocks: list[CssBlock]

    def walk(self):
        def visit(nodes):
            for node in nodes:
                yield node
                yield from visit(node.children)

        yield from visit(self.elements)


@dataclass
class Project:
    documents: list[Document]
    css_by_class: dict[str, list[str]]


def line_at(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def column_at(text: str, offset: int) -> int:
    last = text.rfind("\n", 0, offset)
    return offset - last


def extract_classes(attr_raw: str) -> str:
    parts = [match.group("value") for match in _CLASS_ATTR.finditer(attr_raw)]
    return " ".join(part.strip() for part in parts if part.strip())


def parse_css(text: str) -> list[CssBlock]:
    """Flatten a stylesheet, including rules nested in a single @-block."""
    cleaned = re.sub(
        r"/\*.*?\*/",
        lambda match: re.sub(r"[^\n]", " ", match.group(0)),
        text,
        flags=re.DOTALL,
    )
    return _parse_css_region(cleaned, base_line=1)


def _parse_css_region(text: str, base_line: int) -> list[CssBlock]:
    blocks: list[CssBlock] = []
    index = 0
    length = len(text)
    while True:
        brace = text.find("{", index)
        if brace < 0:
            break
        selector = " ".join(text[index:brace].split())
        depth = 1
        cursor = brace + 1
        while cursor < length and depth:
            char = text[cursor]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            cursor += 1
        body = text[brace + 1 : cursor - 1]
        open_line = base_line + text.count("\n", 0, brace)
        if selector.startswith("@") and "{" in body:
            blocks.extend(_parse_css_region(body, open_line))
        elif selector and not selector.startswith("@"):
            blocks.append(CssBlock(selector=selector[-180:], body=body, line=open_line))
        index = cursor
    return blocks


def declarations(body: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for part in body.split(";"):
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        name = key.strip().lower()
        if name:
            found[name] = value.strip()
    return found


def parse_markup(text: str) -> tuple[list[Element], list[tuple[int, str]]]:
    roots: list[Element] = []
    stack: list[Element] = []
    styles: list[tuple[int, str]] = []
    length = len(text)
    index = 0
    text_start = 0

    def flush(end: int) -> None:
        if not stack:
            return
        raw = text[text_start:end]
        cleaned = re.sub(r"\{[^{}]*\}", " ", raw)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if cleaned:
            stack[-1].own_text = (stack[-1].own_text + " " + cleaned).strip()

    while index < length:
        if text.startswith("<!--", index):
            flush(index)
            close = text.find("-->", index + 4)
            index = length if close < 0 else close + 3
            text_start = index
            continue
        if text.startswith("<!", index) or text.startswith("<?", index):
            flush(index)
            close = text.find(">", index)
            index = length if close < 0 else close + 1
            text_start = index
            continue
        if text.startswith("<>", index) or text.startswith("</>", index):
            flush(index)
            index += 3 if text.startswith("</>", index) else 2
            text_start = index
            continue
        if text[index] != "<":
            index += 1
            continue
        nxt = text[index + 1] if index + 1 < length else ""
        if nxt != "/" and not nxt.isalpha():
            index += 1
            continue

        flush(index)
        closing = nxt == "/"
        cursor = index + (2 if closing else 1)
        name_start = cursor
        while cursor < length and (text[cursor].isalnum() or text[cursor] in ":._-"):
            cursor += 1
        if cursor == name_start:
            index += 1
            text_start = index
            continue
        name = text[name_start:cursor]
        quote = ""
        braces = 0
        attr_start = cursor
        while cursor < length:
            char = text[cursor]
            if quote:
                if char == "\\" and quote != "`":
                    cursor += 2
                    continue
                if char == quote:
                    quote = ""
                cursor += 1
                continue
            if char in "\"'`":
                quote = char
                cursor += 1
                continue
            if char == "{":
                braces += 1
                cursor += 1
                continue
            if char == "}" and braces:
                braces -= 1
                cursor += 1
                continue
            if char == ">" and braces == 0:
                break
            cursor += 1
        if cursor >= length:
            break
        attr_raw = text[attr_start:cursor]
        self_closing = attr_raw.rstrip().endswith("/")
        tag_line = line_at(text, index)
        tag_col = column_at(text, index)

        if not closing and name.lower() in {"script", "style"}:
            match = _STYLE_CLOSE.search(text, cursor + 1)
            body_end = match.start() if match else length
            if name.lower() == "style":
                styles.append((line_at(text, cursor + 1), text[cursor + 1 : body_end]))
            index = match.end() if match else length
            text_start = index
            continue

        if closing:
            target = name.lower()
            while stack:
                top = stack.pop()
                if top.tag.lower() == target:
                    break
            index = cursor + 1
            text_start = index
            continue

        element = Element(
            tag=name,
            classes=extract_classes(attr_raw),
            line=tag_line,
            column=tag_col,
        )
        if stack:
            stack[-1].children.append(element)
        else:
            roots.append(element)
        if not self_closing and name.lower() not in VOID_TAGS:
            stack.append(element)
        index = cursor + 1
        text_start = index
    return roots, styles


def document_from_source(path: str, text: str) -> Document:
    suffix = Path(path).suffix.lower()
    lines = text.splitlines()
    elements: list[Element] = []
    css_blocks: list[CssBlock] = []
    if suffix in {".css", ".scss"}:
        css_blocks = parse_css(text)
    else:
        elements, style_chunks = parse_markup(text)
        for start_line, chunk in style_chunks:
            for block in parse_css(chunk):
                css_blocks.append(
                    CssBlock(
                        selector=block.selector,
                        body=block.body,
                        line=start_line + block.line - 1,
                    )
                )
    return Document(
        path=path,
        text=text,
        suffix=suffix,
        lines=lines,
        elements=elements,
        css_blocks=css_blocks,
    )


def load_document(path: Path, display: str) -> Document:
    text = path.read_text(encoding="utf-8", errors="replace")
    return document_from_source(display, text)


def build_project(documents: list[Document]) -> Project:
    index: dict[str, list[str]] = {}
    for doc in documents:
        for block in doc.css_blocks:
            for name in re.findall(r"\.([A-Za-z_][\w-]*)", block.selector):
                index.setdefault(name, []).append(block.body)
    return Project(documents=documents, css_by_class=index)
