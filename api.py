# import semua module yang dibutuhkan
from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, ForeignKey
from sqlalchemy.orm import relationship
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_jwt_extended import jwt_required, JWTManager, create_access_token, get_jwt_identity, get_jwt_claims, verify_jwt_in_request
from functools import wraps
from flask_cors import CORS
import sys
from run import grading

# pengaturan app
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:sipsalphatech123@sips-db.cedjkayreeam.ap-southeast-1.rds.amazonaws.com/sips_db'
app.config['SQLALCHEMY_ECHO']=True
app.config['JWT_SECRET_KEY'] = 'SFsieaaBsLEpecP675r243faM8oSB2hV'
api = Api(app)
jwt = JWTManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app,db)
manager = Manager(app)
manager.add_command('db',MigrateCommand)

# tabel guru
class Guru(db.Model):
    id_guru = db.Column(db.Integer, primary_key=True)
    nip = db.Column(db.Integer,unique=True,nullable=False)
    nama = db.Column(db.String(100),nullable=False)
    alamat = db.Column(db.String(1000),nullable=False)
    jenis_kelamin = db.Column(db.String(1),nullable=False)
    telepon = db.Column(db.String(15),nullable=False)

    def __repr__(self):
        return '<Guru %r>' %self.id_guru

# tabel mapel
class Mapel(db.Model):
    id_mapel = db.Column(db.Integer, primary_key=True)
    id_guru = db.Column(db.Integer,ForeignKey('guru.id_guru', ondelete='CASCADE'))
    nama_mapel = db.Column(db.String(100),nullable=False)
    jadwal = db.Column(db.DateTime,nullable=False)
    
    def __repr__(self):
        return '<Mapel %r>' %self.id_mapel

# tabel kelas
class Kelas(db.Model):
    id_kelas = db.Column(db.Integer, primary_key=True)
    nama_kelas = db.Column(db.String(100),nullable=False)
    wali_kelas = db.Column(db.String(100),nullable=False)
    
    def __repr__(self):
        return '<Mapel %r>' %self.id_kelas

# tabel kelas_mapel_conj
class KelasMapelConj(db.Model):
     id_kelas = db.Column(db.Integer,db.ForeignKey('kelas.id_kelas', ondelete="CASCADE"),nullable=False,primary_key=True)
     kelas = relationship("Kelas",uselist=False, back_populates="parents")
     id_mapel = db.Column(db.Integer, db.ForeignKey('mapel.id_mapel', ondelete="CASCADE"),nullable=False,primary_key=True)
     mapel = relationship("Mapel", uselist=False,back_populates="children")
    
# tabel siswa 
class Siswa(db.Model):
    id_siswa = db.Column(db.Integer, primary_key=True)
    id_kelas = db.Column(db.Integer,ForeignKey('kelas.id_kelas', ondelete='CASCADE'))
    nis = db.Column(db.Integer,unique=True,nullable=False)
    nama = db.Column(db.String(100),nullable=False)
    alamat = db.Column(db.String(1000),nullable=False)
    jenis_kelamin = db.Column(db.String(1),nullable=False)
    telepon = db.Column(db.String(15),nullable=False)
    

    def __repr__(self):
        return '<Siswa %r>' %self.id_siswa

# tabel paket_soal 
class PaketSoal(db.Model):
    id_paket_soal = db.Column(db.Integer, primary_key=True)
    id_mapel = db.Column(db.Integer,ForeignKey('mapel.id_mapel', ondelete='CASCADE'))
    kode_soal = db.Column(db.String(100),nullable=False)   
    tanggal_ujian = db.Column(db.DateTime,nullable=False)
    
    def __repr__(self):
        return '<Paket_Soal %r>' %self.id_paket_soal

# tabel soal 
class Soal(db.Model):
    id_soal = db.Column(db.Integer, primary_key=True)
    id_paket_soal = db.Column(db.Integer,ForeignKey('paket_soal.id_paket_soal', ondelete='CASCADE'))
    narasi = db.Column(db.String(255),nullable=False)   
    option_A = db.Column(db.String(255),nullable=False) 
    option_B = db.Column(db.String(255),nullable=False) 
    option_C = db.Column(db.String(255),nullable=False) 
    option_D = db.Column(db.String(255),nullable=False) 
    option_E = db.Column(db.String(255),nullable=False)
    jawaban = db.Column(db.String(1),nullable=False) 
    no_soal = db.Column(db.Integer,nullable=False)  
    
    def __repr__(self):
        return '<Soal %r>' %self.id_soal

# tabel jawaban_ujian
class JawabanUjian(db.Model):
    id_jawaban_ujian = db.Column(db.Integer, primary_key=True)
    id_siswa = db.Column(db.Integer,db.ForeignKey('siswa.id_siswa', ondelete="CASCADE"),nullable=False)
    siswa = relationship("Siswa",uselist=False, back_populates="parents")
    id_paket_soal = db.Column(db.Integer, db.ForeignKey('paket_soal.id_paket_soal', ondelete="CASCADE"),nullable=False)
    paket_soal = relationship("Paket_Soal", uselist=False,back_populates="children")
    no_soal = db.Column(db.Integer,nullable=False)
    jawaban_siswa = db.Column(db.String(1),nullable=False)
    score_siswa = db.Column(db.Integer,nullable=False)
    
# tabel scoring
class Scoring(db.Model):
    id_scoring = db.Column(db.Integer, primary_key=True)
    id_siswa = db.Column(db.Integer,db.ForeignKey('siswa.id_siswa', ondelete="CASCADE"),nullable=False)
    siswa = relationship("Siswa",uselist=False, back_populates="parents")
    id_paket_soal = db.Column(db.Integer, db.ForeignKey('paket_soal.id_paket_soal', ondelete="CASCADE"),nullable=False)
    paket_soal = relationship("Paket_Soal", uselist=False,back_populates="children")
    nilai = db.Column(db.Integer,nullable=False)
    

class CameraResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("dataUri", type= str, help= 'judul key must be an string and exist', location= 'json', required= True)
        args = parser.parse_args()
        grading(args['dataUri'])
        print("yey")
        return {"data": args['dataUri']}, 200


api.add_resource(CameraResource, '/camera')

if __name__=='__main__':
    try:
        if sys.argv[1]=='db':
            manager.run()
        else:
            app.run(debug=True,host='0.0.0.0',port=5000)
    except IndexError as p:
        app.run(debug=True,host='0.0.0.0',port=5000)