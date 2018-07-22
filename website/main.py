#/usr/bin/env python3
# -*- coding:utf-8 -*-

from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import requests
import os
import python_script.add_method_knowledge_graph as add_method
import python_script.sparql_to_visualization as visualization
import python_script.import_export_rdf4j as imp_exp

METHOD_FOLDER = 'static/method_schema'
UPLOAD_FOLDER = '/home/damien/Workspace/master_project/website/temp'
#URL_SERVER = 'http://kr.unige.ch:8080/rdf4j-server/repositories/master_project_damien'
ALLOWED_EXTENSIONS = set(['json', 'yml'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

@app.route('/')
def racine():
    render_template('accueil.html')

@app.route('/accueil')
def accueil():
    return render_template('accueil.html')

@app.route('/export', methods=['GET', 'POST'])
def export():
    if request.method == 'POST':
        filename = visualization.get_all_articles()
        print(filename)
        return send_from_directory(UPLOAD_FOLDER,
                               filename, as_attachment=True)
    else:
        return render_template('export.html')

@app.route('/import', methods=['GET', 'POST'])
def upload_file():
    """Route if someone wants to add his method in the knowledge graph"""
    if request.method == 'POST':
        # check if the post request has the file part
        # print(request.files)
        if 'file' not in request.files:
            flash('Aucun fichier trouvé')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            full_path_name = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(full_path_name)
            extension = os.path.splitext(filename)[1]
            full_path_rdf_name = full_path_name.replace(extension, '.rdf')

            # We take the file and convert it into rdf file
            [_, method_name] = add_method.create_rdf_graph(full_path_name, full_path_rdf_name)

            # We take the new rdf graph and we import it in the rdf4j server
            imp_exp.import_rdf_to_rdf4j(full_path_rdf_name, method_name)

            # We get a new json file for the vizualisation
            visualization.write_informations_for_visualization(method_name)

            flash('The file has been successfully added to the database')
            return redirect(url_for('upload_file'))
    else:
        return render_template('import.html')


"""app.route('/world', methods=['GET', 'POST'])
def display_world():
    list_method = get_list_method_schema()
    if request.method == 'POST':
        method_select = request.form['method_select']
        name_file = '{}/{}.json'.format(METHOD_FOLDER, method_select)
        # We get index of element which is selected
        index = ([idx for idx in range(len(list_method)) if list_method[idx] == method_select])[0]
        # We insert element selected in first position and we pop the old position
        list_method.insert(0, method_select)
        list_method.pop(index+1)
        print(name_file)
        return render_template('world.html', printable=True, list_method=list_method, name_file=name_file, titre="Bienvenue !")
    else:
        return render_template('world.html', printable=False, list_method=list_method, titre="Bienvenue !")
"""

@app.route('/visualization', methods=['GET', 'POST'])
def vizualisation():
    list_method = get_list_method_schema()
    if request.method == 'POST':
        method_select = request.form['method_select']
        name_file = '{}/{}.json'.format(METHOD_FOLDER, method_select)
        # We get index of element which is selected
        index = ([idx for idx in range(len(list_method)) if list_method[idx] == method_select])[0]
        # We insert element selected in first position and we pop the old position
        list_method.insert(0, method_select)
        list_method.pop(index+1)
        informations_method = visualization.get_information_method(method_select)
        method_title = informations_method[0]
        method_description = informations_method[1]
        print(visualization.get_information_method(method_select))
        return render_template('visualization.html', printable=True, list_method=list_method, name_file=name_file, method_title=method_title, method_description=method_description)
    else:
        return render_template('visualization.html', printable=False, list_method=list_method, titre="Bienvenue !")


@app.errorhandler(404)
def ma_page_404(error):
    return "This is an error 404", 404


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_list_method_schema():
    """Return list of method schema in static/method_schema"""
    list_method = []
    for method in os.listdir(METHOD_FOLDER):
        list_method.append(method.replace('.json', ''))
    return list_method


if __name__ == '__main__':
    app.run(debug=True)
