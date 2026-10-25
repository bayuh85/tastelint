# tastelint

Coding agents ship the same interface over and over: a purple-to-blue gradient, Inter, a centered hero, three rounded cards, a glass panel, and a sentence like "Unlock the power of…". tastelint is an offline taste linter for that habit. It reads UI source, names the pattern, and scores it before the page ships.

## What it does

- `tastelint scan` walks HTML, CSS, SCSS, JSX/TSX, Vue, Svelte, and Tailwind class strings with a deterministic rule engine. No network, no browser, no model. It prints `file:line` findings, a 0–100 taste score, and exits non-zero when the score is under `--fail-under`.
- `tastelint review` sends a compact summary of those findings to an OpenAI-compatible chat endpoint and asks for edits that name a file and a replacement.
- `tastelint skill install` writes an original design guide where Claude Code, Cursor, and Codex look for instructions, and tells the agent to run the scanner.

The stance behind the rules is the Plain Surface Charter: a typeface you can defend, one pigment, sentences that would be false on another product, and depth that does not come from nested cards.

## Quickstart

Requires Python 3.10 or newer. The scanner's runtime dependencies are the standard library.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
tastelint scan examples
pytest
```

`examples/sloppy-landing` is a deliberately generic marketing page (HTML, CSS, React, Vue, and Svelte). `examples/quiet-studio` is a small ceramics-studio page that should stay at 100.

## Example output

This is the output of `tastelint scan examples` in this repository:

```
tastelint 0.1.0
examples  ·  7 files  ·  85 findings (25 high, 52 medium, 8 low)  ·  taste score 0/100

examples/sloppy-landing/Badge.svelte:2  low     emoji-icon        Emoji standing in for an icon.
examples/sloppy-landing/Badge.svelte:3  low     empty-cta         Call to action with no object.
examples/sloppy-landing/Badge.svelte:3  medium  violet-default    Indigo or violet used as the default accent.
examples/sloppy-landing/Hero.tsx:3  medium  center-gravity    Layout collapsed onto the center.
examples/sloppy-landing/Hero.tsx:3  medium  radius-inflation  Corner radius larger than the object.
examples/sloppy-landing/Hero.tsx:3  medium  shadow-bloat      Heavy drop shadow.
examples/sloppy-landing/Hero.tsx:3  high    gradient-wash     Cool purple-to-blue gradient.
examples/sloppy-landing/Hero.tsx:4  low     blur-orb          Decorative blur orb.
examples/sloppy-landing/Hero.tsx:4  medium  violet-default    Indigo or violet used as the default accent.
examples/sloppy-landing/Hero.tsx:5  medium  emoji-heading     Emoji sitting in a heading.
examples/sloppy-landing/Hero.tsx:6  medium  gradient-text     Gradient clipped into a headline.
examples/sloppy-landing/Hero.tsx:6  high    gradient-wash     Cool purple-to-blue gradient.
examples/sloppy-landing/Hero.tsx:7  medium  stock-sans        Default sans, used as the actual face.
examples/sloppy-landing/Hero.tsx:9  high    hype-phrase       Sentence that could ship on any other product.
examples/sloppy-landing/Hero.tsx:11  high    gray-on-gray      Neutral text on a nearby neutral.
examples/sloppy-landing/Hero.tsx:11  high    nested-card       Card nested inside a card.
examples/sloppy-landing/Hero.tsx:11  medium  radius-inflation  Corner radius larger than the object.
examples/sloppy-landing/Hero.tsx:12  high    hype-phrase       Sentence that could ship on any other product.
examples/sloppy-landing/Hero.tsx:14  medium  feature-trio      Three matching feature cards.
examples/sloppy-landing/Hero.tsx:15  medium  glass-panel       Glass panel.
examples/sloppy-landing/Hero.tsx:15  high    nested-card       Card nested inside a card.
examples/sloppy-landing/Hero.tsx:15  medium  radius-inflation  Corner radius larger than the object.
examples/sloppy-landing/Hero.tsx:15  medium  shadow-bloat      Heavy drop shadow.
examples/sloppy-landing/Hero.tsx:16  high    nested-card       Card nested inside a card.
examples/sloppy-landing/Hero.tsx:16  medium  radius-inflation  Corner radius larger than the object.
examples/sloppy-landing/Hero.tsx:17  medium  emoji-heading     Emoji sitting in a heading.
examples/sloppy-landing/Hero.tsx:18  medium  filler-copy       Placeholder copy still in the file.
examples/sloppy-landing/Hero.tsx:21  medium  glass-panel       Glass panel.
examples/sloppy-landing/Hero.tsx:21  high    nested-card       Card nested inside a card.
examples/sloppy-landing/Hero.tsx:21  medium  radius-inflation  Corner radius larger than the object.
examples/sloppy-landing/Hero.tsx:21  medium  shadow-bloat      Heavy drop shadow.
examples/sloppy-landing/Hero.tsx:22  medium  filler-copy       Placeholder copy still in the file.
examples/sloppy-landing/Hero.tsx:22  medium  emoji-heading     Emoji sitting in a heading.
examples/sloppy-landing/Hero.tsx:23  high    hype-phrase       Sentence that could ship on any other product.
examples/sloppy-landing/Hero.tsx:25  medium  glass-panel       Glass panel.
examples/sloppy-landing/Hero.tsx:25  high    nested-card       Card nested inside a card.
examples/sloppy-landing/Hero.tsx:25  medium  radius-inflation  Corner radius larger than the object.
examples/sloppy-landing/Hero.tsx:25  medium  shadow-bloat      Heavy drop shadow.
examples/sloppy-landing/Hero.tsx:26  medium  filler-copy       Placeholder copy still in the file.
examples/sloppy-landing/Hero.tsx:26  medium  emoji-heading     Emoji sitting in a heading.
examples/sloppy-landing/Hero.tsx:27  low     empty-cta         Call to action with no object.
examples/sloppy-landing/Hero.tsx:27  medium  violet-default    Indigo or violet used as the default accent.
examples/sloppy-landing/Pricing.vue:3  high    hype-phrase       Sentence that could ship on any other product.
examples/sloppy-landing/Pricing.vue:3  medium  emoji-heading     Emoji sitting in a heading.
examples/sloppy-landing/Pricing.vue:4  high    gray-on-gray      Neutral text on a nearby neutral.
examples/sloppy-landing/Pricing.vue:4  medium  radius-inflation  Corner radius larger than the object.
examples/sloppy-landing/Pricing.vue:4  medium  shadow-bloat      Heavy drop shadow.
examples/sloppy-landing/Pricing.vue:5  high    hype-phrase       Sentence that could ship on any other product.
examples/sloppy-landing/Pricing.vue:12  medium  stock-sans        Default sans, used as the actual face.
examples/sloppy-landing/index.html:6  high    hype-phrase       Sentence that could ship on any other product.
examples/sloppy-landing/index.html:7  medium  stock-sans        Default sans, used as the actual face.
examples/sloppy-landing/index.html:13  high    hype-phrase       Sentence that could ship on any other product.
examples/sloppy-landing/index.html:13  low     emoji-icon        Emoji standing in for an icon.
examples/sloppy-landing/index.html:14  high    hype-phrase       Sentence that could ship on any other product.
examples/sloppy-landing/index.html:14  medium  emoji-heading     Emoji sitting in a heading.
examples/sloppy-landing/index.html:16  high    hype-phrase       Sentence that could ship on any other product.
examples/sloppy-landing/index.html:19  low     empty-cta         Call to action with no object.
examples/sloppy-landing/index.html:20  low     empty-cta         Call to action with no object.
examples/sloppy-landing/index.html:23  medium  feature-trio      Three matching feature cards.
examples/sloppy-landing/index.html:25  high    nested-card       Card nested inside a card.
examples/sloppy-landing/index.html:26  medium  filler-copy       Placeholder copy still in the file.
examples/sloppy-landing/index.html:26  medium  emoji-heading     Emoji sitting in a heading.
examples/sloppy-landing/index.html:27  medium  filler-copy       Placeholder copy still in the file.
examples/sloppy-landing/index.html:31  medium  filler-copy       Placeholder copy still in the file.
examples/sloppy-landing/index.html:31  medium  emoji-heading     Emoji sitting in a heading.
examples/sloppy-landing/index.html:32  high    hype-phrase       Sentence that could ship on any other product.
examples/sloppy-landing/index.html:35  medium  filler-copy       Placeholder copy still in the file.
examples/sloppy-landing/index.html:35  medium  emoji-heading     Emoji sitting in a heading.
examples/sloppy-landing/index.html:36  high    hype-phrase       Sentence that could ship on any other product.
examples/sloppy-landing/styles.css:6  medium  stock-sans        Default sans, used as the actual face.
examples/sloppy-landing/styles.css:7  medium  center-gravity    Layout collapsed onto the center.
examples/sloppy-landing/styles.css:9  high    gray-on-gray      Neutral text on a nearby neutral.
examples/sloppy-landing/styles.css:19  medium  violet-default    Indigo or violet used as the default accent.
examples/sloppy-landing/styles.css:20  low     blur-orb          Decorative blur orb.
examples/sloppy-landing/styles.css:26  medium  center-gravity    Layout collapsed onto the center.
examples/sloppy-landing/styles.css:32  high    gradient-wash     Cool purple-to-blue gradient.
examples/sloppy-landing/styles.css:33  medium  radius-inflation  Corner radius larger than the object.
examples/sloppy-landing/styles.css:34  medium  shadow-bloat      Heavy drop shadow.
examples/sloppy-landing/styles.css:43  high    gradient-wash     Cool purple-to-blue gradient.
examples/sloppy-landing/styles.css:45  medium  gradient-text     Gradient clipped into a headline.
examples/sloppy-landing/styles.css:66  medium  violet-default    Indigo or violet used as the default accent.
examples/sloppy-landing/styles.css:86  medium  glass-panel       Glass panel.
examples/sloppy-landing/styles.css:88  medium  radius-inflation  Corner radius larger than the object.
examples/sloppy-landing/styles.css:89  medium  shadow-bloat      Heavy drop shadow.
examples/sloppy-landing/styles.css:95  high    gray-on-gray      Neutral text on a nearby neutral.

gate: not set
```

The quiet control, `tastelint scan examples/quiet-studio --fail-under 90 --quiet`:

```
tastelint 0.1.0
examples/quiet-studio  ·  2 files  ·  0 findings (0 high, 0 medium, 0 low)  ·  taste score 100/100

gate: 90  ·  pass
```

JSON and SARIF are the same report in another shape:

```bash
tastelint scan examples/sloppy-landing --format json
tastelint scan examples/sloppy-landing --format sarif -o tastelint.sarif
tastelint scan examples/sloppy-landing --verbose
```

A line can opt out with a comment. `tastelint-disable-next-line hype-phrase` applies to the next line. `tastelint-disable-line radius-inflation` applies to the line that contains it. `all` suppresses every rule.

## Taste score

High findings cost 12, medium 5, low 2, and each rule is capped at 12. Penalties inside one rule are applied largest-first until the cap. The score is 100 minus the sum, and it does not go below 0.

A file that trips `gradient-wash`, `hype-phrase`, and `empty-cta` once each scores 74. A second `gradient-wash` on the same rule does not lower it further. The page under `examples/sloppy-landing` trips every rule and scores 0. `examples/quiet-studio` scores 100.

`--fail-under 90` is a practical CI gate: one high finding fails it, and a clean page passes.

## Rules

| Rule | Severity | What it catches |
| --- | --- | --- |
| `gradient-wash` | high | Cool purple-to-blue gradient. |
| `stock-sans` | medium | Default sans, used as the actual face. |
| `emoji-heading` | medium | Emoji sitting in a heading. |
| `emoji-icon` | low | Emoji standing in for an icon. |
| `nested-card` | high | Card nested inside a card. |
| `radius-inflation` | medium | Corner radius larger than the object. |
| `shadow-bloat` | medium | Heavy drop shadow. |
| `hype-phrase` | high | Sentence that could ship on any other product. |
| `filler-copy` | medium | Placeholder copy still in the file. |
| `gray-on-gray` | high | Neutral text on a nearby neutral. |
| `center-gravity` | medium | Layout collapsed onto the center. |
| `glass-panel` | medium | Glass panel. |
| `feature-trio` | medium | Three matching feature cards. |
| `blur-orb` | low | Decorative blur orb. |
| `violet-default` | medium | Indigo or violet used as the default accent. |
| `gradient-text` | medium | Gradient clipped into a headline. |
| `empty-cta` | low | Call to action with no object. |

`tastelint rules` prints the same list with a one-line fix for each.

Scanned extensions: `.html`, `.htm`, `.css`, `.scss`, `.jsx`, `.tsx`, `.vue`, `.svelte`, `.js`, `.ts`, `.mdx`. `node_modules`, `dist`, build output, and hidden directories are skipped. The linter does not compute layout. A card is a class named `card`, or a node that combines a large radius with a shadow, border, or fill.

## CI

`.github/workflows/ci.yml` installs the package, runs pytest, scans the samples, and expects the sloppy page to fail a real gate.

```yaml
name: tastelint
on: [push, pull_request]
jobs:
  taste:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install -e .
      - run: tastelint scan examples/quiet-studio --fail-under 90
      - name: Generated pages have to clear the gate
        run: tastelint scan src --fail-under 90
```

Exit codes: `0` the score meets the gate (or no gate was set), `1` the score is below `--fail-under`, `2` the path or the arguments are wrong, `3` the review request failed, `4` review has no API key.

## Agent skill

The installed text tells the agent to run `tastelint scan <path> --fail-under 90` and to follow the Plain Surface Charter. It is not a copy of anyone else's skill file.

```bash
tastelint skill install --target claude   # .claude/skills/tastelint/SKILL.md
tastelint skill install --target cursor   # .cursor/rules/tastelint.mdc
tastelint skill install --target codex    # AGENTS.md, between tastelint markers
```

Run it again and the Codex section is replaced instead of duplicated. `--dest` writes into another project root.

## Review

`review` scans first. If the taste score is already 100 it stops. Otherwise it posts the score, the rule ids, and short snippets.

```bash
cp .env.example .env   # set ATMOROUTER_API_KEY
tastelint review examples/sloppy-landing
tastelint review examples/sloppy-landing --dry-run
```

`--dry-run` prints the prompt and does not open a socket. Point the same command at another OpenAI-compatible server:

```bash
tastelint review src \
  --base-url http://127.0.0.1:11434/v1 \
  --model llama3.2 \
  --api-key local
```

## Why AtmoRouter

Design critique is a small prompt you will run often, so the default host is a cheap AI API gateway rather than one vendor's full-price endpoint. AtmoRouter is an OpenRouter alternative: it serves 169 models through one OpenAI/Anthropic-compatible key, with pay per token billing at an avg 80% below official prices. tastelint only needs chat completions, and `--base-url`, `--model`, and `--api-key` retarget that call.

Default LLM provider: AtmoRouter (https://atmorouter.dev)

The default model is `atmo/deepseek-v4.1-flash`. Catalog ids change; override it when you want a different one.

## Configuration

Flags win, then `TASTELINT_*`, then the AtmoRouter variables, then `OPENAI_API_KEY` as a last-resort key. A `.env` file in the working directory fills only what is not already set.

| Variable | Default | Role |
| --- | --- | --- |
| `ATMOROUTER_API_KEY` | unset | Bearer key. The example value is `ar-your-key-here`. |
| `ATMOROUTER_BASE_URL` | `https://atmorouter.dev/v1` | OpenAI-compatible root. |
| `TASTELINT_BASE_URL` | unset | Overrides the base URL when set. |
| `TASTELINT_MODEL` | `atmo/deepseek-v4.1-flash` | Model id sent as `model`. |
| `TASTELINT_API_KEY` | unset | Overrides the bearer key when set. |
| `OPENAI_API_KEY` | unset | Used only when no AtmoRouter key is set. |

| Flag | Applies to | Role |
| --- | --- | --- |
| `--format` | scan | `text` (default), `json`, or `sarif`. |
| `--fail-under N` | scan, review | Exit 1 when the score is below N (0–100). |
| `--verbose` / `--quiet` | scan | Hints and source lines, or the summary only. |
| `-o FILE` | scan | Also write the report to a file. |
| `--base-url` `--model` `--api-key` | review | Endpoint overrides. |
| `--dry-run` | review | Build the prompt and skip the network. |
| `--timeout` | review | Socket timeout in seconds. Default 60. |

## Development

```bash
python -m pip install -e ".[dev]"
pytest
tastelint scan examples/quiet-studio --fail-under 90
```

Tests are offline. The review suite stubs the HTTP call and never dials out.

## License

Released under the MIT License. See [LICENSE](LICENSE).
