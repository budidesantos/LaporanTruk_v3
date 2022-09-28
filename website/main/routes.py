from flask import Blueprint, render_template, request, flash, url_for, redirect, abort, current_app
from flask_login import login_required, current_user

from sqlalchemy import desc

from ..models import Laporan, ImageSet
from .forms import FormBerangkat, FormKembali, LaporanAdmin
from .. import db

from PIL import Image
from datetime import datetime, timedelta

import os
import secrets

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == "POST":
        tgl_ats = request.form.get('atas')
        tgl_bwh = request.form.get('bawah')
        if tgl_ats and tgl_bwh:
            return render_template('/main/filter.html', user=current_user, 
            atas=datetime.strptime(tgl_ats,"%Y-%m-%d")+timedelta(days=1), bawah=tgl_bwh )
    return render_template('/main/index.html', user=current_user)

# API data table
@main.route('/api/data/pabrik')
def data():
    query = Laporan.query.order_by(desc(Laporan.id))

    #search filter
    search = request.args.get('search')
    if search:
        query = query.filter(db.or_(
            Laporan.nopol.like(f'%{search}%'),
            Laporan.sopir.like(f'%{search}%')
        ))
    total = query.count()

    #pagination
    start = request.args.get('start', type=int, default=-1)
    length = request.args.get('length', type=int, default=-1)
    if start != -1 and length != -1:
        query = query.offset(start).limit(length)

    #response
    return {
        'data': [laporan.to_dict() for laporan in query],
        'total' : total}

# API untuk data filter
@main.route('/api/data/pabrik/date_from/<atas>/date_to/<bawah>', methods=['GET', 'POST'])
def filtered_data(atas, bawah):
    query = Laporan.query.order_by(desc(Laporan.id)).filter(Laporan.tgl_brgkt<=atas, Laporan.tgl_brgkt>=bawah)
    
    #search filter
    search = request.args.get('search')
    if search:
        query = query.filter(db.or_(
            Laporan.nopol.like(f'%{search}%'),
            Laporan.sopir.like(f'%{search}%')
        ))
    total = query.count()

    #sorting
    sort = request.args.get('sort')
    if sort:
        order = []
        for s in sort.split(','):
            direction = s[0]
            name = s[1:]
            if name not in ['tgl_brgkt','nopol', 'sopir']:
                name = 'id'
            col = getattr(Laporan, name)
            if direction == '-':
                col = col.desc()
            order.append(col)
        if order:
            query = query.order_by(*order)
    
    #pagination
    start = request.args.get('start', type=int, default=-1)
    length = request.args.get('length', type=int, default=-1)
    if start != -1 and length != -1:
        query = query.offset(start).limit(length)

    #response
    return {
        'data': [laporan.to_dict() for laporan in query],
        'total' : total}

#detail laporan
@main.route('/pabrik/laporan/<int:id>')
def laporan(id):
    laporan =  Laporan.query.get_or_404(id)
    foto = []
    if ImageSet.query.filter(ImageSet.laporan_id==id):
        for list in ImageSet.query.filter(ImageSet.laporan_id==id):
            foto.append(url_for('static', filename='images/laporan_pabrik/' + list.image))

    return render_template('/main/laporan.html', user=current_user, laporan=laporan, img=foto)

# upload img
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/images/laporan_pabrik', picture_fn)
    output_size = (384, 216)
    
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

# tambah laporan berangkat
@main.route('/pabrik/add-berangkat', methods=['POST','GET'])
@login_required
def add_berangkat():
    form = FormBerangkat()
    if form.validate_on_submit():
        nopol = form.nopol.data.upper()
        sopir = form.sopir.data.upper()
        satpam1 = form.satpam1.data.upper()
        km_awal = form.km_awal.data
        tujuan = form.tujuan.data
        file_foto = form.foto.data
        
        cek_nopol = Laporan.query.order_by(desc(Laporan.id)).filter_by(nopol=nopol).first()
            
        if cek_nopol:
            if cek_nopol.tgl_kmbl==None:
                flash('Error! Nomor Polisi/Sopir belum kembali', category='error')          
            else:
                new_post = Laporan(tgl_brgkt=datetime.now().replace(microsecond=0), nopol=nopol, sopir=sopir, satpam1=satpam1, km_awal=km_awal, km_isi=0, solar_awal=0, e_toll=0, tujuan=tujuan)
                db.session.add(new_post)
                db.session.flush() #
                if file_foto:
                    foto = save_picture(file_foto)
                    new_foto = ImageSet(laporan_id=new_post.id, image= foto)
                    db.session.add(new_foto) #
                db.session.commit()
                return redirect(url_for('main.home'))
        else:
            new_post = Laporan(tgl_brgkt=datetime.now().replace(microsecond=0), nopol=nopol, sopir=sopir, satpam1=satpam1, km_awal=km_awal, km_isi=0, solar_awal=0, e_toll=0, tujuan=tujuan)
            db.session.add(new_post)
            db.session.flush() #
            if file_foto:
                foto = save_picture(file_foto)
                new_foto = ImageSet(laporan_id=new_post.id, image= foto)
                db.session.add(new_foto) #
            db.session.commit()
            return redirect(url_for('main.home'))
    return render_template("/main/add_brgkt.html", title="Tambah Laporan Truk Berangkat", form = form, user=current_user)

# tambah laporan kembali
@main.route('/pabrik/add-kembali', methods=['POST','GET'])
@login_required
def add_kembali():
    form = FormKembali()
    if form.validate_on_submit():
        nopol = form.nopol.data.upper()
        sopir = form.sopir.data.upper()
        satpam2 = form.satpam2.data.upper()
        km_isi = form.km_isi.data
        keterangan = form.keterangan.data
        file_foto = form.foto.data

        cek_nopol = Laporan.query.order_by(desc(Laporan.id)).filter_by(nopol=nopol).first()
        cek_sopir = Laporan.query.order_by(desc(Laporan.id)).filter_by(sopir=sopir).first()
        if cek_nopol and cek_sopir:
            laporan = Laporan.query.get_or_404(cek_nopol.id)
            if laporan.tgl_kmbl==None:
                laporan.satpam2 = satpam2
                laporan.tgl_kmbl = datetime.now().replace(microsecond=0)
                laporan.km_isi = km_isi
                laporan.keterangan = keterangan
                if file_foto:
                    foto = save_picture(file_foto)
                    new_foto = ImageSet(laporan_id=laporan.id, image= foto)
                    db.session.add(new_foto)
                db.session.commit()
                return redirect(url_for('main.home'))
            else:
                flash(f'Error! Truk {cek_nopol.nopol} telah kembali', category='error')
        else:
            flash('Error! Nopol/Nama Sopir tidak ada', category='error')
    return render_template("/main/add_kmbl.html", title="Tambah Laporan Truk Kembali", form = form, user=current_user)

@main.route('/pabrik/laporan/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_laporan(id):
    laporan = Laporan.query.get_or_404(id)
    form = LaporanAdmin()
    file_foto = form.foto.data
    if form.validate_on_submit():
        laporan.nopol = form.nopol.data.upper()
        laporan.sopir = form.sopir.data.upper()
        laporan.km_awal = form.km_awal.data
        laporan.km_isi = form.km_isi.data
        laporan.solar_awal = form.solar_awal.data
        laporan.e_toll = form.e_toll.data
        laporan.tujuan = form.tujuan.data
        laporan.keterangan = form.keterangan.data
        if file_foto:
            foto = save_picture(file_foto)
            new_foto = ImageSet(laporan_id=laporan.id, image= foto)
            db.session.add(new_foto)
        db.session.commit()
        flash('Data laporan berhasil diupdate!', 'success')
        return redirect(url_for('main.laporan', id=laporan.id))
    elif request.method == 'GET':
        form.nopol.data = laporan.nopol
        form.sopir.data = laporan.sopir
        form.km_awal.data = laporan.km_awal
        form.km_isi.data = laporan.km_isi
        form.solar_awal.data = laporan.solar_awal
        form.e_toll.data = laporan.e_toll
        form.tujuan.data = laporan.tujuan
        form.keterangan.data = laporan.keterangan
    return render_template('/main/add_admin.html', title="Update Laporan", form = form, user=current_user)

#hapus laporan
@main.route('/pabrik/laporan/<int:id>/delete', methods=['POST'])
@login_required
def delete_laporan(id):
    laporan = Laporan.query.get_or_404(id)
    if current_user.username!='admin':
        abort(403)
    if ImageSet.query.filter(ImageSet.laporan_id==id):
        for list in ImageSet.query.filter(ImageSet.laporan_id==id):
            os.remove(os.path.join(current_app.root_path, 'static/images/laporan_pabrik', list.image))
        ImageSet.query.filter(ImageSet.laporan_id==id).delete()
    db.session.delete(laporan)
    db.session.commit()
    flash('Laporan berhasil dihapus', 'success')
    return redirect(url_for('main.home'))

# list nopol
@main.route('/pabrik/nopol', methods=['GET'])
@login_required
def get_nopol_list():
    list_laporan = Laporan.query.order_by(desc(Laporan.nopol))
    list_nopol = []
    jum_list = []
    for list in list_laporan:
        if list.nopol in list_nopol:
            jum_list[list_nopol.index(list.nopol)] += 1
        else:
            list_nopol.append(list.nopol)
            jum_list.append(1)
    data = sorted(zip(jum_list, list_nopol), key = lambda x: (-x[0], x[1]))
    return render_template('/main/list_nopol.html', title="List Nomor Polisi",  data=data, user=current_user)

#list sopir
@main.route('/pabrik/sopir', methods=['GET'])
@login_required
def get_sopir_list():
    list_laporan = Laporan.query.order_by(desc(Laporan.sopir))
    list_sopir = []
    jum_list = []
    for list in list_laporan:
        if list.sopir in list_sopir:
            jum_list[list_sopir.index(list.sopir)] += 1
        else:
            list_sopir.append(list.sopir)
            jum_list.append(1)
    data = sorted(zip(jum_list, list_sopir), key = lambda x: (-x[0], x[1]))
    return render_template('/main/list_sopir.html', title="List Sopir",  data=data, user=current_user)
