from flask import Blueprint, render_template, request, flash, url_for, redirect, abort, current_app
from flask_login import login_required, current_user

from sqlalchemy import desc

from ..models import Laporan_supplier, ImageSet_supplier
from .forms import FormDatang, FormPergi, LaporanAdmin
from .. import db

from PIL import Image
from datetime import datetime, timedelta

import os
import secrets

supply = Blueprint('supply', __name__)

@supply.route('/supplier', methods=['GET', 'POST'])
@login_required
def supplier():
    if request.method == "POST":
        tgl_ats = request.form.get('atas')
        tgl_bwh = request.form.get('bawah')
        if tgl_ats and tgl_bwh:
            return render_template('/supplier/filter.html', user=current_user, 
            atas=tgl_ats, bawah=tgl_bwh) # datetime.strptime(tgl_ats,"%Y-%m-%d")+timedelta(days=1)
    return render_template('/supplier/index.html', user=current_user)

# API data table
@supply.route('/api/data/supplier')
def data():
    query = Laporan_supplier.query.order_by(desc(Laporan_supplier.id))

    #search filter
    search = request.args.get('search')
    if search:
        query = query.filter(db.or_(
            Laporan_supplier.nopol.like(f'%{search}%'),
            Laporan_supplier.sopir.like(f'%{search}%'),
            Laporan_supplier.supplier.like(f'%{search}%')
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
@supply.route('/api/data/supplier/date_from/<atas>/date_to/<bawah>', methods=['GET', 'POST'])
def filtered_data(atas, bawah):
    query = Laporan_supplier.query.order_by(desc(Laporan_supplier.id)).filter(Laporan_supplier.tgl_datang<=atas,
     Laporan_supplier.tgl_datang>=bawah)
    
    #search filter  
    search = request.args.get('search')
    if search:
        query = query.filter(db.or_(
            Laporan_supplier.nopol.like(f'%{search}%'),
            Laporan_supplier.sopir.like(f'%{search}%'),
            Laporan_supplier.supplier.like(f'%{search}%')
        ))
    total = query.count()

    #sorting
    sort = request.args.get('sort')
    if sort:
        order = []
        for s in sort.split(','):
            direction = s[0]
            name = s[1:]
            if name not in ['tgl_datang','nopol', 'sopir', 'supplier']:
                name = 'id'
            col = getattr(Laporan_supplier, name)
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
@supply.route('/supplier/laporan/<int:id>')
def laporan(id):
    laporan =  Laporan_supplier.query.get_or_404(id)
    foto = []
    if ImageSet_supplier.query.filter(ImageSet_supplier.laporan_id==id):
        for list in ImageSet_supplier.query.filter(ImageSet_supplier.laporan_id==id):
            foto.append(url_for('static', filename='images/laporan_supplier/' + list.image))

    return render_template('/supplier/laporan.html', user=current_user, laporan=laporan, img=foto)

# upload img
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/images/laporan_supplier', picture_fn)
    output_size = (384, 216)
    
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

# Add Laporan Datang
@supply.route('/supplier/add-datang', methods=['POST','GET'])
@login_required
def add_datang():
    form = FormDatang()
    if form.validate_on_submit():
        nopol = form.nopol.data.upper()
        sopir = form.sopir.data.upper()
        supplier = form.supplier.data.upper()
        satpam1 = form.satpam1.data.upper()
        muatan = form.muatan.data
        file_foto = form.foto.data
        
        cek_nopol = Laporan_supplier.query.order_by(desc(Laporan_supplier.id)).filter_by(nopol=nopol).first()
            
        if cek_nopol:
            if cek_nopol.tgl_pergi==None:
                flash('Error! Nomor Polisi/Sopir sudah datang', category='error')          
            else:
                new_post = Laporan_supplier(tgl_datang=datetime.now().replace(microsecond=0), 
                nopol=nopol, sopir=sopir, supplier=supplier, satpam1=satpam1, muatan=muatan)
                db.session.add(new_post)
                db.session.flush() #
                if file_foto:
                    foto = save_picture(file_foto)
                    new_foto = ImageSet_supplier(laporan_id=new_post.id, image= foto)
                    db.session.add(new_foto) #
                db.session.commit()
                return redirect(url_for('supply.supplier'))
        else:
            new_post = Laporan_supplier(tgl_datang=datetime.now().replace(microsecond=0), 
                nopol=nopol, sopir=sopir, supplier=supplier, satpam1=satpam1, muatan=muatan)
            db.session.add(new_post)
            db.session.flush() #
            if file_foto:
                foto = save_picture(file_foto)
                new_foto = ImageSet_supplier(laporan_id=new_post.id, image= foto)
                db.session.add(new_foto) #
            db.session.commit()
            return redirect(url_for('supply.supplier'))
    return render_template("/supplier/add_datang.html", title="Tambah Laporan Truk Supplier Datang", form = form, user=current_user)

# add Laporan Pergi
@supply.route('/supplier/add-pergi', methods=['POST','GET'])
@login_required
def add_pergi():
    form = FormPergi()
    if form.validate_on_submit():
        nopol = form.nopol.data.upper()
        sopir = form.sopir.data.upper()
        satpam2 = form.satpam2.data.upper()
        keterangan = form.keterangan.data
        file_foto = form.foto.data

        cek_nopol = Laporan_supplier.query.order_by(desc(Laporan_supplier.id)).filter_by(nopol=nopol).first()
        cek_sopir = Laporan_supplier.query.order_by(desc(Laporan_supplier.id)).filter_by(sopir=sopir).first()
        if cek_nopol and cek_sopir:
            laporan = Laporan_supplier.query.get_or_404(cek_nopol.id)
            if laporan.tgl_pergi==None:
                laporan.satpam2 = satpam2
                laporan.tgl_pergi = datetime.now().replace(microsecond=0)
                laporan.keterangan = keterangan
                if file_foto:
                    foto = save_picture(file_foto)
                    new_foto = ImageSet_supplier(laporan_id=laporan.id, image= foto)
                    db.session.add(new_foto)
                db.session.commit()
                return redirect(url_for('supply.supplier'))
            else:
                flash(f'Error! Truk {cek_nopol.nopol} telah pergi', category='error')
        else:
            flash('Error! Nopol/Nama Sopir tidak ada', category='error')
    return render_template("/supplier/add_pergi.html", title="Tambah Laporan Truk Supplier Pergi", form = form, user=current_user)

# Update
@supply.route('/supplier/laporan/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_laporan(id):
    laporan = Laporan_supplier.query.get_or_404(id)
    form = LaporanAdmin()
    if form.validate_on_submit():
        laporan.nopol = form.nopol.data.upper()
        laporan.sopir = form.sopir.data.upper()
        laporan.supplier = form.supplier.data
        laporan.muatan = form.muatan.data
        laporan.keterangan = form.keterangan.data
        file_foto = form.foto.data
        if file_foto:
            foto = save_picture(file_foto)
            new_foto = ImageSet_supplier(laporan_id=laporan.id, image= foto)
            db.session.add(new_foto)
        db.session.commit()
        flash('Data laporan berhasil diupdate!', 'success')
        return redirect(url_for('supply.laporan', id=laporan.id))
    elif request.method == 'GET':
        form.nopol.data = laporan.nopol
        form.sopir.data = laporan.sopir
        form.supplier.data = laporan.supplier
        form.muatan.data = laporan.muatan
        form.keterangan.data = laporan.keterangan
    return render_template('/supplier/add_admin.html', title="Update Laporan Supplier", form = form, user=current_user)

#hapus laporan
@supply.route('/supplier/laporan/<int:id>/delete', methods=['POST'])
@login_required
def delete_laporan(id):
    laporan = Laporan_supplier.query.get_or_404(id)
    if current_user.username!='admin':
        abort(403)
    if ImageSet_supplier.query.filter(ImageSet_supplier.laporan_id==id):
        for list in ImageSet_supplier.query.filter(ImageSet_supplier.laporan_id==id):
            os.remove(os.path.join(current_app.root_path, 'static/images/laporan_supplier', list.image))
        ImageSet_supplier.query.filter(ImageSet_supplier.laporan_id==id).delete()
    db.session.delete(laporan)
    db.session.commit()
    flash('Laporan berhasil dihapus', 'success')
    return redirect(url_for('supply.supplier'))
