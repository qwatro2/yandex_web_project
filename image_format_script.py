from PIL import Image


def image_convert_script(filename: str) -> None:
    img = Image.open(f'./static/media/{filename}')
    w, h = img.size
    k = float(w) / float(h)
    if w > h:        
        img = img.resize((600, int(600 / k)), Image.ANTIALIAS)
    else:
        img = img.resize((int(600 * k), 600), Image.ANTIALIAS)
    img.save(f'./static/media/{filename}')  
