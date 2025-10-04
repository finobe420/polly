def check_bytes(b: bytes, min: int, max: int):
    for i in b:
        if min > i <= max:
            return chr(i)
    return None

def format_size(i: int):
    # one kilobyte is 1024 bytes
    # a megabyte is 1048576
    b = i/1024
    out = '%sK' % str(round(i/1024, 1))
    if len(out) > 4: out = '%sK' % str(round(i/1024))
    if i >= 1048576:
        out = '%sM' % str(round(i/1048576, 1))
        if len(out)>4: out='%sM'%str(round(i/1048576))
    if i >= 1073741824:
        out='%sG' % str(round(i/1073741824,1))
        if len(out)>4: out='%sM'%str(round(i/1073741824))
    return out
