import re

RE_SPLI_LOGIC = re.compile(r'(?:[^\W_]+)|(?:[^ \r\n\t\xA0\u2003\u2009])') # Include nbsp thsp emsp
RE_ANY_LETTER = re.compile(r'[^\W_]')
RE_ONLY_WS = re.compile(r'^[ \r\n\t\u2003\u2009]*$')
RE_WHITESPACE = re.compile(r"[ \r\n\t\xA0\u2003\u2009]")
