import cv2
import numpy as np
import qrcode

#read the blank test sheet
sheet = cv2.imread("test_sheet.png")

#convert to grayscale
sheet = cv2.cvtColor(sheet, cv2.COLOR_BGR2GRAY)

#scaling constants
x_offset = 330
y_offset = 10

name = "kobar"

#make QR code
qr_img = qrcode.make(name)
qr_img = np.float32(qr_img)

#crop and resize QR code
qr_img = cv2.resize(qr_img, (170, 170))
qr_img = qr_img[20:150, 20:150]

#calculate coordinates where the QR code should be placed
y1, y2 = y_offset, y_offset + qr_img.shape[0]
x1, x2 = x_offset, x_offset + qr_img.shape[1]

#place the QR code on the sheet
sheet[y1:y2, x1:x2] = qr_img * 255

#write the image file
cv2.imwrite(name + ".png", sheet)
# cv2.imshow('hasil', cv2.resize(sheet, (0,0), fx=0.5, fy=0.5) )
cv2.waitKey(0)