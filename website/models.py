from flask_login import UserMixin
from sqlalchemy.sql import func
from . import db

# Truk Pabrik
class Laporan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tgl_brgkt = db.Column(db.DateTime())
    tgl_kmbl = db.Column(db.DateTime())
    nopol = db.Column(db.String(100))
    sopir = db.Column(db.String(100))
    tujuan = db.Column(db.String(500))
    km_awal = db.Column(db.Integer)  # KM Berangkat
    km_isi = db.Column(db.Integer)  # KM Kembali
    solar_awal = db.Column(db.Float)
    e_toll = db.Column(db.Integer)
    keterangan = db.Column(db.String(500))
    satpam1 = db.Column(db.String(100))
    satpam2 = db.Column(db.String(100))
    img = db.relationship('ImageSet', backref='laporan',
                          lazy=True, uselist=True)
#
    def to_dict(self):
        return {
            'id': self.id,
            'tgl_brgkt': self.tgl_brgkt.strftime("%d-%m-%Y, %H:%M:%S"),
            'tgl_kmbl': self.tgl_kmbl.strftime("%d-%m-%Y, %H:%M:%S") if self.tgl_kmbl else '-',
            'nopol': self.nopol,
            'sopir': self.sopir,
            'km_awal': self.km_awal,
            'km_isi': self.km_isi,
            'rate': ('1:' + str("{:10.2f}".format((self.km_isi-self.km_awal)/self.solar_awal))) if self.solar_awal else '-',
        }

class ImageSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(150), nullable=False)
    laporan_id = db.Column(db.Integer, db.ForeignKey(
        'laporan.id'), nullable=False)

# Truk supplier
class Laporan_supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tgl_datang = db.Column(db.DateTime())
    tgl_pergi = db.Column(db.DateTime())
    nopol = db.Column(db.String(100))
    sopir = db.Column(db.String(100))
    supplier = db.Column(db.String(100))
    satpam1 = db.Column(db.String(100))
    satpam2 = db.Column(db.String(100))
    muatan = db.Column(db.String(500))
    keterangan = db.Column(db.String(500))
    img = db.relationship('ImageSet_supplier',
                          backref='Laporan_supplier', lazy=True, uselist=True)
#                          
    def to_dict(self):
        return {
            'id': self.id,
            'tgl_datang': self.tgl_datang.strftime("%d-%m-%Y, %H:%M:%S"),
            'tgl_pergi': self.tgl_pergi.strftime("%d-%m-%Y, %H:%M:%S") if self.tgl_pergi else '-',
            'nopol': self.nopol,
            'sopir': self.sopir,
            'supplier' : self.supplier,
        }

class ImageSet_supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(150), nullable=False)
    laporan_id = db.Column(db.Integer, db.ForeignKey(
        'laporan_supplier.id'), nullable=False)

# Truk Sewa
class Laporan_sewa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tgl_datang = db.Column(db.DateTime())
    tgl_pergi = db.Column(db.DateTime())
    tgl_kmbl = db.Column(db.DateTime())
    nopol = db.Column(db.String(100))
    sopir = db.Column(db.String(100))
    satpam1 = db.Column(db.String(100))
    satpam2 = db.Column(db.String(100))
    satpam3 = db.Column(db.String(100))
    ekspedisi = db.Column(db.String(500))
    muatan = db.Column(db.String(500))
    keterangan = db.Column(db.String(500))
    img = db.relationship(
        'ImageSet_sewa', backref='Laporan_sewa', lazy=True, uselist=True)

    def to_dict(self):
        return {
            'id': self.id,
            'tgl_datang': self.tgl_datang.strftime("%d-%m-%Y, %H:%M:%S"),
            'tgl_pergi': self.tgl_pergi.strftime("%d-%m-%Y, %H:%M:%S") if self.tgl_pergi else '-',
            'tgl_kmbl': self.tgl_kmbl.strftime("%d-%m-%Y, %H:%M:%S") if self.tgl_kmbl else '-',
            'nopol': self.nopol,
            'sopir': self.sopir,
            'ekspedisi': self.ekspedisi,
        }
#
class ImageSet_sewa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(150), nullable=False)
    laporan_id = db.Column(db.Integer, db.ForeignKey(
        'laporan_sewa.id'), nullable=False)

# User
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
