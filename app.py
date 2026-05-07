from flask import Flask, render_template, request, redirect, url_for, Response, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import csv
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pendaftaran.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'kemnaker-bina-intala-2026'

db = SQLAlchemy(app)

# Database Models
class Peserta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    tempat_lahir = db.Column(db.String(100))
    tanggal_lahir = db.Column(db.String(20))
    jenis_kelamin = db.Column(db.String(10))
    nik = db.Column(db.String(16))
    alamat = db.Column(db.String(200))
    no_hp = db.Column(db.String(20))
    email = db.Column(db.String(100))
    jenis_jabatan = db.Column(db.String(50))
    pendidikan = db.Column(db.String(20))
    prodi = db.Column(db.String(100))
    tipe_lembaga = db.Column(db.String(50))
    nama_lembaga = db.Column(db.String(100))
    alamat_lembaga = db.Column(db.String(200))
    kota = db.Column(db.String(100))
    provinsi = db.Column(db.String(100))
    telp_lembaga = db.Column(db.String(20))
    email_lembaga = db.Column(db.String(100))
    tanggal_daftar = db.Column(db.DateTime, default=datetime.now)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()
    # Buat admin default kalau belum ada
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(
            username='admin',
            password=generate_password_hash('kemnaker2026')
        )
        db.session.add(admin)
        db.session.commit()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/daftar', methods=['POST'])
def daftar():
    peserta = Peserta(
        nama=request.form.get('nama'),
        tempat_lahir=request.form.get('tempat_lahir'),
        tanggal_lahir=request.form.get('tanggal_lahir'),
        jenis_kelamin=request.form.get('jenis_kelamin'),
        nik=request.form.get('nik'),
        alamat=request.form.get('alamat'),
        no_hp=request.form.get('no_hp'),
        email=request.form.get('email'),
        jenis_jabatan=request.form.get('jenis_jabatan'),
        pendidikan=request.form.get('pendidikan'),
        prodi=request.form.get('prodi'),
        tipe_lembaga=request.form.get('tipe_lembaga'),
        nama_lembaga=request.form.get('nama_lembaga'),
        alamat_lembaga=request.form.get('alamat_lembaga'),
        kota=request.form.get('kota'),
        provinsi=request.form.get('provinsi'),
        telp_lembaga=request.form.get('telp_lembaga'),
        email_lembaga=request.form.get('email_lembaga')
    )
    db.session.add(peserta)
    db.session.commit()
    return redirect(url_for('sukses'))

@app.route('/sukses')
def sukses():
    return render_template('sukses.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            return redirect(url_for('dashboard'))
        else:
            error = 'Username atau password salah!'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('admin_id', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    peserta = Peserta.query.order_by(Peserta.tanggal_daftar.desc()).all()
    total = Peserta.query.count()
    provinsi_count = db.session.query(Peserta.provinsi).distinct().count()
    lembaga_count = db.session.query(Peserta.nama_lembaga).distinct().count()
    return render_template('dashboard.html',
        peserta=peserta,
        total=total,
        provinsi_count=provinsi_count,
        lembaga_count=lembaga_count
    )

@app.route('/export')
@login_required
def export():
    peserta = Peserta.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['No', 'Nama', 'Tempat Lahir', 'Tanggal Lahir', 'Jenis Kelamin',
                     'NIK', 'Alamat', 'No HP', 'Email', 'Jabatan', 'Pendidikan',
                     'Prodi', 'Tipe Lembaga', 'Nama Lembaga', 'Alamat Lembaga',
                     'Kota', 'Provinsi', 'Telp Lembaga', 'Email Lembaga', 'Tanggal Daftar'])
    for i, p in enumerate(peserta, 1):
        writer.writerow([i, p.nama, p.tempat_lahir, p.tanggal_lahir, p.jenis_kelamin,
                         p.nik, p.alamat, p.no_hp, p.email, p.jenis_jabatan,
                         p.pendidikan, p.prodi, p.tipe_lembaga, p.nama_lembaga,
                         p.alamat_lembaga, p.kota, p.provinsi, p.telp_lembaga,
                         p.email_lembaga, p.tanggal_daftar.strftime('%d/%m/%Y')])
    output.seek(0)
    return Response(output, mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=data_peserta.csv"})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)