from typing import NamedTuple, List


class Protomoji(NamedTuple):
    shortcode: str
    before_eyes: List[str] = []
    eyes: List[str] = [":", "="]
    before_nose: List[str] = []
    nose: List[str] = ["", "-"]
    after_nose: List[str] = []
    mouth: List[str] = [")"]


class Shortmoji(NamedTuple):
    shortcode: str
    patterns: List[str]


def apply_options(roots: List[str], options: List[str]) -> List[str]:
    if options:
        return [r + o for o in options for r in roots]   
    else:
        return roots


def inflate(proto: Protomoji) -> Shortmoji:
    working = [""]
    for options in proto[1:]:
        working = apply_options(working, options)
    return Shortmoji(
        ":" + proto.shortcode + ":",
        working
    )


shortmoji_set = {
    Shortmoji(":heart", ["<3"]),
    Shortmoji(":broken_heart", ["</3"]),
    Shortmoji(":heart", ["<3"]),
}
