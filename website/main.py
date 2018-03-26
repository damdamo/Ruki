#/usr/bin/env python3
# -*- coding:utf-8 -*-

from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
import requests
import os
import python_script.add_method_knowledge_graph as add_method
import python_script.sparql_to_visualization as visualization

METHOD_FOLDER = 'static/method_schema'
UPLOAD_FOLDER = '/home/damien/Workspace/master_project/website/temp'
ALLOWED_EXTENSIONS = set(['json', 'yml'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

@app.route('/coucou')
def dire_coucou():
    return 'Coucou !'

@app.route('/')
def racine():
    return "Le chemin de 'racine' est : " + request.path

@app.route('/accueil')
def answer_sparql():
    answer_table = get_response_sparql()
    return render_template('accueil.html', titre="Bienvenue !", results=answer_table)

@app.route('/import', methods=['GET', 'POST'])
def upload_file():
    """Route if someone wants to add his method in the knowledge graph"""
    if request.method == 'POST':
        # check if the post request has the file part
        print(request.files)
        if 'file' not in request.files:
            flash('Aucun fichier trouvé')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('Aucun fichier sélectionné')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            full_path_name = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(full_path_name)
            extension = os.path.splitext(filename)[1]
            full_path_rdf_name = full_path_name.replace(extension, '.rdf')

            add_method.create_rdf_graph(full_path_name, full_path_rdf_name)

            print("YOOOO")

            """------------------------------TEST------------------------------"""

            url = 'http://kr.unige.ch:8080/rdf4j-server/repositories/master_project_damien/statements'
            files = {'data':'{}'.format(open(full_path_rdf_name, 'rb'))}
            headers = {'Content-Type':'text/n3'}
            result = requests.post(url, data=files, headers=headers)
            print(result)

            """----------------------------------------------------------------"""


            flash('Le fichier a correctement été ajouté à la base de connaissance')
            return redirect(url_for('upload_file'))
    else:
        return render_template('import.html')


@app.errorhandler(404)
def ma_page_404(error):
    return "Ma jolie page 404", 404

@app.route('/world', methods=['GET', 'POST'])
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
        
        return render_template('world.html', printable=True, list_method=list_method, name_file=name_file, titre="Bienvenue !")
    else:
        return render_template('world.html', printable=False, list_method=list_method, titre="Bienvenue !")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_list_method_schema():
    """Return list of method schema in static/method_schema"""
    list_method = []
    for method in os.listdir(METHOD_FOLDER):
        list_method.append(method.replace('.json', ''))
    return list_method

def get_response_sparql(sparql_request):
    """ Take a string in input which represent the sparql request
    Return a csv with the answer of request """

    url = 'http://kr.unige.ch:8080/rdf4j-server/repositories/master_project_damien'

    query4 = '''PREFIX cui: <http://cui.unige.ch/>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX vgiid: <http://vgibox.eu/repository/index.php?curid=>
        PREFIX xml: <http://www.w3.org/XML/1998/namespace>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX schema: <http://schema.org/>

        SELECT DISTINCT ?a
        WHERE {
          ?a a schema:Article.
        }'''

    payload = {'query': '{}'.format(query4), 'queryLn':'SPARQL'}

    result = requests.get(url, params=payload)

    my_text = (result.content).decode("utf-8")
    return my_text.split('\r\n')


if __name__ == '__main__':
    app.run(debug=True)
