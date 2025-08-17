import regex
from typing import NamedTuple, List, Optional
from abc import ABC, abstractmethod

# Parser regexs
WORD_REGEX = regex.compile(r'(\S+)')
NEWLINE_REGEX = regex.compile(r'(?<=[^\\](?:\\\\)*)(\\n)')
JUMP_URL_REGEX = regex.compile(r'^https:\/\/discord\.com\/channels\/(?P<guild_id>@me|\d+)\/(?P<channel_id>\d+)(?:\/(?P<message_id>\d+))?$')


# Base class for Parser layers
class TextMessageParser(ABC):

    @abstractmethod
    def __call__(self, input_txt: str) -> str:
        pass


# Collection for storing registered Parser
PARSERS: dict[str, TextMessageParser] = dict()


def register_text_message_parser(name: str):
    def registering_function(parser: TextMessageParser) -> TextMessageParser:
        PARSERS[name] = parser()
        return parser
    return registering_function


@register_text_message_parser(
    name='newlines'
)
class NewlineParser(TextMessageParser):

    description = 'A parser that convertsany instance of \'\\n\' into a new line'

    def __call__(self, input_txt: str) -> str:
        return NEWLINE_REGEX.sub('\n', input_txt)


class Protomoji(NamedTuple):
    shortcode: str
    before_eyes: List[str] = []
    eyes: List[str] = [':', '=']
    before_nose: List[str] = []
    nose: List[str] = ['', '-']
    after_nose: List[str] = []
    mouth: List[str] = [')']


class Shortmoji(NamedTuple):
    shortcode: str
    patterns: List[str]


@register_text_message_parser(
    name='emoji'
)
class EmojiParser(TextMessageParser):

    description = 'A parser intended to match the convert emoticons function for a traditional Discord user.'

    protomoji_list = [
        Protomoji('slight_smile', mouth=[')']),
        Protomoji('frowning', mouth=['(']),
        Protomoji('smile', mouth=['D']),
        Protomoji('open_mouth', mouth=['O', 'o']),
        Protomoji('neutral_face', mouth=['|']),
        Protomoji('sob', eyes=[';'], mouth=['(']),
        Protomoji('cry', before_nose=[',', '\''], mouth=['(']),
        Protomoji('angry', before_eyes=['>'], mouth=['(']),
        Protomoji('stuck_out_tongue', mouth=['P']),
        Protomoji('sweat_smile', before_eyes=[','], mouth=[')']),
        Protomoji('smiling_face_with_tear', before_nose=[',', '\''], mouth=[')']),
        Protomoji('unamused', mouth=['$', 's', 'z']),
        Protomoji('rage', mouth=['@']),
        Protomoji('wink', eyes=[';'], mouth=[')']),
        Protomoji('joy', before_nose=['\'', ','], mouth=['D']),
        Protomoji('sweat', before_eyes=[','], mouth=['(']),
        Protomoji('kissing', mouth=['*']),
        Protomoji('blush', after_nose=['\''], mouth=[')']),
        Protomoji('innocent', before_eyes=['O', 'o'], mouth=[')']),
        Protomoji('imp', before_eyes=[']'], mouth=['(']),
        Protomoji('smiling_imp', before_eyes=[']'], mouth=[')']),
    ]

    shortmoji_list = [
        Shortmoji(':heart:', ['<3']),
        Shortmoji(':broken_heart:', ['</3']),
    ]

    non_functioning_patterns = [
        'O=)', 'o=)', 'O=-)', 'o=-)',
        ':-s', '=-s', ':-z', '=-z'
    ]

    def __init__(self):
        full_shortmoji_list = self.shortmoji_list + [self.inflate(p) for p in self.protomoji_list]

        self.patterns_dict: dict[str, str] = dict()
        # Populate the patterns dict with each patter and the shortcode
        for s in full_shortmoji_list:
            for p in s.patterns:
                self.patterns_dict[p] = s.shortcode
        # Remove the codes that don't work
        for nfp in self.non_functioning_patterns:
            del self.patterns_dict[nfp]

    def apply_options(self, roots: List[str], options: List[str]) -> List[str]:
        if options:
            return [r + o for o in options for r in roots]
        else:
            return roots

    def inflate(self, proto: Protomoji) -> Shortmoji:
        working = ['']
        for options in proto[1:]:
            working = self.apply_options(working, options)
        return Shortmoji(
            ':' + proto.shortcode + ':',
            working
        )

    def get_emoji(self, match: regex.Match) -> str:
        return self.patterns_dict.get(match.group(), match.group())

    def __call__(self, input_txt: str) -> str:
        return WORD_REGEX.sub(self.get_emoji, input_txt)


class JumpURLResponse(NamedTuple):
    guild_id: Optional[int]
    channel_id: int
    message_id: Optional[int]


def parse_jump_url(jump_url: str) -> JumpURLResponse:
    if match := JUMP_URL_REGEX.match(jump_url):
        return JumpURLResponse(
            None if match['guild_id'] == '@me' else match['guild_id'],
            match['channel_id'],
            match['message_id']
        )
    else:
        raise ValueError(f'failed to parse url: {jump_url}')
