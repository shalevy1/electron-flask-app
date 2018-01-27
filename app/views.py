import os
import pandas as pd
from flask import render_template, Blueprint, request, redirect, url_for
from flask import send_from_directory, flash, session
from werkzeug.utils import secure_filename
from .codes.utils import read_product, read_bom_file, get_sub_component
from .codes.utils import get_operation_sequence,get_sub_component_base_quatities, build_tree, get_bom, build_bom, read_excluded_product, read_ressources_data, read_inter_operartions, build_boo, get_max_time


home = Blueprint('home', __name__, template_folder='templates')
ALLOWED_EXTENSIONS = set(['csv', 'xlsx',])
UPLOAD_FOLDER = 'files/'
BOM_FOLDER = 'bom_files/'
FULL_BOM_FOLDER = os.path.join(os.getcwd(), BOM_FOLDER)
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
    full_path = os.path.join(os.getcwd(), UPLOAD_FOLDER+filename+'.'+ext)
    file_data.save(full_path)
    return full_path
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
                    return 'sucess'
                except Exception :
                    return 'Erreur choisissez un fichier correct'
            elif name == 'ressources':
                path = save_file(name, file_data=bom_file)
                try:
                    session['ressources_data'] = read_ressources_data(path)
                    return 'sucess'
                except Exception as error:
                    print(error)
                    return 'Erreur choisissez un fichier correct'
            elif name == 'interoperation':
                path = save_file(name, file_data=bom_file)
                try:
                    session['interopeartion_time'] = read_inter_operartions(path)
                    return 'sucess'
                except Exception as error:
                    print(error)
                    return 'Erreur choisissez un fichier correct'
            elif name == 'excluded':
                path = save_file(name, file_data=bom_file)
                try:
                    session['excluded_products'] = read_excluded_product(path)
                    return 'sucess'
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
                    FULL_BOM_FOLDER
                    )
                hours_df, boo_df = get_max_time(
                    results,
                    excluded_products,
                    operation_data,
                    component_with_interoperation,
                    inter_operation_time,
                    FULL_BOM_FOLDER)
                mass_df = mass_df.append(hours_df)
        mass_df.to_csv(path_or_buf=FULL_BOM_FOLDER+"mass_calculation.csv")
        return "sucess"
    except Exception as e:
        raise e
        print(e)
        return 'erreur survenu'

