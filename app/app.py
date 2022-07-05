from flask import Flask, render_template, redirect, url_for, request
from .db import Connector

app = Flask(__name__)
db = Connector()


current_user = {
    'id': None,
    'name': None,
    'tipo': None,
    'id_original': None
}


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']
        # Checa se um usuário com essa senha existe no banco de dados
        login_result = db.query(f"SELECT userid, tipo, idoriginal FROM users WHERE login = '{user}' AND password = md5('{password}')")[0]
        if login_result:
            current_user['id'] = login_result[0]
            current_user['tipo'] = login_result[1]
            current_user['id_original'] = login_result[2]

            # Seta o nome do usuário de acordo seu tipo
            if current_user['tipo'] == 'Administrador':
                current_user['name'] = user.title()
            elif current_user['tipo'] == 'Escuderia':
                result = db.query(f"SELECT name FROM constructors WHERE constructorid = '{current_user['id_original']}'")[0]
                current_user['name'] = result[0]
            elif current_user['tipo'] == 'Piloto':
                result = db.query(f"SELECT forename, surname FROM driver WHERE driverid = '{current_user['id_original']}'")[0]
                current_user['name'] = result[0] + " " + result[1]

            return redirect(url_for('homepage'))
        else:
            error = 'Credenciais inválidas. Por favor, tente novamente.'
    return render_template('login.html', current_user=current_user, error=error)


@app.route('/logout')
def logout():
    current_user['id'] = None
    current_user['name'] = None
    current_user['tipo'] = None
    current_user['id_original'] = None
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def homepage():
    message = ''
    results = dict()
    table_title = ''
    fields = list()
    rows = list()
    report = request.args.get("relatorio")

    #---------------------------#
    # Homepage do Administrador #
    #---------------------------#

    if current_user['tipo'] == 'Administrador':
        # Overview
        driver_amount = db.query(f"SELECT COUNT(1) FROM driver")[0][0]
        constructors_amount = db.query(f"SELECT COUNT(1) FROM constructors")[0][0]
        races_amount = db.query(f"SELECT COUNT(1) FROM races")[0][0]
        seasons_amount = db.query(f"SELECT COUNT(1) FROM seasons")[0][0]

        # Relatorio 1
        if report == '1':
            table_title = 'Quantidade de resultados por cada status'
            fields = ['Status', 'Contagem']
            rows = db.query(
                f"SELECT DISTINCT status.status, COUNT(1) OVER (PARTITION BY status.statusid) AS count "
                f"FROM results JOIN status ON results.statusid = status.statusid ORDER BY count DESC"
            )

        # Relatorio 2
        if report == '2':
            city = request.args.get("cidade")
            table_title = 'Aeroportos brasileiros nas proximidades'
            fields = [
                'Nome da Cidade',
                'Código IATA do Aeroporto',
                'Nome do Aeroporto',
                'Cidade do Aeroporto',
                'Distância',
                'Tipo do Aeroporto'
            ]
            rows = db.query(f"SELECT * FROM airports_near_city('{city}', 100000) ORDER BY distance")

        return render_template(
            'homepage_admin.html',
            current_user=current_user,
            driver_amount=driver_amount,
            constructors_amount=constructors_amount,
            races_amount=races_amount,
            seasons_amount=seasons_amount,
            table_title=table_title,
            fields=fields,
            rows=rows
        )

    #-----------------------#
    # Homepage da Escuderia #
    #-----------------------#

    elif current_user['tipo'] == 'Escuderia':
        # Overview
        wins = db.query(
            f"SELECT COUNT(1) FROM results "
            f"WHERE constructorid = '{current_user['id_original']}'"
            f"AND position = 1"
        )[0][0]
        drivers_amount = db.query(
            f"SELECT COUNT(DISTINCT driverid) FROM results "
            f"WHERE constructorid = '{current_user['id_original']}'"
        )[0][0]
        first_reg_year = db.query(
            f"SELECT year FROM races "
            f"JOIN results ON races.raceid = results.raceid "
            f"WHERE results.constructorid = '{current_user['id_original']}' "
            f"ORDER BY year ASC LIMIT 1"
        )[0][0]
        last_reg_year = db.query(
            f"SELECT year FROM races "
            f"JOIN results ON races.raceid = results.raceid "
            f"WHERE results.constructorid = '{current_user['id_original']}' "
            f"ORDER BY year DESC LIMIT 1"
        )[0][0]

        # Uma requisição POST aqui é uma consulta de piloto
        if request.method == 'POST':
            forename = request.form['forename']
            query_result = db.query(
                f"SELECT forename, surname, dob, nationality FROM driver "
                f"WHERE LOWER(forename) = LOWER('{forename}') "
                f"AND EXISTS (SELECT 1 FROM results WHERE driverid = driver.driverid)"
            )
            if query_result:
                results['forename'] = query_result[0][0]
                results['surname'] = query_result[0][1]
                results['dateofbirth'] = query_result[0][2]
                results['nationality'] = query_result[0][3]
            else:
                message = 'Não existe um piloto com esse nome que já tenha corrido pela sua escuderia'

        return render_template(
            'homepage_constructor.html',
            current_user=current_user,
            wins=wins,
            drivers_amount=drivers_amount,
            first_reg_year=first_reg_year,
            last_reg_year=last_reg_year,
            message=message,
            results=results
        )

    #--------------------#
    # Homepage do Piloto #
    #--------------------#

    elif current_user['tipo'] == 'Piloto':
        # Overview
        wins = db.query(
            f"SELECT COUNT(1) FROM results "
            f"WHERE driverid = '{current_user['id_original']}'"
            f"AND position = 1"
        )[0][0]
        first_reg_year = db.query(
            f"SELECT year FROM races "
            f"JOIN results ON races.raceid = results.raceid "
            f"WHERE results.driverid = '{current_user['id_original']}' "
            f"ORDER BY year ASC LIMIT 1"
        )[0][0]
        last_reg_year = db.query(
            f"SELECT year FROM races "
            f"JOIN results ON races.raceid = results.raceid "
            f"WHERE results.driverid = '{current_user['id_original']}' "
            f"ORDER BY year DESC LIMIT 1"
        )[0][0]

        return render_template(
            'homepage_driver.html',
            current_user=current_user,
            wins=wins,
            first_reg_year=first_reg_year,
            last_reg_year=last_reg_year
        )

    #----------------------------------------------------------------#
    # Se usuário não for um dos 3 redireciona para a página de login #
    #----------------------------------------------------------------#

    else:
        return redirect(url_for('login'))


@app.route('/cadastrar/escuderia', methods=['GET', 'POST'])
def register_constructor():
    if current_user['id'] is None:
        return redirect(url_for('login'))
    message = ''
    if request.method == 'POST':
        # Le os dados vindos do form
        constructorref = request.form['constructorref']
        name = request.form['name']
        nationality = request.form['nationality']
        url = request.form['url']
        # Pega o último id da tabela e soma 1 para determinar o id dessa escuderia
        constructorid = db.query(f"SELECT constructorid FROM constructors ORDER BY constructorid DESC LIMIT 1")[0][0] + 1
        # Insere dados na tabela
        success = db.execute(
            f"INSERT INTO constructors (constructorid, constructorref, name, nationality, url) "
            f"VALUES ('{constructorid}', '{constructorref}', '{name}', '{nationality}', '{url}')"
        )
        if success:
            message = 'Escuderia ' + name + ' criada com sucesso'
        else:
            message = 'Já existe uma escuderia com esse constructorref ou name, por favor altere e tente novamente'
    return render_template('register_constructor.html', current_user=current_user, message=message)


@app.route('/cadastrar/piloto', methods=['GET', 'POST'])
def register_driver():
    if current_user['id'] is None:
        return redirect(url_for('login'))
    message = ''
    if request.method == 'POST':
        # Le os dados vindos do form
        driverref = request.form['driverref']
        number = request.form['number']
        code = request.form['code']
        forename = request.form['forename']
        surname = request.form['surname']
        dateofbirth = request.form['dateofbirth']
        nationality = request.form['nationality']
        # Pega o último id da tabela e soma 1 para determinar o id desse piloto
        driverid = db.query(f"SELECT driverid FROM driver ORDER BY driverid DESC LIMIT 1")[0][0] + 1
        # Insere dados na tabela
        success = db.execute(
            f"INSERT INTO driver (driverid, driverref, number, code, forename, surname, dob, nationality) "
            f"VALUES ('{driverid}', '{driverref}', '{number}', '{code}', '{forename}', '{surname}', '{dateofbirth}', '{nationality}')"
        )
        if success:
            message = 'Piloto ' + forename + ' ' + surname + ' criado com sucesso'
        else:
            message = 'Já existe um piloto com esse driverref, por favor altere e tente novamente'
    return render_template('register_driver.html', current_user=current_user, message=message)
