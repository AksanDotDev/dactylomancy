from typing import NamedTuple, List
import regex


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


protomoji_list = [
    Protomoji("slight_smile", mouth=[")"]),
    Protomoji("frowning", mouth=["("]),
    Protomoji("smile", mouth=["D"]),
    Protomoji("open_mouth", mouth=["O", "o"]),
    Protomoji("neutral_face", mouth=["|"]),
    Protomoji("sob", eyes=[";"], mouth=["("]),
    Protomoji("cry", before_nose=[",", "'"], mouth=["("]),
    Protomoji("angry", before_eyes=[">"], mouth=["("]),
    Protomoji("stuck_out_tongue", mouth=["P"]),
    Protomoji("sweat_smile", before_eyes=[","], mouth=[")"]),
    Protomoji("smiling_face_with_tear", before_nose=[",", "'"], mouth=[")"]),
    Protomoji("unamused", mouth=["$", "s", "z"]),
    Protomoji("rage", mouth=["@"]),
    Protomoji("wink", eyes=[";"], mouth=[")"]),
    Protomoji("joy", before_nose=["'", ","], mouth=["D"]),
    Protomoji("sweat", before_eyes=[","], mouth=["("]),
    Protomoji("kissing", mouth=["*"]),
    Protomoji("blush", after_nose=["\""], mouth=[")"]),
    Protomoji("innocent", before_eyes=["O", "o"], mouth=[")"]),
    Protomoji("imp", before_eyes=["]"], mouth=["("]),
    Protomoji("smiling_imp", before_eyes=["]"], mouth=[")"]),
]

shortmoji_list = [
    Shortmoji(":heart:", ["<3"]),
    Shortmoji(":broken_heart:", ["</3"]),
]

non_functioning_patterns = [
    "O=)", "o=)", "O=-)", "o=-)",
    ":-s", "=-s", ":-z", "=-z"
]


full_shortmoji_list = shortmoji_list + [inflate(p) for p in protomoji_list]

patterns_dict = dict()
# Populate the patterns dict with each patter and the shortcode
for s in full_shortmoji_list:
    for p in s.patterns:
        patterns_dict[p] = s.shortcode
# Remove the codes that don't work
for nfp in non_functioning_patterns:
    del patterns_dict[nfp]

word_regex = regex.compile(r"(\S+)")


def get_emoji(pattern: regex.Match) -> str:
    return patterns_dict.get(pattern.group(), pattern.group())


def emojify(body: str) -> str:
    return word_regex.sub(get_emoji, body)
