import re
import unicodedata

def lower_tr(text):
    return text.translate(str.maketrans({'I': 'ı', 'İ': 'i'})).lower()

def upper_first(text):
    return text[:1].translate(str.maketrans({'i': 'İ', 'ı': 'I'})).upper() + text[1:]

def normalize(text):
    # Preserve newlines, tabs, repeated spaces and all user-visible characters.
    return unicodedata.normalize('NFC', text.replace('\r\n', '\n').replace('\r', '\n'))

def canonical(text):
    return re.sub(r'[^a-zçğıöşü0-9]', '', lower_tr(normalize(text)))

def chunks(text, max_bytes=176):
    """Lossless partition: (part, is_layout). No truncation, even for long words."""
    result = []
    for line in re.split(r'(\n+)', text):
        if not line:
            continue
        if line.startswith('\n') or not line.strip():
            result.append((line, True))
            continue
        leading = line[:len(line) - len(line.lstrip())]
        if leading:
            result.append((leading, True))
            line = line[len(leading):]
        while line:
            n = 0
            used = 0
            for c in line:
                if used + len(c.encode('utf-8')) > max_bytes:
                    break
                used += len(c.encode('utf-8'))
                n += 1
            if n < len(line):
                boundary = line.rfind(' ', 0, n + 1)
                if boundary > n // 2:
                    n = boundary
            part, line = line[:n], line[n:]
            trailing = len(part) - len(part.rstrip())
            if trailing:
                result.extend([(part[:-trailing], False), (part[-trailing:], True)])
            else:
                result.append((part, False))
            whitespace = len(line) - len(line.lstrip(' \t'))
            if whitespace:
                result.append((line[:whitespace], True))
                line = line[whitespace:]
    return result
