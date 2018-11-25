import cv2
import numpy as np
import qrcode
import sys, zipfile, os, shutil

#read the blank test sheet
template = cv2.imread("template.jpg")
#convert to grayscale
template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

#scaling constants
x_offset = 1580
y_offset = 230

def create_ljk(obj, path):
    global template
    global x_offset
    global y_offset
    sheet = template.copy()
    name = str(obj['id_siswa']) + '.' + str(obj['id_kelas']) + '.' + str(obj['id_mapel']) + '.' + str(obj['id_paket'])
    #make QR code
    qr_img = qrcode.make(name)
    qr_img = np.float32(qr_img)

    # put identity to sheet
    cv2.putText(sheet, obj['nama_siswa'], (590, 403), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 0), 3)
    cv2.putText(sheet, obj['kelas'], (590, 480), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 0), 3)
    cv2.putText(sheet, obj['mapel'], (590, 550), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 0), 3)
    cv2.putText(sheet, obj['kode_soal'], (590, 620), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 0), 3)

    #crop and resize QR code
    size = 560
    offset = 40
    qr_img = cv2.resize(qr_img, (size, size))
    qr_img = qr_img[offset:size-offset, offset:size-offset]

    #calculate coordinates where the QR code should be placed
    y1, y2 = y_offset, y_offset + qr_img.shape[0]
    x1, x2 = x_offset, x_offset + qr_img.shape[1]

    #place the QR code on the sheet
    sheet[y1:y2, x1:x2] = qr_img * 255
    
    #write the image file
    nama = obj['nama_siswa'].lower().replace(' ', '_')
    kode_soal = obj['kode_soal'].replace('.', '_')
    img_name = kode_soal + '_' + nama + ".png"
    # save ljk in directory
    cv2.imwrite(os.path.join( path, img_name) , sheet)
    # cv2.imshow('hasil', cv2.resize(sheet, (0,0), fx=0.3, fy=0.3) )
    # cv2.waitKey(0)

def build(data_siswa):
    path = data_siswa[0]['kode_soal'] + '-' + data_siswa[0]['kelas'].replace(' ', '')
    path_zip = path + '.zip'
    os.mkdir(path)

    for data in data_siswa:
        if len(data['nama_siswa']) > 25:
            nama = ''
            tmp = data['nama_siswa'].split(' ')
            for _ in tmp:
                if len(nama + _ ) <= 25:
                    nama += ' ' + _
            data['nama_siswa'] = nama
        create_ljk(data, path)
    


    ljk_zip = zipfile.ZipFile(path_zip, 'w')
    
    for folder, subfolders, files in os.walk(path):
        for file in files:
            if file.endswith('.png'):
                ljk_zip.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file), path), compress_type = zipfile.ZIP_DEFLATED)
    
    ljk_zip.close()
    shutil.rmtree(path)
    return path_zip

# build(data_siswa)