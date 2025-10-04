def find_type(ext):
    match ext:
        case '.txt': return '0'
        case '.uu': return '6'
        case '.gif': return 'g'
        case '.bmp': return 'I'
        case '.jpg': return 'I'
        case '.jpeg': return 'I'
        case _: return '9'