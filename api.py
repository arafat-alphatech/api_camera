# import semua module yang dibutuhkan
from flask import Flask, jsonify, request, send_file
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, ForeignKey
from sqlalchemy.orm import relationship
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_jwt_extended import jwt_required, JWTManager, create_access_token, get_jwt_identity, get_jwt_claims, verify_jwt_in_request
from functools import wraps
from flask_cors import CORS
import sys, zipfile, os, shutil
from run import grading
from create_test_sheets import build

import ssl
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)	
context.load_cert_chain('server.crt', 'server.key')

# from OpenSSL import SSL
# context = SSL.Context(SSL.SSLv23_METHOD)
# context.use_privatekey_file('server.key')
# context.use_certificate_file('server.crt')

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
	def get(self):
		return {"score": 'score', "codes": 'codes'}, 200
		
		data_siswa = [
			{
			'id_paket': 1,
			'kode_soal': '8.BIND.23.11',
			'mapel': 'Bahasa Indonesia',
			'id_kelas': 1,
			'kelas': 'VIII - 3',
			'id_siswa': 1,
			'nama_siswa': 'Much. Arafat A. M.',
			'id_mapel': 1
			},{
			'id_siswa': 2,
			'id_kelas': 1,
			'id_mapel': 1,
			'id_paket': 1,
			'nama_siswa': 'Hasan Mubarok',
			'kelas': 'VIII - 3',
			'mapel': 'Bahasa Indonesia',
			'kode_soal': '8.BIND.23.11'
			}
		]
		path_zip = build(data_siswa)
		# new_path = os.path.join(current_app.root_path, path_zip)
		return send_file(path_zip, as_attachment=True)
		# return {"message": new_path}, 200

	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument("dataUri", type= str, help= 'dataUri must be string and exist', location= 'json', required= True)
		args = parser.parse_args()
		answers, codes= grading(args['dataUri'])
		correct = 0
		kunci_jawaban = "ABCDEDCBABCDEDCBABCDEDCBAABCDEDCBABCDEDCBABCDEDCBA"
		for index, answer in enumerate(answers):
			if answer == kunci_jawaban[index]:
				correct += 1
		print(answers)
		score = correct / len(answers) * 100

		return {"score": score, "codes": codes}, 200


api.add_resource(CameraResource, '/camera')

if __name__=='__main__':
	try:
		if sys.argv[1]=='db':
			manager.run()
		else:
			app.run(debug=True,host='0.0.0.0',port=5001)
	except IndexError as p:
		# app.run(debug=True,host='0.0.0.0', port=5001)
		app.run(debug=True,host='0.0.0.0', port=5001, ssl_context=context)