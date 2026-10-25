"""Seventeen source rules for the look generated interfaces keep repeating.

Each rule reads source. None of them render a page. Tailwind utilities and
plain CSS are both in scope, and a class defined in a stylesheet can make an
HTML element count as a card.
"""

from __future__ import annotations

import re
import urllib.parse
from dataclasses import dataclass

from tastelint.extract import Document, Element, Project, declarations
from tastelint.model import Finding
from tastelint.palette import (
    achromatic,
    contrast_ratio,
    colors_in,
    is_cool_stop,
    is_violet_accent,
    plain_color,
    utility_color,
)

COPY_SUFFIXES = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".js", ".ts", ".mdx"}

HYPE_PHRASES = (
    "unlock the power",
    "unleash your",
    "unleash the",
    "supercharge",
    "revolutionize",
    "next-generation",
    "next generation",
    "cutting-edge",
    "cutting edge",
    "elevate your",
    "seamless experience",
    "game-changing",
    "game changer",
    "the future of",
    "empower your",
    "harness the power",
    "reimagine",
    "streamline your",
    "all-in-one platform",
    "to the next level",
    "designed for the modern",
    "welcome to the future",
    "the ultimate",
    "beautifully simple",
    "everything you need",
    "one platform to",
)

FILLER_PATTERNS = (
    re.compile(r"lorem ipsum", re.I),
    re.compile(r"dolor sit amet", re.I),
    re.compile(r"your text here", re.I),
    re.compile(r"placeholder text", re.I),
    re.compile(r"\bchangeme\b", re.I),
    re.compile(r"todo:\s*add copy", re.I),
    re.compile(r"\[your [a-z ]+\]", re.I),
    re.compile(r"sample text", re.I),
    re.compile(r"insert (?:copy|text) here", re.I),
    re.compile(r"\bfeature (?:one|two|three|four|[1-4])\b", re.I),
)

EMPTY_CTA = re.compile(
    r"^(get started|learn more|click here|sign up now|start for free|try for free|"
    r"explore more|discover more|join now|submit)$",
    re.I,
)

EMOJI = re.compile(
    "["
    "\U0001F1E6-\U0001F1FF"
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U00002700-\U000027BF"
    "]+"
)

STOCK_FAMILIES = {
    "inter",
    "roboto",
    "open sans",
    "poppins",
    "nunito",
    "montserrat",
    "lato",
    "arial",
    "helvetica",
    "helvetica neue",
    "ui-sans-serif",
    "system-ui",
    "-apple-system",
    "blinkmacsystemfont",
    "segoe ui",
}

VIOLET_UTILITY = re.compile(
    r"^bg-(?:purple|violet|indigo|fuchsia)-(?:400|500|600|700)$"
)
GRADIENT_UTILITY = re.compile(r"bg-(?:gradient|linear)-to-[trbl]{1,2}")
STOP_UTILITY = re.compile(r"(?:from|via|to)-([a-z]+)-\d{2,3}")
VIOLET_FAMILIES = {"purple", "violet", "indigo", "fuchsia"}
RADIUS_UTILITY = re.compile(
    r"^rounded-(?:2xl|3xl|4xl|\[(\d*\.?\d+)(px|rem)\])$"
)
PILL_EXEMPT = re.compile(
    r"button|\bbtn\b|\bcta\b|pill|avatar|badge|chip|\borb\b",
    re.I,
)
CARD_TOKEN = re.compile(r"^(?:[\w]+-)*card(?:-[\w]+)*$", re.I)
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
FAMILY_DECL = re.compile(r"font-family\s*:\s*([^;}{]+)", re.I)
JS_FAMILY = re.compile(r"fontFamily\s*[:=]\s*['\"]([^'\"]+)['\"]")
TW_FONT = re.compile(r"font-\[([^\]]+)\]")
GOOGLE_FAMILY = re.compile(r"family=([^:&\"'>\s]+)")
GRADIENT_CALL = re.compile(r"(?:linear|radial|conic)-gradient\(", re.I)
SHADOW_TRIPLE = re.compile(
    r"(-?\d*\.?\d+)(px|rem)?\s+(-?\d*\.?\d+)(px|rem)?\s+(-?\d*\.?\d+)(px|rem)?"
)


@dataclass(frozen=True)
class Rule:
    id: str
    severity: str
    summary: str
    hint: str
    fn: object


RULES: list[Rule] = []


def rule(rule_id: str, severity: str, summary: str, hint: str):
    def decorate(fn):
        RULES.append(Rule(rule_id, severity, summary, hint, fn))
        return fn

    return decorate


def tokens(classes: str) -> list[str]:
    cleaned = []
    for raw in classes.split():
        token = raw.split(":")[-1]
        if token.startswith("!"):
            token = token[1:]
        if token:
            cleaned.append(token)
    return cleaned


def emit(doc: Document, spec: Rule, line: int, column: int = 1, message: str | None = None) -> Finding:
    if doc.lines:
        line = max(1, min(line, len(doc.lines)))
        snippet = doc.lines[line - 1].strip()[:180]
    else:
        line = 1
        snippet = ""
    return Finding(
        rule_id=spec.id,
        severity=spec.severity,
        message=message or spec.summary,
        hint=spec.hint,
        path=doc.path,
        line=line,
        column=max(1, column),
        snippet=snippet,
    )


def deduped(findings: list[Finding]) -> list[Finding]:
    seen = set()
    kept = []
    for finding in findings:
        key = (finding.rule_id, finding.path, finding.line)
        if key in seen:
            continue
        seen.add(key)
        kept.append(finding)
    return kept


def primary_family(value: str) -> str:
    first = value.split(",")[0].strip().strip("'\"")
    first = re.sub(r"\s+", " ", first)
    return first.lower()


def length_px(number: str, unit: str | None) -> float:
    value = float(number)
    if unit in {"rem", "em"}:
        return value * 16
    return value


def visible_lines(doc: Document):
    if doc.suffix in {".css", ".scss"}:
        return
    skipping = False
    for number, line in enumerate(doc.lines, 1):
        low = line.lower()
        if not skipping and ("<style" in low or "<script" in low):
            if "</style" not in low and "</script" not in low:
                skipping = True
                continue
        if skipping:
            if "</style" in low or "</script" in low:
                skipping = False
            continue
        stripped = line.strip()
        if stripped.startswith("<!--") or stripped.startswith("/*"):
            continue
        text = re.sub(r"<[^>]*>", " ", line)
        text = re.sub(r"\{[^{}]*\}", " ", text)
        yield number, text


def css_says_card(class_string: str, project: Project) -> bool:
    radius = False
    surface = False
    for token in class_string.split():
        for body in project.css_by_class.get(token, ()):
            decls = declarations(body)
            if "border-radius" in decls:
                radius = True
            shadow = decls.get("box-shadow", "")
            if shadow and shadow.lower() != "none":
                surface = True
            if "backdrop-filter" in decls or "-webkit-backdrop-filter" in decls:
                surface = True
            if "border" in decls or "border-width" in decls:
                surface = True
    return radius and surface


def looks_like_card(element: Element, project: Project) -> bool:
    toks = tokens(element.classes)
    if any(CARD_TOKEN.match(token) for token in toks):
        return True
    has_radius = any(token == "rounded" or token.startswith("rounded-") for token in toks)
    has_surface = False
    for token in toks:
        if token.startswith("shadow") or token.startswith("drop-shadow") or token.startswith("backdrop-blur"):
            has_surface = True
        elif token in {"bg-white", "bg-black", "bg-card"} or token.startswith("bg-white/") or token.startswith("bg-black/"):
            has_surface = True
        elif re.match(r"bg-(?:slate|gray|zinc|neutral|stone)-\d+", token):
            has_surface = True
        elif token == "border" or (
            token.startswith("border-")
            and token not in {"border-0", "border-none"}
            and not token.startswith("border-radius")
        ):
            has_surface = True
    if has_radius and has_surface:
        return True
    return css_says_card(element.classes, project)


def walk_with_ancestors(elements: list[Element], ancestors: tuple[Element, ...] = ()):
    for element in elements:
        yield element, ancestors
        yield from walk_with_ancestors(element.children, ancestors + (element,))


def property_line(doc: Document, block_line: int, prop: str) -> int:
    end = min(len(doc.lines), block_line + 30)
    pattern = re.compile(rf"(^|[^-]){re.escape(prop)}\s*:", re.I)
    for number in range(max(1, block_line), end + 1):
        if pattern.search(doc.lines[number - 1]):
            return number
    return block_line


def iter_gradient_calls(text: str):
    for match in GRADIENT_CALL.finditer(text):
        start = match.end() - 1
        depth = 0
        cursor = start
        while cursor < len(text):
            if text[cursor] == "(":
                depth += 1
            elif text[cursor] == ")":
                depth -= 1
                if depth == 0:
                    yield match.start(), text[match.start() : cursor + 1]
                    break
            cursor += 1


def radius_exempt(selector: str, tag: str = "") -> bool:
    if tag.lower() in {"button", "a", "input"}:
        return True
    return bool(PILL_EXEMPT.search(selector))


@rule(
    "gradient-wash",
    "high",
    "Cool purple-to-blue gradient.",
    "Paint a flat field, or mix two pigments you would write down in the brand notes.",
)
def gradient_wash(doc: Document, project: Project, spec: Rule) -> list[Finding]:
    del project
    hits = []
    seen = set()
    for start, call in iter_gradient_calls(doc.text):
        stops = colors_in(call)
        cool = [rgb for rgb in stops if is_cool_stop(rgb)]
        violet = [rgb for rgb in stops if is_violet_accent(rgb)]
        if len(cool) >= 2 and violet:
            line = doc.text.count("\n", 0, start) + 1
            if line not in seen:
                seen.add(line)
                hits.append(emit(doc, spec, line, column_from(doc.text, start)))
    for number, line in enumerate(doc.lines, 1):
        if number in seen:
            continue
        if not GRADIENT_UTILITY.search(line):
            continue
        families = STOP_UTILITY.findall(line)
        if any(family in VIOLET_FAMILIES for family in families):
            hits.append(emit(doc, spec, number, line.find("bg-") + 1 or 1))
    return hits


def column_from(text: str, offset: int) -> int:
    prior = text.rfind("\n", 0, offset)
    return offset - prior


@rule(
    "stock-sans",
    "medium",
    "Default sans, used as the actual face.",
    "Set the first family to a face you chose. Inter, Roboto, Poppins, and the system stack do not count.",
)
def stock_sans(doc: Document, project: Project, spec: Rule) -> list[Finding]:
    del project
    hits = []
    for number, line in enumerate(doc.lines, 1):
        flagged = False
        for match in FAMILY_DECL.finditer(line):
            if primary_family(match.group(1)) in STOCK_FAMILIES:
                hits.append(emit(doc, spec, number, match.start() + 1))
                flagged = True
                break
        if flagged:
            continue
        for match in JS_FAMILY.finditer(line):
            if primary_family(match.group(1)) in STOCK_FAMILIES:
                hits.append(emit(doc, spec, number, match.start() + 1))
                flagged = True
                break
        if flagged:
            continue
        for match in TW_FONT.finditer(line):
            if primary_family(match.group(1)) in STOCK_FAMILIES:
                hits.append(emit(doc, spec, number, match.start() + 1))
                flagged = True
                break
        if flagged:
            continue
        if "fonts.googleapis.com" in line or "fonts.gstatic.com" in line:
            decoded = urllib.parse.unquote(line)
            families = [urllib.parse.unquote(item).replace("+", " ") for item in GOOGLE_FAMILY.findall(decoded)]
            if any(primary_family(family) in STOCK_FAMILIES for family in families):
                hits.append(emit(doc, spec, number, line.lower().find("family=") + 1 or 1))
    return hits


@rule(
    "emoji-heading",
    "medium",
    "Emoji sitting in a heading.",
    "Write the heading. If it needs a mark, draw one or leave the space empty.",
)
def emoji_heading(doc: Document, project: Project, spec: Rule) -> list[Finding]:
    del project
    hits = []
    for element in doc.walk():
        if element.tag.lower() not in HEADING_TAGS:
            continue
        if EMOJI.search(element.full_text()):
            hits.append(emit(doc, spec, element.line, element.column))
    return hits


@rule(
    "emoji-icon",
    "low",
    "Emoji standing in for an icon.",
    "Use a drawn icon, or drop the mark. A pictograph is not a design system.",
)
def emoji_icon(doc: Document, project: Project, spec: Rule) -> list[Finding]:
    del project
    hits = []
    for element in doc.walk():
        if element.tag.lower() in HEADING_TAGS:
            continue
        # Own text only. A parent whose child is an emoji heading is not itself an icon.
        text = re.sub(r"\s+", " ", element.own_text).strip()
        if not text or not EMOJI.search(text):
            continue
        only = EMOJI.sub("", text).strip() == "" and len(text) <= 8
        starts = bool(EMOJI.match(text)) and len(text) <= 48
        iconish = "icon" in element.classes.lower()
        if only or iconish or (element.tag.lower() in {"span", "li", "p", "div"} and starts):
            hits.append(emit(doc, spec, element.line, element.column))
    return hits


@rule(
    "nested-card",
    "high",
    "Card nested inside a card.",
    "One surface is enough. Separate the inner block with space or type, not another rounded box.",
)
def nested_card(doc: Document, project: Project, spec: Rule) -> list[Finding]:
    hits = []
    for element, ancestors in walk_with_ancestors(doc.elements):
        if not looks_like_card(element, project):
            continue
        if any(looks_like_card(parent, project) for parent in ancestors):
            hits.append(emit(doc, spec, element.line, element.column))
    return hits


@rule(
    "radius-inflation",
    "medium",
    "Corner radius larger than the object.",
    "A control can be a pill. A section, card, or panel should stay near 8px or under.",
)
def radius_inflation(doc: Document, project: Project, spec: Rule) -> list[Finding]:
    del project
    hits = []
    for element in doc.walk():
        if radius_exempt("", element.tag):
            continue
        if any(token in {"btn", "cta", "pill", "avatar", "badge", "chip", "orb"} for token in tokens(element.classes)):
            continue
        for token in tokens(element.classes):
            match = RADIUS_UTILITY.match(token)
            if token in {"rounded-2xl", "rounded-3xl", "rounded-4xl"}:
                hits.append(emit(doc, spec, element.line, element.column))
                break
            if match and match.group(1):
                pixels = length_px(match.group(1), match.group(2))
                if pixels >= 20:
                    hits.append(emit(doc, spec, element.line, element.column))
                    break
    for block in doc.css_blocks:
        if radius_exempt(block.selector):
            continue
        decls = declarations(block.body)
        raw = decls.get("border-radius")
        if not raw:
            continue
        low = raw.lower().strip()
        if low.endswith("%") or "9999" in low:
            continue
        sizes = []
        for number, unit in re.findall(r"(\d*\.?\d+)(px|rem|em)?", low):
            if number:
                sizes.append(length_px(number, unit))
        if any(20 <= size <= 80 for size in sizes):
            hits.append(emit(doc, spec, property_line(doc, block.line, "border-radius")))
    return hits


@rule(
    "shadow-bloat",
    "medium",
    "Heavy drop shadow.",
    "A 1px edge or a change of ground color carries depth. Blur past 24px is fog.",
)
def shadow_bloat(doc: Document, project: Project, spec: Rule) -> list[Finding]:
    del project
    hits = []
    heavy = {"shadow-xl", "shadow-2xl", "drop-shadow-xl", "drop-shadow-2xl"}
    for element in doc.walk():
        if any(token in heavy for token in tokens(element.classes)):
            hits.append(emit(doc, spec, element.line, element.column))
    for block in doc.css_blocks:
        decls = declarations(block.body)
        raw = decls.get("box-shadow", "")
        if not raw or raw.lower() == "none":
            continue
        for match in SHADOW_TRIPLE.finditer(raw):
            blur = length_px(match.group(5), match.group(6))
            if blur >= 24:
                hits.append(emit(doc, spec, property_line(doc, block.line, "box-shadow")))
                break
    return hits


@rule(
    "hype-phrase",
    "high",
    "Sentence that could ship on any other product.",
    "Name the thing this product does, for whom, in words that would be false somewhere else.",
)
def hype_phrase(doc: Document, project: Project, spec: Rule) -> list[Finding]:
    del project
    hits = []
    for number, text in visible_lines(doc):
        low = text.lower()
        if any(phrase in low for phrase in HYPE_PHRASES):
            hits.append(emit(doc, spec, number))
    return hits


@rule(
    "filler-copy",
    "medium",
    "Placeholder copy still in the file.",
    "Replace lorem, 'your text here', and 'Feature One' before the page is reviewable.",
)
def filler_copy(doc: Document, project: Project, spec: Rule) -> list[Finding]:
    del project
    hits = []
    for number, text in visible_lines(doc):
        if any(pattern.search(text) for pattern in FILLER_PATTERNS):
            hits.append(emit(doc, spec, number))
    return hits


@rule(
    "gray-on-gray",
    "high",
    "Neutral text on a nearby neutral.",
    "Keep body type at 4.5:1 against the surface behind it. Gray on gray is unfinished, not quiet.",
)
def gray_on_gray(doc: Document, project: Project, spec: Rule) -> list[Finding]:
    del project
    hits = []
    for element in doc.walk():
        text_rgb = None
        bg_rgb = None
        for token in tokens(element.classes):
            parsed = utility_color(token)
            if not parsed:
                continue
            role, rgb = parsed
            if role == "text" and text_rgb is None:
                text_rgb = rgb
            elif role == "bg" and bg_rgb is None:
                bg_rgb = rgb
        if text_rgb and bg_rgb and achromatic(text_rgb) and achromatic(bg_rgb):
            if contrast_ratio(text_rgb, bg_rgb) < 4.5:
                hits.append(emit(doc, spec, element.line, element.column))
    for block in doc.css_blocks:
        decls = declarations(block.body)
        fg = plain_color(decls.get("color", ""))
        bg = plain_color(decls.get("background-color", "")) or plain_color(decls.get("background", ""))
        if not fg or not bg:
            continue
        if achromatic(fg) and achromatic(bg) and contrast_ratio(fg, bg) < 4.5:
            hits.append(emit(doc, spec, property_line(doc, block.line, "color")))
    return hits


def _page_selector(selector: str) -> bool:
    for part in selector.split(","):
        name = part.strip().lower()
        if name in {"body", "main", "html", "header", "section"}:
            return True
        if name.endswith(".hero") or name == ".hero":
            return True
    return False


@rule(
    "center-gravity",
    "medium",
    "Layout collapsed onto the center.",
    "Center one line if it is the point. Do not center the page, the hero, and the sections as a system.",
)
def center_gravity(doc: Document, project: Project, spec: Rule) -> list[Finding]:
    del project
    hits = []
    for element in doc.walk():
        toks = set(tokens(element.classes))
        hero_shell = bool({"min-h-screen", "h-screen", "min-h-svh", "min-h-dvh", "py-20", "py-24", "py-32"} & toks)
        if {"text-center", "items-center", "justify-center"} <= toks and hero_shell:
            hits.append(emit(doc, spec, element.line, element.column))
    for block in doc.css_blocks:
        decls = declarations(block.body)
        align = decls.get("text-align", "").lower()
        display = decls.get("display", "").lower()
        items = decls.get("align-items", "").lower()
        justify = decls.get("justify-content", "").lower()
        min_h = decls.get("min-height", "").lower()
        flex_center = display == "flex" and items == "center" and justify == "center"
        tall = "vh" in min_h or min_h in {"100%", "100vh"}
        if _page_selector(block.selector) and align == "center":
            hits.append(emit(doc, spec, property_line(doc, block.line, "text-align")))
        elif flex_center and tall:
            hits.append(emit(doc, spec, property_line(doc, block.line, "display")))
    return hits


@rule(
    "glass-panel",
    "medium",
    "Glass panel.",
    "A translucent blur is decoration. Use a solid ground unless the thing behind the panel is the content.",
)
def glass_panel(doc: Document, project: Project, spec: Rule) -> list[Finding]:
    del project
    hits = []
    for element in doc.walk():
        if any(token.startswith("backdrop-blur") for token in tokens(element.classes)):
            hits.append(emit(doc, spec, element.line, element.column))
    for block in doc.css_blocks:
        decls = declarations(block.body)
        blur = decls.get("backdrop-filter", "") + decls.get("-webkit-backdrop-filter", "")
        if "blur" in blur.lower():
            hits.append(emit(doc, spec, property_line(doc, block.line, "backdrop-filter")))
    return hits


def _three_column(element: Element, project: Project) -> bool:
    toks = tokens(element.classes)
    if "grid-cols-3" in toks:
        return True
    for token in element.classes.split():
        for body in project.css_by_class.get(token, ()):
            if re.search(r"grid-template-columns\s*:\s*repeat\(\s*3\s*,", body, re.I):
                return True
            if re.search(r"grid-template-columns\s*:\s*(?:1fr\s+){2}1fr", body, re.I):
                return True
    return False


@rule(
    "feature-trio",
    "medium",
    "Three matching feature cards.",
    "If the points differ, let the layout differ. Three equal cards is the default outline, not a decision.",
)
def feature_trio(doc: Document, project: Project, spec: Rule) -> list[Finding]:
    hits = []
    for element in doc.walk():
        children = [child for child in element.children if child.tag.lower() not in {"script", "style"}]
        cards = [child for child in children if looks_like_card(child, project)]
        if len(cards) != 3:
            continue
        if _three_column(element, project) or (len(children) == 3 and ("grid" in tokens(element.classes) or "flex" in tokens(element.classes))):
            hits.append(emit(doc, spec, element.line, element.column))
    return hits


@rule(
    "blur-orb",
    "low",
    "Decorative blur orb.",
    "Remove the absolute blurred circle. It does not identify the product.",
)
def blur_orb(doc: Document, project: Project, spec: Rule) -> list[Finding]:
    del project
    hits = []
    families = ("purple", "violet", "indigo", "blue", "fuchsia", "pink", "cyan")
    for element in doc.walk():
        toks = set(tokens(element.classes))
        positioned = "absolute" in toks or "fixed" in toks
        blurred = any(token.startswith("blur-") for token in toks)
        round_full = "rounded-full" in toks
        colored = any(token.startswith(f"bg-{family}") for family in families for token in toks)
        if positioned and blurred and round_full and colored:
            hits.append(emit(doc, spec, element.line, element.column))
    for block in doc.css_blocks:
        decls = declarations(block.body)
        position = decls.get("position", "").lower()
        blur = "blur" in decls.get("filter", "").lower()
        radius = decls.get("border-radius", "").lower()
        round_full = radius.strip() in {"50%", "9999px", "999px"} or "9999" in radius
        if position in {"absolute", "fixed"} and blur and round_full:
            hits.append(emit(doc, spec, property_line(doc, block.line, "filter")))
    return hits


@rule(
    "violet-default",
    "medium",
    "Indigo or violet used as the default accent.",
    "Pick a pigment on purpose. Purple, indigo, and fuchsia buttons are the unchosen accent.",
)
def violet_default(doc: Document, project: Project, spec: Rule) -> list[Finding]:
    del project
    hits = []
    for element in doc.walk():
        for token in tokens(element.classes):
            if VIOLET_UTILITY.match(token.split("/")[0]):
                hits.append(emit(doc, spec, element.line, element.column))
                break
    for block in doc.css_blocks:
        decls = declarations(block.body)
        for prop in ("background-color", "background"):
            raw = decls.get(prop, "")
            if not raw or "gradient" in raw.lower():
                continue
            color = plain_color(raw)
            if color and is_violet_accent(color):
                hits.append(emit(doc, spec, property_line(doc, block.line, prop)))
                break
    return hits


@rule(
    "gradient-text",
    "medium",
    "Gradient clipped into a headline.",
    "Set the headline in the ink color. A clipped gradient is the same costume as the purple wash.",
)
def gradient_text(doc: Document, project: Project, spec: Rule) -> list[Finding]:
    del project
    hits = []
    for number, line in enumerate(doc.lines, 1):
        if "bg-clip-text" in line and "text-transparent" in line:
            hits.append(emit(doc, spec, number))
    for block in doc.css_blocks:
        decls = declarations(block.body)
        clip = (decls.get("background-clip", "") + " " + decls.get("-webkit-background-clip", "")).lower()
        if "text" in clip.split():
            hits.append(emit(doc, spec, property_line(doc, block.line, "background-clip")))
    return hits


@rule(
    "empty-cta",
    "low",
    "Call to action with no object.",
    "Say what the control does: 'Reserve a firing slot', not 'Get Started' or 'Learn More'.",
)
def empty_cta(doc: Document, project: Project, spec: Rule) -> list[Finding]:
    del project
    hits = []
    for element in doc.walk():
        if element.tag.lower() not in {"a", "button"}:
            continue
        label = re.sub(r"\s+", " ", element.full_text()).strip(" .!")
        if EMPTY_CTA.match(label):
            hits.append(emit(doc, spec, element.line, element.column))
    return hits


def run_rules(doc: Document, project: Project) -> list[Finding]:
    found: list[Finding] = []
    for spec in RULES:
        found.extend(deduped(spec.fn(doc, project, spec)))
    return found
