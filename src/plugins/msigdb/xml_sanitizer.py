import re


ENTITY_REF_RE = re.compile(r"&(?:amp|lt|gt|apos|quot|#\d+|#x[0-9A-Fa-f]+);")
ATTRIBUTE_REPLACEMENTS = (
    ("<sup>", "&lt;sup&gt;"),
    ("</sup>", "&lt;/sup&gt;"),
    ("<sub>", "&lt;sub&gt;"),
    ("</sub>", "&lt;/sub&gt;"),
    ("<i>", "&lt;i&gt;"),
    ("</i>", "&lt;/i&gt;"),
    ("<b>", "&lt;b&gt;"),
    ("</b>", "&lt;/b&gt;"),
    ("<BR/>", "&lt;BR/&gt;"),
    ("<br/>", "&lt;br/&gt;"),
    (' "TRP-EGL" ', " &quot;TRP-EGL&quot; "),
    (' "Treg" ', " &quot;Treg&quot; "),
    ("</=", "&lt;/="),
    (">/=", "&gt;/="),
    ("<or", "&lt;or"),
    (">or", "&gt;or"),
    (" =< ", " =&lt; "),
    (" => ", " =&gt; "),
    ("(", "&#40;"),
    (")", "&#41;"),
)


def _apply_attribute_replacement_map(attr_value: str) -> str:
    for pattern, replacement in ATTRIBUTE_REPLACEMENTS:
        attr_value = attr_value.replace(pattern, replacement)
    return attr_value


def _escape_attribute_value(attr_value: str) -> str:
    out = []
    i = 0
    value_len = len(attr_value)

    while i < value_len:
        ch = attr_value[i]
        if ch == "&":
            entity_match = ENTITY_REF_RE.match(attr_value, i)
            if entity_match:
                out.append(entity_match.group(0))
                i = entity_match.end()
            else:
                out.append("&amp;")
                i += 1
            continue
        if ch == "<":
            out.append("&lt;")
        elif ch == ">":
            out.append("&gt;")
        elif ch == '"':
            out.append("&quot;")
        else:
            out.append(ch)
        i += 1

    return "".join(out)


def _sanitize_attribute_value(attr_value: str) -> str:
    return _escape_attribute_value(_apply_attribute_replacement_map(attr_value))


def _is_closing_attribute_quote(xml_text: str, start_index: int) -> bool:
    """Return True if the quote at start_index-1 ends an attribute value."""
    i = start_index
    text_len = len(xml_text)

    while i < text_len and xml_text[i].isspace():
        i += 1

    if i >= text_len:
        return True

    if xml_text[i] in {">", "/", "?"}:
        return True

    if not (xml_text[i].isalpha() or xml_text[i] in {"_", ":"}):
        return False

    i += 1
    while i < text_len and (xml_text[i].isalnum() or xml_text[i] in {"_", ":", "-", "."}):
        i += 1

    while i < text_len and xml_text[i].isspace():
        i += 1

    return i < text_len and xml_text[i] == "="


def sanitize_xml_attributes(xml_text: str) -> str:
    """Escape invalid XML characters found inside quoted attribute values."""
    out = []
    in_tag = False
    in_attr_value = False
    expect_attr_quote = False
    attr_buffer = []
    i = 0
    text_len = len(xml_text)

    while i < text_len:
        ch = xml_text[i]

        if not in_tag:
            if ch == "<":
                in_tag = True
            out.append(ch)
            i += 1
            continue

        if in_attr_value:
            if ch == '"':
                if _is_closing_attribute_quote(xml_text, i + 1):
                    out.append(_sanitize_attribute_value("".join(attr_buffer)))
                    attr_buffer = []
                    in_attr_value = False
                    out.append(ch)
                else:
                    attr_buffer.append(ch)
                i += 1
                continue

            attr_buffer.append(ch)
            i += 1
            continue

        if ch == ">":
            in_tag = False
            expect_attr_quote = False
            out.append(ch)
            i += 1
            continue

        if expect_attr_quote:
            if ch.isspace():
                out.append(ch)
            elif ch == '"':
                in_attr_value = True
                expect_attr_quote = False
                out.append(ch)
            else:
                expect_attr_quote = False
                out.append(ch)
            i += 1
            continue

        if ch == "=":
            expect_attr_quote = True

        out.append(ch)
        i += 1

    if attr_buffer:
        out.append(_sanitize_attribute_value("".join(attr_buffer)))

    return "".join(out)
