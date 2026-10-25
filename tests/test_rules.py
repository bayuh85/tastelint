from tastelint.extract import build_project, document_from_source
from tastelint.rules import RULES, run_rules


def ids_for(name: str, text: str) -> set[str]:
    doc = document_from_source(name, text)
    project = build_project([doc])
    return {finding.rule_id for finding in run_rules(doc, project)}


def test_rule_catalog_is_stable():
    assert len(RULES) >= 15
    assert len({spec.id for spec in RULES}) == len(RULES)


def test_gradient_wash_flags_purple_blue_and_ignores_clay():
    slop = ".hero { background: linear-gradient(135deg, #7c3aed 0%, #2563eb 100%); }"
    clay = ".dawn { background: linear-gradient(90deg, #9a3412, #f6f1ea); }"
    blue = ".sea { background: linear-gradient(90deg, #2563eb, #60a5fa); }"
    utility = '<div className="bg-gradient-to-r from-purple-500 to-blue-600"></div>'
    assert "gradient-wash" in ids_for("a.css", slop)
    assert "gradient-wash" not in ids_for("b.css", clay)
    assert "gradient-wash" not in ids_for("c.css", blue)
    assert "gradient-wash" in ids_for("d.tsx", utility)


def test_stock_sans_flags_the_first_family_only():
    inter = "body { font-family: Inter, Georgia, serif; }"
    link = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400&display=swap" rel="stylesheet" />'
    chosen = 'h1 { font-family: Fraunces, "Iowan Old Style", Georgia, serif; }'
    fallback = 'p { font-family: Fraunces, Helvetica, sans-serif; }'
    assert "stock-sans" in ids_for("a.css", inter)
    assert "stock-sans" in ids_for("a.html", link)
    assert "stock-sans" not in ids_for("b.css", chosen)
    assert "stock-sans" not in ids_for("c.css", fallback)


def test_emoji_heading_and_icon():
    heading = "<h2>🚀 Ship the kiln</h2>"
    icon = '<span class="icon">🔥</span>'
    prose = "<p>The Monday firing has twelve slots and no pictographs.</p>"
    assert "emoji-heading" in ids_for("a.html", heading)
    assert "emoji-icon" not in ids_for("a.html", heading)
    assert "emoji-icon" in ids_for("b.html", icon)
    assert "emoji-heading" not in ids_for("c.html", prose)
    assert "emoji-icon" not in ids_for("c.html", prose)


def test_nested_card_and_feature_trio():
    nested = """
    <section class="hero">
      <article class="card"><div class="card inner">Notes</div></article>
    </section>
    """
    trio = """
    <div class="grid grid-cols-3">
      <article class="card">One</article>
      <article class="card">Two</article>
      <article class="card">Three</article>
    </div>
    """
    pair = """
    <div class="grid grid-cols-2">
      <article class="card">Bowl</article>
      <article class="card">Cup</article>
    </div>
    """
    assert "nested-card" in ids_for("a.html", nested)
    assert "feature-trio" in ids_for("b.html", trio)
    assert "feature-trio" not in ids_for("c.html", pair)


def test_radius_and_shadow_thresholds():
    puffy = ".panel { border-radius: 32px; box-shadow: 0 25px 50px rgba(0,0,0,.2); }"
    quiet = ".book { border-radius: 2px; box-shadow: 0 1px 2px rgba(0,0,0,.08); }"
    pill = ".cta { border-radius: 9999px; }"
    utility = '<div class="rounded-3xl shadow-2xl"></div>'
    assert "radius-inflation" in ids_for("a.css", puffy)
    assert "shadow-bloat" in ids_for("a.css", puffy)
    assert "radius-inflation" not in ids_for("b.css", quiet)
    assert "shadow-bloat" not in ids_for("b.css", quiet)
    assert "radius-inflation" not in ids_for("c.css", pill)
    assert {"radius-inflation", "shadow-bloat"} <= ids_for("d.html", utility)


def test_copy_rules():
    hype = "<p>Unlock the power of next-generation teamwork.</p>"
    specific = "<p>Orders open Monday 2 November. Twelve slots.</p>"
    filler = "<p>Lorem ipsum dolor sit amet, your text here. Feature One.</p>"
    assert "hype-phrase" in ids_for("a.html", hype)
    assert "hype-phrase" not in ids_for("b.html", specific)
    assert "filler-copy" in ids_for("c.html", filler)
    assert "filler-copy" not in ids_for("b.html", specific)


def test_gray_on_gray_and_real_ink():
    muted = '<p class="text-gray-400 bg-gray-100">Hard to read.</p>'
    css = ".muted { color: #9ca3af; background: #f3f4f6; }"
    ink = ".page { color: #1c1917; background: #f6f1ea; }"
    strong = '<p class="text-gray-900 bg-white">Readable.</p>'
    assert "gray-on-gray" in ids_for("a.html", muted)
    assert "gray-on-gray" in ids_for("b.css", css)
    assert "gray-on-gray" not in ids_for("c.css", ink)
    assert "gray-on-gray" not in ids_for("d.html", strong)


def test_center_glass_orb_violet_and_gradient_text():
    hero = '<section class="flex min-h-screen items-center justify-center text-center">Hi</section>'
    left = '<section class="text-left">Hi</section>'
    glass = '<div class="backdrop-blur-md bg-white/10"></div>'
    orb = '<div class="absolute rounded-full bg-purple-400 blur-3xl"></div>'
    violet = '<button class="bg-indigo-600">Reserve a firing slot</button>'
    blue = '<button class="bg-blue-600">Reserve a firing slot</button>'
    clipped = '<h1 class="bg-clip-text text-transparent">Kiln</h1>'
    assert "center-gravity" in ids_for("a.html", hero)
    assert "center-gravity" not in ids_for("b.html", left)
    assert "glass-panel" in ids_for("c.html", glass)
    assert "blur-orb" in ids_for("d.html", orb)
    assert "violet-default" in ids_for("e.html", violet)
    assert "violet-default" not in ids_for("f.html", blue)
    assert "empty-cta" not in ids_for("e.html", violet)
    assert "gradient-text" in ids_for("g.html", clipped)


def test_empty_cta_is_exact():
    generic = '<a href="#">Learn More</a>'
    specific = '<a href="#book">Reserve a firing slot</a>'
    assert "empty-cta" in ids_for("a.html", generic)
    assert "empty-cta" not in ids_for("b.html", specific)


def test_css_trio_uses_a_class_defined_elsewhere():
    html = """
    <section class="features">
      <article class="card">A</article>
      <article class="card">B</article>
      <article class="card">C</article>
    </section>
    """
    css = ".features { display: grid; grid-template-columns: repeat(3, 1fr); }"
    page = document_from_source("index.html", html)
    sheet = document_from_source("styles.css", css)
    project = build_project([page, sheet])
    found = {finding.rule_id for finding in run_rules(page, project)}
    assert "feature-trio" in found


def test_vue_and_svelte_are_parsed():
    vue = """
    <template><h2>🚀 Unlock the power of pricing</h2></template>
    <style scoped>
    h2 { font-family: Poppins, sans-serif; }
    </style>
    """
    svelte = '<span class="icon">🔥</span><button class="bg-purple-600">Learn More</button>'
    assert {"emoji-heading", "hype-phrase", "stock-sans"} <= ids_for("Pricing.vue", vue)
    assert {"emoji-icon", "violet-default", "empty-cta"} <= ids_for("Badge.svelte", svelte)
