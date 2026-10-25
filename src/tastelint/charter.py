"""The Plain Surface Charter.

This is the design stance tastelint installs into coding agents and hands to
the review model. The rule engine checks the part of it that can be checked
from source. The rest is judgment, which is what `tastelint review` is for.
"""

from __future__ import annotations

TITLE = "Plain Surface Charter"

PRINCIPLES = (
    (
        "Name the type.",
        "The first family is a choice you can defend. Inter, Roboto, Poppins, "
        "Nunito, Montserrat, Lato, Arial, and an untouched system stack are not choices.",
    ),
    (
        "Spend one pigment.",
        "Use it for the thing that should be touched or remembered. A gradient has to "
        "join two colors you would write in the brand notes. Violet drifting into blue is weather, not a brand.",
    ),
    (
        "Write a sentence that fails elsewhere.",
        "If the line still works after you swap the product name, it is not copy.",
    ),
    (
        "Center a line, not a page.",
        "Alignment is hierarchy. A stack of centered sections is a missing decision.",
    ),
    (
        "Get depth from the ground.",
        "Use contrast, overlap, or a change of surface. Do not nest cards, and do not "
        "pile blur, shadow, and a huge radius on the same box.",
    ),
    (
        "Keep type readable.",
        "Gray on a nearby gray is unfinished, not quiet. Body text needs real contrast.",
    ),
    (
        "Match the radius to the object.",
        "A pill is a control someone presses. A section is not a pebble.",
    ),
    (
        "Draw the icon or leave the space.",
        "An emoji in a heading is a placeholder you forgot to remove.",
    ),
    (
        "Scan before you call it done.",
        "Run tastelint on the files you touched. Fix high findings first. A taste score under 90 is not ready.",
    ),
)


def principles_markdown() -> str:
    lines = [f"# {TITLE}", ""]
    lines.append(
        "Generated interfaces converge. The gradient runs from violet to blue, the type "
        "is a default sans, the hero is centered, three cards sit under it, and the first "
        "sentence could be pasted onto a bank or a bakery. tastelint reads the source and "
        "names those moves so they can be replaced with decisions."
    )
    lines.append("")
    for index, (name, detail) in enumerate(PRINCIPLES, 1):
        lines.append(f"{index}. **{name}** {detail}")
    return "\n".join(lines)


def review_system_prompt() -> str:
    return (
        "You are the design editor inside tastelint. You receive a taste-score report "
        "and short source snippets from a generated interface. Answer in plain prose:\n"
        "1. One sentence on the single biggest reason the surface feels interchangeable.\n"
        "2. A numbered list of edits. Each edit names the file, the pattern, and a specific "
        "replacement (a color, a typeface, a layout change, or a rewritten sentence).\n"
        "3. One sentence on what the redesigned surface should feel like.\n\n"
        "Do not praise. Do not suggest a violet or indigo gradient, the Inter typeface, "
        "glassmorphism, emoji headings, or a row of three equal cards. Prefer subtraction.\n\n"
        + principles_markdown()
    )
