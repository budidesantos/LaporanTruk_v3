from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, IntegerField, TextAreaField, DecimalField, DateField # , FieldList, FormField, HiddenField
from wtforms.validators import DataRequired

# Form untuk Laporan Datang
class FormDatang(FlaskForm):
    nopol = StringField('Nomor Polisi', validators=[DataRequired()])
    sopir = StringField('Nama Sopir', validators=[DataRequired()])
    supplier = StringField('Supplier', validators=[DataRequired()])
    satpam1 = StringField('Nama Satpam', validators=[DataRequired()])
    muatan = TextAreaField('Muatan')
    foto = FileField('Tambahkan Foto', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Submit')

# Form untuk Laporan Pergi
class FormPergi(FlaskForm):
    nopol = StringField('Nomor Polisi', validators=[DataRequired()])
    sopir = StringField('Nama Sopir', validators=[DataRequired()])
    satpam2 = StringField('Nama Satpam', validators=[DataRequired()])
    keterangan = TextAreaField('Keterangan')
    foto = FileField('Tambahkan Foto', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Submit')

# Form edit
class LaporanAdmin(FlaskForm):
    nopol = StringField('Nomor Polisi', validators=[DataRequired()])
    sopir = StringField('Nama Sopir', validators=[DataRequired()])
    supplier = StringField('Supplier', validators=[DataRequired()])
    muatan = TextAreaField('Muatan')
    keterangan = TextAreaField('Keterangan')
    foto = FileField('Tambahkan Foto', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Submit')
