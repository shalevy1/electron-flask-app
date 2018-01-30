# -*- coding: utf-8 -*-

import os, sys, platform
import pandas as pd
from flask import render_template, Blueprint, request, redirect, url_for
from flask import send_from_directory, flash, session
from werkzeug.utils import secure_filename
from .codes.utils import read_product, read_bom_file, get_sub_component
from .codes.utils import get_operation_sequence,get_sub_component_base_quatities, build_tree, get_bom, build_bom, read_excluded_product, read_ressources_data, read_inter_operartions, build_boo, get_max_time


home = Blueprint('home', __name__, template_folder='templates')
ALLOWED_EXTENSIONS = set(['csv', 'xlsx',])



def get_bom_folder():
#get my document folder for windows otherswise
    if platform.system() == 'Windows' :
        import ctypes.wintypes
        CSIDL_PERSONAL = 5       # My Documents
        SHGFP_TYPE_CURRENT = 0   # Get current, not default value
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        return  buf.value
    else:
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        else:
            return os.getcwd()
FULL_BOM_FOLDER = get_bom_folder()
UPLOAD_FOLDER = os.path.join(FULL_BOM_FOLDER, 'PLT_TOOLS', 'files')
BOM_FOLDER = os.path.join(FULL_BOM_FOLDER, 'PLT_TOOLS', 'bom_files')
#create the directory
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BOM_FOLDER,  exist_ok=True)
def allowed_file(filename):
    """
    check if a file name is in alowwed filename"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def save_file(filename, file_data):
    """
    save a file with a name according to his category

    """
    filename = filename
    ext = file_data.filename.rsplit('.', 1)[1].lower()
    full_path = os.path.join(UPLOAD_FOLDER, filename+'.'+ext)
    try:
        file_data.save(full_path)
        return full_path
    except Exception as e:
        raise e
@home.route('/')
def index():
    """
    the main entry of my page
    """
    return render_template("index.html")



@home.route('/uploadBomFile', methods=['POST', 'GET'])
def upload_bom():
    """
    handle the unique route for uploading differents files
    on the server, each file has a category and it is save accoridng to
    his category ,
    after saving the file , the applications reads it
    and create the corresponding dataframe
    and save it in the application context
    """
    if request.method == 'POST':
        bom_file = request.files['file']
        name = request.form.get('category', '')
        if bom_file.filename == '':
            return "aucun  fichier selectioner"
        if bom_file and allowed_file(bom_file.filename):
            #save file according to his category
            #if BOOM save as bom , if product save as product etc
            if name == 'bom':
                path = save_file(name, file_data=bom_file)
                try:
                    session['components_data'], session['operation_data'], session['base_material'], session['components_with_sub'] = read_bom_file(path)
                    return 'Bom Telecharger avec sucess'
                except Exception :
                    return 'Erreur choisissez un fichier correct'
            elif name == 'ressources':
                path = save_file(name, file_data=bom_file)
                try:
                    session['ressources_data'] = read_ressources_data(path)
                    return 'les ressources charger avec sucess'
                except Exception as error:
                    print(error)
                    return 'Erreur choisissez un fichier correct'
            elif name == 'interoperation':
                path = save_file(name, file_data=bom_file)
                try:
                    session['interopeartion_time'] = read_inter_operartions(path)
                    return 'les interoperations charger avec sucess'
                except Exception as error:
                    print(error)
                    return 'Erreur choisissez un fichier correct'
            elif name == 'excluded':
                path = save_file(name, file_data=bom_file)
                try:
                    session['excluded_products'] = read_excluded_product(path)
                    return 'les fichiers à exclure chargées avec succes , charger les produits pour debuter avec les calculs'
                except Exception as e:
                    print(e)
                    return 'Erreur choisissez un fichier correct'
            elif name == 'product':
                path = save_file(name, file_data=bom_file)
                try:
                    session['products'] = read_product(path)
                    return redirect(url_for('home.do_calculations'))
                except Exception as e:
                    print(e)
                    return 'Erreur choisissez un fichier correct'
            else:
                pass
            #path_name = send_from_directory(UPLOAD_FOLDER, filename)
            #return redirect(url_for('home.read_dataset', path=filename))
            return 'sucess'
        else:
            return 'choisissez un fichier correct'
    return render_template("index.html")



@home.route('/readBOMt/calculations', methods=['POST', 'GET'])
def do_calculations():
    """
    this is a long running script to to the job of building the files
    basscially after reading all the dataset it should run the function
    doing mass calculation this function is a long running process and could
    take up to 30 mins depending to the files passed in parameter
    """

    try:
        components_data = session.get('components_data', None)
        operation_data = session.get('operation_data', None)
        base_material = session.get('base_material', None)
        components_with_sub = session.get('components_with_sub', None)
        ressources_data = session.get('ressources_data', None)
        operation_data = pd.merge(
            left=ressources_data['hours_days'].reset_index(),
            left_on='Poste de travail',
            right=operation_data.reset_index(),
            right_on="Resource")
        operation_data.set_index('components', inplace=True)
        inter_operation_time = session.get('interopeartion_time', None)
        component_with_interoperation = operation_data.loc[operation_data.index.isin(inter_operation_time.index)].index
        products = session.get('products', None)
        excluded_products = session.get('excluded_products', None)
        mass_df = pd.DataFrame()
        for name in products.index:
            batch_size = products.loc[name, 'Batch Size']
            name = str(name)
            if name not in base_material.values:
                results = get_bom(name, components_data)
                results_df = build_bom(
                    results,
                    batch_size,
                    components_data,
                    base_material,
                    BOM_FOLDER
                    )
                hours_df, boo_df = get_max_time(
                    results,
                    excluded_products,
                    operation_data,
                    component_with_interoperation,
                    inter_operation_time,
                    BOM_FOLDER)
                mass_df = mass_df.append(hours_df)
        mass_df.to_csv(path_or_buf=os.path.join(BOM_FOLDER, "mass_calculation.csv"))
        return "Les calculs se sont teminées avec sucess , veuillez verifier les fichier generés "
    except Exception as e:
        print(e)
        return 'erreur survenu, verifier si les fichier ont été bien chargés '

