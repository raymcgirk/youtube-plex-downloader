def sanitize_filename(title):
    title = title.replace("?", "？")
    title = title.replace("/", "⧸")
    title = title.replace('"', '＂')
    title = title.replace(":", "：")
    title = title.replace("|", "｜")
    return title.strip()
