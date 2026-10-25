"""Decode the actual QR pixels from the source image and rendered PDF cover."""
import fitz,zxingcpp
from PIL import Image
from common import *
image=zxingcpp.read_barcode(Image.open(ROOT/'assets/site-qr.png'))
doc=fitz.open(ROOT/'docs/urfu-design-project.pdf');pix=doc[0].get_pixmap(matrix=fitz.Matrix(2,2));cover=zxingcpp.read_barcode(Image.frombytes('RGB',[pix.width,pix.height],pix.samples))
result={'asset':image.text if image else None,'pdf_cover':cover.text if cover else None}
result['passed']=result['asset']==result['pdf_cover']==PUBLIC
save('17-qr',result)
