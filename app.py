from flask import Flask, render_template, request, redirect, url_for, Response, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import csv
import io
import os

app = Flask(__name__)
database_url = os.environ.get('DATABASE_URL', 'sqlite:///pendaftaran.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'kemnaker-bina-intala-2026'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ajienata97@gmail.com'
app.config['MAIL_PASSWORD'] = 'xafjtoqpkmjpeaji'
app.config['MAIL_DEFAULT_SENDER'] = 'ajienata97@gmail.com'

mail = Mail(app)
db = SQLAlchemy(app)

class Pelatihan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(200), nullable=False)
    tanggal_mulai = db.Column(db.String(20))
    tanggal_selesai = db.Column(db.String(20))
    tipe = db.Column(db.String(20))
    kuota = db.Column(db.Integer)
    status = db.Column(db.String(20), default='aktif')
    tanggal_dibuat = db.Column(db.DateTime, default=datetime.now)

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
    pelatihan_id = db.Column(db.Integer, db.ForeignKey('pelatihan.id'))
    pelatihan = db.relationship('Pelatihan', backref='peserta')
    tanggal_daftar = db.Column(db.DateTime, default=datetime.now)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(
            username='admin',
            password=generate_password_hash('kemnaker2026')
        )
        db.session.add(admin)
        db.session.commit()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def home():
    daftar_pelatihan = Pelatihan.query.filter_by(status='aktif').all()
    return render_template('index.html', pelatihan=daftar_pelatihan)

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
        email_lembaga=request.form.get('email_lembaga'),
        pelatihan_id=request.form.get('pelatihan_id')
    )
    db.session.add(peserta)
    db.session.commit()

    try:
        msg = Message(
            subject='Konfirmasi Pendaftaran Pelatihan - Kemnaker',
            recipients=[peserta.email]
        )
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
            <div style="background-color: #1a3a6b; padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">Kementerian Ketenagakerjaan RI</h1>
                <p style="color: rgba(255,255,255,0.8);">Rektorat Bina Intala</p>
            </div>
            <div style="padding: 30px; background-color: #f9f9f9;">
                <h2 style="color: #1a3a6b;">Pendaftaran Berhasil! ✅</h2>
                <p>Yth. <strong>{peserta.nama}</strong>,</p>
                <p>Pendaftaran Anda telah kami terima dengan detail sebagai berikut:</p>
                <table style="width:100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background-color: #f0f4f8;">
                        <td style="padding: 10px; font-weight: bold;">Nama</td>
                        <td style="padding: 10px;">{peserta.nama}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; font-weight: bold;">Email</td>
                        <td style="padding: 10px;">{peserta.email}</td>
                    </tr>
                    <tr style="background-color: #f0f4f8;">
                        <td style="padding: 10px; font-weight: bold;">Lembaga</td>
                        <td style="padding: 10px;">{peserta.nama_lembaga}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; font-weight: bold;">Provinsi</td>
                        <td style="padding: 10px;">{peserta.provinsi}</td>
                    </tr>
                </table>
                <p>Panitia akan menghubungi Anda melalui email atau WhatsApp untuk informasi lebih lanjut.</p>
                <p>Terima kasih telah mendaftar!</p>
            </div>
            <div style="background-color: #1a3a6b; padding: 20px; text-align: center;">
                <p style="color: rgba(255,255,255,0.7); font-size: 12px; margin: 0;">
                    Rektorat Bina Intala - Kementerian Ketenagakerjaan RI
                </p>
            </div>
        </div>
        """
        mail.send(msg)
    except:
        pass

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
    daftar_pelatihan = Pelatihan.query.all()
    return render_template('dashboard.html',
        peserta=peserta,
        total=total,
        provinsi_count=provinsi_count,
        lembaga_count=lembaga_count,
        daftar_pelatihan=daftar_pelatihan
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

@app.route('/pelatihan')
@login_required
def pelatihan():
    daftar_pelatihan = Pelatihan.query.order_by(Pelatihan.tanggal_dibuat.desc()).all()
    return render_template('pelatihan.html', pelatihan=daftar_pelatihan)

@app.route('/pelatihan/tambah', methods=['GET', 'POST'])
@login_required
def tambah_pelatihan():
    if request.method == 'POST':
        p = Pelatihan(
            nama=request.form.get('nama'),
            tanggal_mulai=request.form.get('tanggal_mulai'),
            tanggal_selesai=request.form.get('tanggal_selesai'),
            tipe=request.form.get('tipe'),
            kuota=request.form.get('kuota'),
            status=request.form.get('status')
        )
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('pelatihan'))
    return render_template('tambah_pelatihan.html')

@app.route('/pelatihan/hapus/<int:id>')
@login_required
def hapus_pelatihan(id):
    p = Pelatihan.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('pelatihan'))

@app.route('/peserta/<int:id>')
@login_required
def detail_peserta(id):
    peserta = Peserta.query.get_or_404(id)
    return render_template('detail_peserta.html', peserta=peserta)

@app.route('/peserta/hapus/<int:id>')
@login_required
def hapus_peserta(id):
    peserta = Peserta.query.get_or_404(id)
    db.session.delete(peserta)
    db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)