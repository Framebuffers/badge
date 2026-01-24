import textwrap

def _text_justify(s: str, width: int = 64) -> None:
    lines = s.splitlines()
    result = []
    for l in lines:
        if len(l) < width:
            result.append(l)
        else:
            breaks = textwrap.wrap( l, width, replace_whitespace=False, break_long_words=True, break_on_hyphens=False )
            for b in breaks[:-1]:
                if len(b) == width:
                    result.append(b)
                    continue
                insert = width-len(b)
                words = b.split()
                every = insert // (len(words)-1) + 1
                extra = insert % (len(words)-1)
                for i in range(extra):
                    words[i] += ' '
                result.append( (' '*every).join(words) )
            result.append( breaks[-1] )
    return result