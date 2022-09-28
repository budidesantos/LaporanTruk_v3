from flask import Blueprint, render_template, request, flash, url_for, redirect, abort, current_app
from flask_login import login_required, current_user

from sqlalchemy import desc

from ..models import Laporan_sewa, ImageSet_sewa
from .forms import FormDatang, FormPergi, FormKembali, LaporanAdmin
from .. import db

from PIL import Image
from datetime import datetime, timedelta

import os
import secrets

sewa = Blueprint('sewa', __name__)

@sewa.route('/sewa', methods=['GET', 'POST'])
@login_required
def sewaa():
    if request.method == "POST":
        tgl_ats = request.form.get('atas')
        tgl_bwh = request.form.get('bawah')
        if tgl_ats and tgl_bwh:
            return render_template('/sewa/filter.html', user=current_user, 
            atas=tgl_ats, bawah=tgl_bwh) # datetime.strptime(tgl_ats,"%Y-%m-%d")+timedelta(days=1)
    return render_template('/sewa/index.html', user=current_user)

# API data table
@sewa.route('/api/data/sewa')
def data():
    query = Laporan_sewa.query.order_by(desc(Laporan_sewa.id))

    #search filter
    search = request.args.get('search')
    if search:
        query = query.filter(db.or_(
            Laporan_sewa.nopol.like(f'%{search}%'),
            Laporan_sewa.sopir.like(f'%{search}%')
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
@sewa.route('/api/data/sewa/date_from/<atas>/date_to/<bawah>', methods=['GET', 'POST'])
def filtered_data(atas, bawah):
    query = Laporan_sewa.query.order_by(desc(Laporan_sewa.id)).filter(Laporan_sewa.tgl_datang<=atas,
     Laporan_sewa.tgl_datang>=bawah)
    
    #search filter  
    search = request.args.get('search')
    if search:
        query = query.filter(db.or_(
            Laporan_sewa.nopol.like(f'%{search}%'),
            Laporan_sewa.sopir.like(f'%{search}%'),
            Laporan_sewa.ekspedisi.like(f'%{search}%')
        ))
    total = query.count()

    #sorting
    sort = request.args.get('sort')
    if sort:
        order = []
        for s in sort.split(','):
            direction = s[0]
            name = s[1:]
            if name not in ['tgl_datang','nopol', 'sopir', 'ekspedisi']:
                name = 'id'
            col = getattr(Laporan_sewa, name)
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
@sewa.route('/sewa/laporan/<int:id>')
def laporan(id):
    laporan =  Laporan_sewa.query.get_or_404(id)
    foto = []
    if ImageSet_sewa.query.filter(ImageSet_sewa.laporan_id==id):
        for list in ImageSet_sewa.query.filter(ImageSet_sewa.laporan_id==id):
            foto.append(url_for('static', filename='images/laporan_sewa/' + list.image))

    return render_template('/sewa/laporan.html', user=current_user, laporan=laporan, img=foto)

# upload img
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/images/laporan_sewa', picture_fn)
    output_size = (384, 216)
    
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

# Add Laporan Datang
@sewa.route('/sewa/add-datang', methods=['POST','GET'])
@login_required
def add_datang():
    form = FormDatang()
    if form.validate_on_submit():
        nopol = form.nopol.data.upper()
        sopir = form.sopir.data.upper()
        satpam1 = form.satpam1.data.upper()
        file_foto = form.foto.data
        
        cek_nopol = Laporan_sewa.query.order_by(desc(Laporan_sewa.id)).filter_by(nopol=nopol).first()
            
        if cek_nopol:
            laporan = Laporan_sewa.query.get_or_404(cek_nopol.id)
            if laporan.tgl_pergi==None:
                flash('Error! Nomor Polisi/Sopir sudah di lokasi', category='error')
            elif not laporan.tgl_kmbl==None:
                flash('Error! Nomor Polisi/Sopir sudah di lokasi', category='error')          
            else:
                new_post = Laporan_sewa(tgl_datang=datetime.now().replace(microsecond=0), 
                nopol=nopol, sopir=sopir, satpam1=satpam1)
                db.session.add(new_post)
                db.session.flush() #
                if file_foto:
                    foto = save_picture(file_foto)
                    new_foto = ImageSet_sewa(laporan_id=new_post.id, image= foto)
                    db.session.add(new_foto) #
                db.session.commit()
                return redirect(url_for('sewa.sewaa'))
        else:
            new_post = Laporan_sewa(tgl_datang=datetime.now().replace(microsecond=0), 
                nopol=nopol, sopir=sopir, satpam1=satpam1)
            db.session.add(new_post)
            db.session.flush() #
            if file_foto:
                foto = save_picture(file_foto)
                new_foto = ImageSet_sewa(laporan_id=new_post.id, image= foto)
                db.session.add(new_foto) #
            db.session.commit()
            return redirect(url_for('sewa.sewaa'))
    return render_template("/sewa/add_datang.html", title="Tambah Laporan Truk Sewa Datang", form = form, user=current_user)

# add Laporan Pergi
@sewa.route('/sewa/add-pergi', methods=['POST','GET'])
@login_required
def add_pergi():
    form = FormPergi()
    if form.validate_on_submit():
        nopol = form.nopol.data.upper()
        sopir = form.sopir.data.upper()
        satpam2 = form.satpam2.data.upper()
        ekspedisi = form.ekspedisi.data
        muatan = form.muatan.data
        keterangan = form.keterangan.data
        file_foto = form.foto.data

        cek_nopol = Laporan_sewa.query.order_by(desc(Laporan_sewa.id)).filter_by(nopol=nopol).first()
        cek_sopir = Laporan_sewa.query.order_by(desc(Laporan_sewa.id)).filter_by(sopir=sopir).first()
        if cek_nopol and cek_sopir:
            laporan = Laporan_sewa.query.get_or_404(cek_nopol.id)
            if laporan.tgl_pergi==None:
                laporan.satpam2 = satpam2
                laporan.tgl_pergi = datetime.now().replace(microsecond=0)
                laporan.ekspedisi = ekspedisi
                laporan.muatan = muatan
                laporan.keterangan = keterangan
                if file_foto:
                    foto = save_picture(file_foto)
                    new_foto = ImageSet_sewa(laporan_id=laporan.id, image= foto)
                    db.session.add(new_foto)
                db.session.commit()
                return redirect(url_for('sewa.sewaa'))
            else:
                flash(f'Error! Truk {cek_nopol.nopol} sudah pergi', category='error')
        else:
            flash('Error! Nopol/Nama Sopir tidak ada', category='error')
    return render_template("/sewa/add_pergi.html", title="Tambah Laporan Truk Sewa Pergi", 
        form = form, user=current_user)

# add Laporan Kembali
@sewa.route('/sewa/add-kembali', methods=['POST','GET'])
@login_required
def add_kembali():
    form = FormKembali()
    if form.validate_on_submit():
        nopol = form.nopol.data.upper()
        sopir = form.sopir.data.upper()
        satpam3 = form.satpam3.data.upper()
        file_foto = form.foto.data

        cek_nopol = Laporan_sewa.query.order_by(desc(Laporan_sewa.id)).filter_by(nopol=nopol).first()
        cek_sopir = Laporan_sewa.query.order_by(desc(Laporan_sewa.id)).filter_by(sopir=sopir).first()
        if cek_nopol and cek_sopir:
            laporan = Laporan_sewa.query.get_or_404(cek_nopol.id)
            if laporan.tgl_pergi:
                if laporan.tgl_kmbl==None:
                    laporan.satpam3 = satpam3
                    laporan.tgl_kmbl = datetime.now().replace(microsecond=0)
                    if file_foto:
                        foto = save_picture(file_foto)
                        new_foto = ImageSet_sewa(laporan_id=laporan.id, image= foto)
                        db.session.add(new_foto)
                    db.session.commit()
                    return redirect(url_for('sewa.sewaa'))
                else:
                    flash(f'Error! Truk {cek_nopol.nopol} sudah kembali', category='error')
            else:
                flash('Error! nopol belum berangkat', category='error')
        else:
            flash('Error! Nopol/Nama Sopir tidak ada', category='error')
    return render_template("/sewa/add_kembali.html", title="Tambah Laporan Truk Sewa Kembali", 
        form = form, user=current_user)

# Update
@sewa.route('/sewa/laporan/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_laporan(id):
    laporan = Laporan_sewa.query.get_or_404(id)
    form = LaporanAdmin()
    if form.validate_on_submit():
        laporan.nopol = form.nopol.data.upper()
        laporan.sopir = form.sopir.data.upper()
        laporan.ekspedisi = form.ekspedisi.data
        laporan.muatan = form.muatan.data
        laporan.keterangan = form.keterangan.data
        file_foto = form.foto.data
        if file_foto:
            foto = save_picture(file_foto)
            new_foto = ImageSet_sewa(laporan_id=laporan.id, image= foto)
            db.session.add(new_foto)
        db.session.commit()
        flash('Data laporan berhasil diupdate!', 'success')
        return redirect(url_for('sewa.laporan', id=laporan.id))
    elif request.method == 'GET':
        form.nopol.data = laporan.nopol
        form.sopir.data = laporan.sopir
        form.ekspedisi.data = laporan.ekspedisi
        form.muatan.data = laporan.muatan
        form.keterangan.data = laporan.keterangan
    return render_template('/sewa/add_admin.html', title="Update Laporan Truk Sewa", form = form, user=current_user)

#hapus laporan
@sewa.route('/sewa/laporan/<int:id>/delete', methods=['POST'])
@login_required
def delete_laporan(id):
    laporan = Laporan_sewa.query.get_or_404(id)
    if current_user.username!='admin':
        abort(403)
    if ImageSet_sewa.query.filter(ImageSet_sewa.laporan_id==id):
        for list in ImageSet_sewa.query.filter(ImageSet_sewa.laporan_id==id):
            os.remove(os.path.join(current_app.root_path, 'static/images/laporan_sewa', list.image))
        ImageSet_sewa.query.filter(ImageSet_sewa.laporan_id==id).delete()
    db.session.delete(laporan)
    db.session.commit()
    flash('Laporan berhasil dihapus', 'success')
    return redirect(url_for('sewa.sewaa'))