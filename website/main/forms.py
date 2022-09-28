from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, IntegerField, TextAreaField, DecimalField, DateField # , FieldList, FormField, HiddenField
from wtforms.validators import DataRequired

# Form untuk Laporan Berangkat(add & update)
class FormBerangkat(FlaskForm):
    nopol = StringField('Nomor Polisi', validators=[DataRequired()])
    sopir = StringField('Nama Sopir', validators=[DataRequired()])
    satpam1 = StringField('Nama Satpam', validators=[DataRequired()])
    km_awal = IntegerField('KM Berangkat', validators=[DataRequired()])
    tujuan = TextAreaField('Tujuan')
    foto = FileField('Tambahkan Foto', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Submit')

# Form untuk Laporan Kembali(add & update)
class FormKembali(FlaskForm):
    nopol = StringField('Nomor Polisi', validators=[DataRequired()])
    sopir = StringField('Nama Sopir', validators=[DataRequired()])
    satpam2 = StringField('Nama Satpam', validators=[DataRequired()])
    km_isi = IntegerField('KM Kembali', validators=[DataRequired()])
    keterangan = TextAreaField('Keterangan')
    foto = FileField('Tambahkan Foto', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Submit')

# Form edit
class LaporanAdmin(FlaskForm):
    nopol = StringField('Nomor Polisi', validators=[DataRequired()])
    sopir = StringField('Nama Sopir', validators=[DataRequired()])
    km_awal = IntegerField('KM Berangkat', validators=[DataRequired()])
    km_isi = IntegerField('KM Kembali')
    solar_awal = DecimalField('Solar Awal (L)')
    e_toll = IntegerField('E-Toll')
    tujuan = TextAreaField('Tujuan')
    keterangan = TextAreaField('Keterangan')
    foto = FileField('Tambahkan Foto', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Submit')
