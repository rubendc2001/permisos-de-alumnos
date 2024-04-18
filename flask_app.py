from flask import Flask, Response
from flask import redirect, render_template, url_for, session, request, flash
from api_clima import clima
from flask_mysqldb import MySQL, MySQLdb
from datetime import datetime
from werkzeug.utils import secure_filename
import os

#Configurar carpeta template
app = Flask(__name__, template_folder="template")
app.config["UPLOAD_FOLDER"] = "archivos_alumno"

#Configurar conexion a base de datos
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "permisos_integradora_final"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

#Establecer la configuracion anterior
mysql = MySQL(app)

#Rutas de la aplicacion
@app.route('/')
def home():
    return redirect(url_for('login'))

#Ruta de la pagina inicial del admin
@app.route('/admin')
def admin():
    if 'logueado' in session and session['id_rol'] == 1:
        nombre = session['nombre']
        apellidos = session['apellidos']
        correo = session['correo']
        contra = session['pas']
        return render_template("administrador/inicio_admin.html", nombre = nombre, apellidos = apellidos, correo = correo, contra = contra)
    elif 'logueado' in session and session['id_rol'] != 1:
        return redirect(url_for('logout'))
    else:
        return redirect(url_for('login'))

#Ruta de la pagina inicial del alumno
@app.route('/alumno')
def alumno():
    if 'logueado' in session and session['id_rol'] == 4:
        nombre = session['nombre']
        apellidos = session['apellidos']
        correo = session['correo']
        contra = session['pas']
        matricula = session['codigo']
        carrera = session['carrera']
        alumno = session['id_persona']
        cur1 = mysql.connection.cursor()
        cur1.execute("""
            SELECT  carreras.nombre AS alumno_carrera, divisiones.nombre AS alumno_division
            FROM carreras
            INNER JOIN divisiones ON carreras.id_division = divisiones.id_division
            WHERE id_carrera = %s
        """, (carrera,))
        div_car_alumno = cur1.fetchone()
        cur1.close()
        cur2 = mysql.connection.cursor()
        cur2.execute("""
            SELECT grupos.nombre AS alumno_grupo
            FROM grupos_alumnos
            INNER JOIN grupos ON grupos_alumnos.id_grupo = grupos.id_grupo
            WHERE id_alumno = %s
        """, (alumno,))
        grupo_alumno = cur2.fetchone()
        cur2.close()
        return render_template("alumno/inicio_alumno.html", nombre = nombre, apellidos = apellidos, correo = correo, contra = contra, matricula = matricula, div_car_alumno = div_car_alumno, grupo_alumno = grupo_alumno)
    elif 'logueado' in session and session['id_rol'] != 4:
        print("No tienes permisos para acceder a esta seccion")
        return redirect(url_for('logout'))
    else:
        return redirect(url_for('login'))

#Ruta de la pagina de registro de permiso del alumno
@app.route('/registro-permiso')
def registro_permiso():
    if 'logueado' in session and session['id_rol'] == 4:
        cur = mysql.connection.cursor()
        persona = session['id_persona']
        cur.execute("""
            SELECT permisos.fecha_solicitud AS fecha_soli, permisos.fechas_solicitadas AS fechas_soli, permisos.nombre_archivo AS archivo_per, permisos.asunto AS asunto_per, estatus.nombre AS estatus_per FROM permisos
            INNER JOIN estatus ON permisos.id_estatus = estatus.id_estatus
            WHERE id_persona = %s""", (persona,))
        permisos_alumno = cur.fetchall()
        cur.close()       
        mensaje1 = request.args.get('mensaje1')
        tipoPermiso = consultar_tipo()
        return render_template("alumno/registro_permiso.html", mensaje1 = mensaje1, permisos_alumno = permisos_alumno, tipoPermiso = tipoPermiso)
    elif 'logueado' in session and session['id_rol'] != 4:
        print("No tienes permisos para acceder a esta seccion")
        return redirect(url_for('logout')) 
    else:
        return redirect(url_for('login'))

#Ruta para crear registro de alumno
@app.route('/crear-permiso-alumno', methods=["GET", "POST"])
def crear_permiso_alumno():
    if 'logueado' in session and session['id_rol'] == 4:
        idPersona = session['id_persona']
        matricula = session['codigo']
        del_dia = request.form['txtDelDia']
        hasta_dia = request.form['txtHastaDia']
        fechas_solicitadas = del_dia + " al " +  hasta_dia
        asunto = request.form['txtAsunto']
        tipo_permiso = request.form['txtTipo']
        ahora = datetime.now()
        fecha_soli = ahora.date()
        fecha = str(fecha_soli)
        archivo = request.files['txtArchivo']
        filename = secure_filename(archivo.filename)
        nombre_final = fecha + matricula + filename
        archivo.save(os.path.join(app.config["UPLOAD_FOLDER"], fecha + matricula + filename))
        cur1 = mysql.connection.cursor()
        cur1.execute("INSERT INTO permisos (id_persona, fecha_solicitud, fechas_solicitadas, nombre_archivo, asunto, revisado_tutor, id_estatus, id_tipo) VALUES (%s, %s, %s, %s, %s,'1','1', %s)",(idPersona, fecha_soli, fechas_solicitadas, nombre_final, asunto, tipo_permiso))
        mysql.connection.commit()
        cur1.close()
        mensaje1 = "Solicitud enviada, espera a que te la aprueben"
        return redirect(url_for('registro_permiso', mensaje1 = mensaje1))
    elif 'logueado' in session and session['id_rol'] != 4:
        print("No tienes permisos para acceder a esta seccion")
        return redirect(url_for('logout')) 
    else:
        return redirect(url_for('login'))

#Ruta de la pagina inicial del tutor
@app.route('/tutor')
def tutor():
    if 'logueado' in session and session['id_rol'] == 3:
        nombre = session['nombre']
        apellidos = session['apellidos']
        correo = session['correo']
        contra = session['pas']
        return render_template("tutor/inicio_tutor.html", nombre = nombre, apellidos = apellidos, correo = correo, contra = contra)
    elif 'logueado' in session and session['id_rol'] != 3:
        print("No tienes permisos para acceder a esta seccion")
        return redirect(url_for('logout'))
    else:
        return redirect(url_for('login'))

#Ruta de la pagina inicial del director
@app.route('/director')
def director():
    if 'logueado' in session and session['id_rol'] == 2:
        nombre = session['nombre']
        apellidos = session['apellidos']
        correo = session['correo']
        contra = session['pas']
        return render_template("director/inicio_director.html", nombre = nombre, apellidos = apellidos, correo = correo, contra = contra)
    elif 'logueado' in session and session['id_rol'] != 2:
        print("No tienes permisos para acceder a esta seccion")
        return redirect(url_for('logout'))
    else:
        return redirect(url_for('login'))

@app.route('/ver-alumnos-del-grupo')
def ver_alumnos_del_grupo():
    grupoid = request.args.get('grupoid')
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT personas.nombre AS nombre_alumno, personas.codigo AS matricula_alumno, personas.apellidos AS apellidos_alumno, personas.correo AS correo_alumno
        FROM grupos_alumnos
        INNER JOIN grupos ON grupos_alumnos.id_grupo = grupos.id_grupo
        INNER JOIN personas ON grupos_alumnos.id_alumno = personas.id_persona
        WHERE grupos_alumnos.id_grupo = %s
    """, (grupoid,))
    alumnos_grupo = cur.fetchall()
    cur1 = mysql.connection.cursor()
    cur.close()
    cur1.execute("SELECT *FROM grupos WHERE id_grupo = %s", (grupoid,))
    datogrupo =  cur1.fetchone()    
    cur1.close()
    return render_template('administrador/alumnos_del_grupo.html' , alumnos_grupo = alumnos_grupo, datogrupo = datogrupo)

@app.route('/consultar-alumnos-grupo', methods=['GET', 'POST'])
def consultar_alumnos_grupo():
    grupoid = request.form['txtGrupoid']
    return redirect(url_for('ver_alumnos_del_grupo', grupoid = grupoid))
    

#Ruta de la pagina de registro de divisiones
@app.route('/registro-division')
def registro_division():
    if 'logueado' in session and session['id_rol'] == 1: 
        mensaje1 = request.args.get('mensaje1')
        mensaje2 = request.args.get('mensaje2')
        directores = consultar_directores_individuales()
        divisiones = consultar_divisiones_con_directores()
        return render_template("administrador/registro_division.html", mensaje2 = mensaje2, directores = directores, mensaje1 = mensaje1, divisiones = divisiones)
    elif 'logueado' in session and session['id_rol'] != 1:
        print("No tienes permisos para acceder a esta seccion")
        return redirect(url_for('logout')) 
    else:
        return redirect(url_for('login'))

#Ruta de la pagina de registro de carreras
@app.route('/registro-carrera')
def registro_carrera():
    if 'logueado' in session and session['id_rol'] == 1:
        divisiones = consultar_divisiones_individuales()
        carreras = consultar_carreras_con_division()
        mensaje1 = request.args.get('mensaje1')    
        return render_template("administrador/registro_carrera.html", divisiones = divisiones, carreras = carreras, mensaje1 = mensaje1)
    elif 'logueado' in session and session['id_rol'] != 1:
        print("No tienes permisos para acceder a esta seccion")
        return redirect(url_for('logout')) 
    else:
        return redirect(url_for('login'))

#ruta de la pagina de registro de grupos
@app.route('/registro-grupo')
def registro_grupo():
    if 'logueado' in session and session['id_rol'] == 1:
        dg = prueba_grupos()
        datos_grupo_tutor = datos_grupos_t()
        turnos = consultar_turnos_individuales()
        carreras = consultar_carreras_con_division()
        tutores = consultar_tutores_individuales()
        mensaje1 = request.args.get('mensaje1')
        mensaje2 = request.args.get('mensaje2')
        return render_template("administrador/registro_grupo.html", datos_grupo_tutor = datos_grupo_tutor, tutores = tutores, dg = dg, turnos = turnos, carreras = carreras, mensaje1 = mensaje1, mensaje2 = mensaje2)
    elif 'logueado' in session and session['id_rol'] != 1:
        print("No tienes permisos para acceder a esta seccion")
        return redirect(url_for('logout')) 
    else:
        return redirect(url_for('login'))

#Ruta de la pagina de registro de director
@app.route('/registro-director')
def registro_director():
    if 'logueado' in session and session['id_rol'] == 1:
        mensaje1 = request.args.get('mensaje1')
        directores = prueba_directores()
        return render_template("administrador/registro_director.html", directores = directores, mensaje1 = mensaje1)
    elif 'logueado' in session and session['id_rol'] != 1:
        print("No tienes permisos para acceder a esta seccion")
        return redirect(url_for('logout')) 
    else:
        return redirect(url_for('login'))
    
#Ruta de la pagina de registro de tutor
@app.route('/registro-tutor')
def registro_tutor():
    if 'logueado' in session and session['id_rol'] == 1:
        mensaje1 = request.args.get('mensaje1')
        tutores = consultar_tutores_individuales()
        return render_template("administrador/registro_tutor.html", mensaje1 = mensaje1, tutores = tutores)
    elif 'logueado' in session and session['id_rol'] != 1:
        print("No tienes permisos para acceder a esta seccion")
        return redirect(url_for('logout')) 
    else:
        return redirect(url_for('login'))
    
#Ruta de la pagina de registro de alumno
@app.route('/registro-alumno')
def registro_alumno():
    if 'logueado' in session and session['id_rol'] == 1:
        mensaje1 = request.args.get('mensaje1')
        mensaje2 = request.args.get('mensaje2')
        mensaje3 = request.args.get('mensaje3')
        carreras = consultar_carreras_con_division()
        alumnos = prueba_alumnos()
        return render_template("administrador/registro_alumno.html", carreras = carreras, mensaje1 = mensaje1, alumnos = alumnos, mensaje2 = mensaje2, mensaje3 = mensaje3)
    elif 'logueado' in session and session['id_rol'] != 1:
        print("No tienes permisos para acceder a esta seccion")
        return redirect(url_for('logout')) 
    else:
        return redirect(url_for('login'))

@app.route('/registrar-alumnos-grupo')
def registrar_alumnos_grupo():
    carrera_buscar = request.args.get('carrera_buscar')
    nombreCa = request.args.get('nombreCarrera')
    id_del_grupo = request.args.get('id_del_grupo')
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT personas.id_persona AS id_alumno, personas.nombre AS nombre_alumno, personas.apellidos AS apellidos_alumno, personas.codigo AS matricula_alumno
        FROM personas
        LEFT JOIN grupos_alumnos ON personas.id_persona = grupos_alumnos.id_alumno
        WHERE grupos_alumnos.id_grupo IS NULL AND personas.id_rol = 4 AND personas.id_carrera = %s
    """, (carrera_buscar,))
    alumnos_sg = cur.fetchall()
    cur.close()
    return render_template("administrador/agregar_alumnos.html", alumnos_sg = alumnos_sg, nombreCa = nombreCa, id_del_grupo = id_del_grupo, carrera_buscar = carrera_buscar)

@app.route('/consultar-alumnos-carrera', methods=['GET', 'POST'])
def consultar_alumnos_carrera():
    carrera_buscar = request.form['txtCarreraGrupo']
    nombreCarrera = request.form['txtNombreCarrera']
    id_del_grupo = request.form['txtGrupoid']
    return redirect(url_for('registrar_alumnos_grupo', carrera_buscar = carrera_buscar, nombreCarrera = nombreCarrera, id_del_grupo = id_del_grupo))

#Ruta para crear registro de division
@app.route('/crear-registro-division', methods=["GET", "POST"])
def crear_registro_division():
    if 'logueado' in session and session['id_rol'] == 1:
        nombre = request.form['txtNombre']
        director = request.form['txtDirector']
        cur1 = mysql.connection.cursor()
        cur1.execute("SELECT * FROM divisiones_directores WHERE id_director = %s", (director,))
        datos = cur1.fetchall()
        cur1.close()
        if datos:
            mensaje2 = "¡El director ya está registrado en otra division!"
            return redirect(url_for('registro_division', mensaje2 = mensaje2))
        else:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO divisiones (nombre) VALUES (%s)", (nombre,))
            last_id = cur.lastrowid
            cur.execute("INSERT INTO divisiones_directores (id_division, id_director) VALUES (%s, %s)", (last_id, director))
            mysql.connection.commit()
            cur.close()
            mensaje1 = "Division registrada con exito"
            return redirect(url_for('registro_division', mensaje1 = mensaje1))
    elif 'logueado' in session and session['id_rol'] != 1:
        print("No tienes permisos para acceder a esta seccion")
        return redirect(url_for('logout')) 
    else:
        return redirect(url_for('login'))

#Ruta para crear registro de carrera
@app.route('/crear-registro-carrera', methods=["GET", "POST"])
def crear_registro_carrera():
    if 'logueado' in session and session['id_rol'] == 1:
        nombre = request.form['txtNombre']
        division = request.form['txtDivision']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO carreras (nombre, id_division) VALUES (%s, %s)",(nombre, division))
        mysql.connection.commit()
        cur.close()
        mensaje1 = "Carrera registrada con exito"
        return redirect(url_for('registro_carrera', mensaje1 = mensaje1))
    elif 'logueado' in session and session['id_rol'] != 1:
        print("No tienes permisos para acceder a esta seccion")
        return redirect(url_for('logout')) 
    else:
        return redirect(url_for('login'))

#Ruta para crear registro de grupos
@app.route('/crear-registro-grupo', methods=["GET", "POST"])
def crear_registro_grupo():
    if 'logueado' in session and session['id_rol'] == 1:
        nombre = request.form['txtNombre']
        fecha_ini = request.form['txtFechaIni']
        fecha_fin = request.form['txtFechaFin']
        carrera = request.form['txtCarrera']
        turno = request.form['txtTurno']
        tutor = request.form['txtTutor']
        cur1 = mysql.connection.cursor()
        cur1.execute("SELECT * FROM grupos_tutores WHERE id_tutor = %s", (tutor,))
        datos = cur1.fetchall()
        cur1.close()
        if datos:
            mensaje2 = "¡El tutor ya está registrado en otro grupo!"
            return redirect(url_for('registro_grupo', mensaje2 = mensaje2))
        else:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO grupos (nombre, fecha_inicio, fecha_fin, id_carrera, id_turno) VALUES (%s, %s, %s, %s, %s)", (nombre, fecha_ini, fecha_fin, carrera, turno))
            last_id = cur.lastrowid
            cur.execute("INSERT INTO grupos_tutores (id_grupo, id_tutor) VALUES (%s, %s)", (last_id, tutor))
            mysql.connection.commit()
            cur.close()
            mensaje1 = "Grupo registrado con exito"
            return redirect(url_for('registro_grupo', mensaje1 = mensaje1))
    elif 'logueado' in session and session['id_rol'] != 1:
        print("No tienes permisos para acceder a esta seccion")
        return redirect(url_for('logout')) 
    else:
        return redirect(url_for('login'))  

#Ruta para crear registro de director
@app.route('/crear-registro-director', methods=["GET", "POST"])
def crear_registro_director():
    if 'logueado' in session and session['id_rol'] == 1:
        nombre = request.form['txtNombre']
        apellidos = request.form['txtApellidos']
        correo = request.form['txtCorreo']
        password = request.form['txtPassword']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO personas (nombre, apellidos, correo, password, id_rol) VALUES (%s, %s, %s, %s,'2')",(nombre, apellidos, correo, password))
        mysql.connection.commit()
        cur.close()
        mensaje1 = "¡Director registrado con exito!"
        return redirect(url_for('registro_director', mensaje1 = mensaje1))
    elif 'logueado' in session and session['id_rol'] != 1:
        print("No tienes permisos para acceder a esta seccion")
        return redirect(url_for('logout')) 
    else:
        return redirect(url_for('login')) 

#Ruta para crear registro de director desde la pagina del registro de division
@app.route('/crear-registro-director-division', methods=["GET", "POST"])
def crear_registro_director_division():
    if 'logueado' in session and session['id_rol'] == 1:
        nombre = request.form['txtNombre']
        apellidos = request.form['txtApellidos']
        correo = request.form['txtCorreo']
        password = request.form['txtPassword']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO personas (nombre, apellidos, correo, password, id_rol) VALUES (%s, %s, %s, %s,'2')",(nombre, apellidos, correo, password))
        mysql.connection.commit()
        cur.close()
        mensaje1 = "¡Director registrado con exito!"
        return redirect(url_for('registro_division', mensaje1 = mensaje1))
    elif 'logueado' in session and session['id_rol'] != 1:
        print("No tienes permisos para acceder a esta seccion")
        return redirect(url_for('logout')) 
    else:
        return redirect(url_for('login'))

#Ruta para crear registro de tutor
@app.route('/crear-registro-tutor', methods=["GET", "POST"])
def crear_registro_tutor():
    if 'logueado' in session and session['id_rol'] == 1:
        nombre = request.form['txtNombre']
        apellidos = request.form['txtApellidos']
        correo = request.form['txtCorreo']
        password = request.form['txtPassword']
        cur1 = mysql.connection.cursor()
        cur1.execute("SELECT * FROM personas WHERE correo = %s", (correo,))
        datos1 = cur1.fetchall()
        cur1.close()
        if datos1:
            mensaje1 = "La el correo: " + correo + " ya se encuentra registrada"
            return redirect(url_for('registro_tutor', mensaje1 = mensaje1))        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO personas (nombre, apellidos, correo, password, id_rol) VALUES (%s, %s, %s, %s,'3')",(nombre, apellidos, correo, password))
        mysql.connection.commit()
        cur.close()
        mensaje2 = "Tutor registrado con exito!"
        return redirect(url_for('registro_tutor', mensaje2 = mensaje2))
    elif 'logueado' in session and session['id_rol'] != 1:
        print("No tienes permisos para acceder a esta seccion")
        return redirect(url_for('logout')) 
    else:
        return redirect(url_for('login')) 
 
#Ruta para crear registro desde la pagina del registro de grupo
@app.route('/crear-registro-tutor-grupo', methods=["GET", "POST"])
def crear_registro_tutor_grupo():
    if 'logueado' in session and session['id_rol'] == 1:
        nombre = request.form['txtNombre']
        apellidos = request.form['txtApellidos']
        correo = request.form['txtCorreo']
        password = request.form['txtPassword']
        cur1 = mysql.connection.cursor()
        cur1.execute("SELECT * FROM personas WHERE correo = %s", (correo,))
        datos1 = cur1.fetchall()
        cur1.close()
        if datos1:
            mensaje1 = "La el correo: " + correo + " ya se encuentra registrada"
            return redirect(url_for('registro_grupo', mensaje1 = mensaje1))        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO personas (nombre, apellidos, correo, password, id_rol) VALUES (%s, %s, %s, %s,'3')",(nombre, apellidos, correo, password))
        mysql.connection.commit()
        cur.close()
        mensaje2 = "Tutor registrado con exito!"
        return redirect(url_for('registro_grupo', mensaje2 = mensaje2))
    elif 'logueado' in session and session['id_rol'] != 1:
        print("No tienes permisos para acceder a esta seccion")
        return redirect(url_for('logout')) 
    else:
        return redirect(url_for('login')) 

#Ruta para crear registro de alumno
@app.route('/crear-registro-alumno', methods=["GET", "POST"])
def crear_registro_alumno():
    if 'logueado' in session and session['id_rol'] == 1:
        nombre = request.form['txtNombre']
        apellidos = request.form['txtApellidos']
        correo = request.form['txtCorreo']
        password = request.form['txtPassword']
        carrera = request.form['txtCarrera']
        codigo = request.form['txtMatricula']
        cur1 = mysql.connection.cursor()
        cur1.execute("SELECT * FROM personas WHERE codigo = %s", (codigo,))
        datos1 = cur1.fetchall()
        cur1.close()
        if datos1:
            mensaje1 = "La matricula: " + codigo + " ya se encuentra registrada"
            return redirect(url_for('registro_alumno', mensaje1 = mensaje1))
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT * FROM personas WHERE correo = %s", (correo,))
        datos2 = cur2.fetchall()
        cur2.close()
        if datos2:
            mensaje2 = "El correo: " + correo + " ya se encuentra registrado"
            return redirect(url_for('registro_alumno', mensaje2 = mensaje2))        
        cur3 = mysql.connection.cursor()
        cur3.execute("INSERT INTO personas (nombre, apellidos, correo, password, codigo, id_carrera, id_rol) VALUES (%s, %s, %s, %s, %s, %s,'4')",(nombre, apellidos, correo, password, codigo, carrera))
        mysql.connection.commit()
        cur3.close()
        mensaje3 = "Alumno registrado correctamente"
        return redirect(url_for('registro_alumno', mensaje3 = mensaje3))
    elif 'logueado' in session and session['id_rol'] != 1:
        print("No tienes permisos para acceder a esta seccion")
        return redirect(url_for('logout')) 
    else:
        return redirect(url_for('login'))

#ruta para vincular alumnos a sus grupos
@app.route('/vincular-alumno-grupo', methods=['GET', 'POST'])
def vincular_alumno_grupo():
    nombreCarrera = request.form['txtNombreCarrera']  
    id_del_alumno = request.form['txtAlumnoV']
    id_del_grupo = request.form['txtGrupoV']
    carrera_buscar = request.form['txtCarreraGrupo']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO grupos_alumnos (id_grupo, id_alumno) VALUES (%s, %s)", (id_del_grupo, id_del_alumno))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('registrar_alumnos_grupo', id_del_grupo = id_del_grupo, carrera_buscar = carrera_buscar, nombreCarrera = nombreCarrera))

#Ruta para consultar permisos pendientes del tutor
@app.route('/permisos-pendientes-tutor')
def per_pendientes_tutor():
    cons_permisos = permisos_pendientes_tutor()
    ver_permisos = permisos_pendientes_tutor_modal()
    return render_template('tutor/per_pendientes_tutor.html', permisos = cons_permisos, ver_permisos = ver_permisos)

#Ruta para funcionalidad del botón aceptar permiso por parte del tutor
@app.route('/aceptar-permiso-tutor/<id_permiso>', methods=["POST"])
def acpt_permiso_tutor(id_permiso):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE permisos SET revisado_tutor = 2 WHERE id_permiso = (%s)", (id_permiso,))
    mysql.connection.commit()
    cur.close()
    cons_permisos = permisos_pendientes_tutor()
    return render_template('tutor/per_pendientes_tutor.html', permisos = cons_permisos)

#Ruta para funcionalidad del botón rechazar permiso por parte del tutor
@app.route('/rechazar-permiso-tutor/<id_permiso>', methods=["POST"])
def rzd_permiso_tutor(id_permiso):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE permisos SET revisado_tutor = 3, id_estatus = 3 WHERE id_permiso = (%s)", (id_permiso,))
    mysql.connection.commit()
    cur.close()
    cons_permisos = permisos_pendientes_tutor()
    return render_template('tutor/per_pendientes_tutor.html', permisos = cons_permisos)

#Ruta para consultar permisos aceptados del tutor
@app.route('/per-acpt-tutor')
def per_acpt_tutor():
    per_acpt = permisos_aceptados_tutor()
    return render_template('tutor/per_aceptados_tutor.html', aceptados = per_acpt)

#Ruta para consultar permisos rechazados del tutor
@app.route('/per-rzd-tutor')
def per_rzd_tutor():
    per_rzd = permisos_rechazados_tutor()
    return render_template('tutor/per_rechazados_tutor.html', rechazados = per_rzd)

#Ruta para filtrar los permisos aceptados del tutor por mes
@app.route('/filtrar-por-mes-per-acpt', methods=['POST'])
def filtrar_por_mes_per_acpt():
    idtutor = session['id_persona']
    mes = request.form['mes-filter']
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.id_permiso, p.fecha_solicitud, p.fechas_solicitadas, per.nombre AS nombre_alumno, per.apellidos, ets.nombre AS nombre_estatus, p.revisado_tutor, grup.nombre AS nombre_grupo
        FROM permisos p
        JOIN personas per ON per.id_persona = p.id_persona
        JOIN estatus ets ON p.revisado_tutor = ets.id_estatus
        JOIN grupos_alumnos g_a ON g_a.id_alumno = per.id_persona
        JOIN grupos grup ON grup.id_grupo = g_a.id_grupo
        JOIN grupos_tutores g_t ON g_t.id_grupo = grup.id_grupo
        WHERE p.revisado_tutor = 2 AND g_t.id_tutor = (%s) AND MONTH(p.fecha_solicitud) = (%s)""", (idtutor, mes))
    per_acpt = cur.fetchall()
    cur.close()
    return render_template('tutor/per_aceptados_tutor.html', aceptados = per_acpt)

#Ruta para filtrar los permisos rechazados del tutor por mes
@app.route('/filtrar-por-mes-per-rzds', methods=['POST'])
def filtrar_por_mes_per_rzds():
    idtutor = session['id_persona']
    mes = request.form['mes-filter']
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.id_permiso, p.fecha_solicitud, p.fechas_solicitadas, per.nombre AS nombre_alumno, per.apellidos, ets.nombre AS nombre_estatus, p.revisado_tutor, grup.nombre AS nombre_grupo
        FROM permisos p
        JOIN personas per ON per.id_persona = p.id_persona
        JOIN estatus ets ON p.revisado_tutor = ets.id_estatus
        JOIN grupos_alumnos g_a ON g_a.id_alumno = per.id_persona
        JOIN grupos grup ON grup.id_grupo = g_a.id_grupo
        JOIN grupos_tutores g_t ON g_t.id_grupo = grup.id_grupo
        WHERE p.revisado_tutor = 3 AND g_t.id_tutor = (%s) AND MONTH(p.fecha_solicitud) = (%s)""", (idtutor, mes))
    per_rzd = cur.fetchall()
    cur.close()
    return render_template('tutor/per_rechazados_tutor.html', rechazados = per_rzd)

#ruta para loguear usuarios
@app.route('/login', methods=["GET", "POST"])
def login():
    datosClima = clima()
    if request.method == 'POST' and 'txtCorreo' in request.form and 'txtPassword':
        _correo = request.form['txtCorreo']
        _password = request.form['txtPassword']
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM personas WHERE correo = %s AND password = %s", (_correo, _password))
            account = cur.fetchone()
        except Exception:
            return render_template("iniciar_sesion/login.html", mensaje = "No se pudo establecer la conexion a la base de datos", datos = datosClima)
        if account:
            session['logueado'] = True
            session['id_persona'] = account['id_persona']
            session['id_rol'] = account['id_rol']
            session['nombre'] = account['nombre']
            session['apellidos'] = account['apellidos']
            session['correo'] = account['correo']
            session['pas'] = account['password']
            session['codigo'] = account['codigo']
            session['carrera'] = account['id_carrera']
            if session['id_rol'] == 1:
                return redirect(url_for('admin'))
            elif session['id_rol'] == 2:
                return redirect(url_for('director'))
            elif session['id_rol'] == 3:
                return redirect(url_for('per_pendientes_tutor'))
            elif session['id_rol'] == 4:
                return redirect(url_for('registro_permiso'))
        else:
            return render_template("iniciar_sesion/login.html", mensaje = "Datos incorrectos", datos = datosClima)
    return render_template("iniciar_sesion/login.html", datos = datosClima)

#Ruta para cerrar sesion
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

#consultar divisiones y sus directores para mostrar en la pagina
def consultar_divisiones_con_directores():
    cur = mysql.connection.cursor()
    consulta = """
        SELECT divisiones.nombre AS nom_division, personas.nombre AS nom_director, personas.apellidos AS ape_director
        FROM divisiones_directores
        INNER JOIN divisiones ON divisiones_directores.id_division = divisiones.id_division
        INNER JOIN personas ON divisiones_directores.id_director = personas.id_persona;
    """
    cur.execute(consulta)
    datos = cur.fetchall()
    cur.close()
    return datos

#consultar divisiones para mostrar en el formulario de carreras
def consultar_divisiones_individuales():
    cur = mysql.connection.cursor()
    consulta = """
        SELECT * FROM divisiones  
    """
    cur.execute(consulta)
    datos = cur.fetchall()
    cur.close()
    return datos
  
#consultar directores para mostrar en el formulario de division
def consultar_directores_individuales():
    cur = mysql.connection.cursor()
    consulta = """
        SELECT * FROM personas WHERE id_rol = 2   
    """
    cur.execute(consulta)
    datos = cur.fetchall()
    cur.close()
    return datos    

#consultar carreras con su division para mostrar en la pagina de carreras
def consultar_carreras_con_division():
    cur = mysql.connection.cursor()
    consulta = """
        SELECT carreras.id_carrera AS id_carrera, carreras.nombre AS nombre, divisiones.nombre AS nombre_div FROM carreras
        INNER JOIN divisiones ON carreras.id_division = divisiones.id_division       
    """
    cur.execute(consulta)
    datos = cur.fetchall()
    cur.close()
    return datos   

#consultar turnos para mostrar en el formulario de grupos
def consultar_turnos_individuales():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM turnos")
    datos = cur.fetchall()
    cur.close()
    return datos

#consultar tutores para mostrarlo en la pagina de tutores y formulario de grupos
def consultar_tutores_individuales():
    cur = mysql.connection.cursor()
    consulta = """
        SELECT * FROM personas WHERE id_rol = 3
    """
    cur.execute(consulta)
    datos = cur.fetchall()
    cur.close()
    return datos

#consultar grupos para mostrarlo en la pagina de grupos
def prueba_grupos():
    cur = mysql.connection.cursor()
    consulta = """
        SELECT grupos.id_grupo AS grupoid, grupos.nombre AS nombre_grupo, carreras.nombre AS nombre_carrera, divisiones.nombre AS nombre_division, carreras.id_carrera AS carreraid,
        grupos.fecha_inicio AS fecha_ini_cuat, grupos.fecha_fin AS fecha_fin_cuat, turnos.nombre AS nombre_turno
        FROM grupos
        INNER JOIN carreras ON grupos.id_carrera = carreras.id_carrera
        INNER JOIN divisiones ON carreras.id_division = divisiones.id_division
        INNER JOIN turnos ON grupos.id_turno = turnos.id_turno        
    """
    cur.execute(consulta)
    datos = cur.fetchall()
    cur.close()
    return datos

#consultar grupos - tutores para mostrar en tarjeta de grupos
def datos_grupos_t():
    cur = mysql.connection.cursor()
    consulta = """
        SELECT grupos.id_grupo AS grupoid, grupos.fecha_inicio AS fecha_ini_cuat, grupos.fecha_fin AS fecha_fin_cuat, grupos.nombre AS nombre_grupo, carreras.nombre AS nombre_carrera, carreras.id_carrera AS carreraid, divisiones.nombre AS nombre_division, personas.nombre AS nombre_tutor, personas.apellidos
        AS apellidos_tutor, personas.id_persona AS id_tutor, personas.correo AS correo_tutor, personas.password AS pwd_tutor,
        turnos.nombre AS nombre_turno
        FROM grupos_tutores
        INNER JOIN grupos ON grupos_tutores.id_grupo = grupos.id_grupo
        INNER JOIN carreras ON grupos.id_carrera = carreras.id_carrera
        INNER JOIN divisiones ON carreras.id_division = divisiones.id_division
        INNER JOIN personas ON grupos_tutores.id_tutor = personas.id_persona
        INNER JOIN turnos ON grupos.id_turno = turnos.id_turno
    """
    cur.execute(consulta)
    datos = cur.fetchall()
    cur.close()
    return datos   

#consultar directores para mostrarlo en el apartado de directores
def prueba_directores():
    cur = mysql.connection.cursor()
    consulta = """
        SELECT personas.nombre AS nombre_director, personas.apellidos AS apellidos_director, personas.correo AS correo_director, personas.password AS pwd_director
        FROM personas
        WHERE id_rol = 2
    """
    cur.execute(consulta)
    datos = cur.fetchall()
    cur.close()
    return datos

#consultar alumnos para mostrarlos en la tabla de alumnos
def prueba_alumnos():
    cur = mysql.connection.cursor()
    consulta = """
        SELECT personas.id_persona AS id_alumno, personas.password AS pwd_alumno, personas.nombre AS nombre_alumno, personas.apellidos AS apellidos_alumno, personas.correo AS correo_alumno, personas.codigo AS matricula_alumno,
        carreras.nombre AS carrera_alumno, divisiones.nombre AS division_alumno
        FROM personas
        INNER JOIN carreras ON personas.id_carrera = carreras.id_carrera
        INNER JOIN divisiones ON carreras.id_division = divisiones.id_division
    """
    cur.execute(consulta)
    datos = cur.fetchall()
    cur.close()
    return datos    

#consultar tipo de permisos para mostrar en el formulario de permisos
def consultar_tipo():
    cur = mysql.connection.cursor()
    consulta = """
        SELECT * FROM tipo_permiso
    """
    cur.execute(consulta)
    datos = cur.fetchall()
    cur.close()
    return datos    

#consultar permisos pendientes del tutor
def permisos_pendientes_tutor():
    idtutor = session['id_persona']
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.id_permiso, p.fecha_solicitud, p.fechas_solicitadas, per.nombre AS nombre_alumno, 
        per.apellidos, ets.nombre AS nombre_estatus, p.revisado_tutor, grup.nombre AS nombre_grupo FROM permisos p
        JOIN personas per ON per.id_persona = p.id_persona
        JOIN estatus ets ON p.revisado_tutor = ets.id_estatus
        JOIN grupos_alumnos g_a ON g_a.id_alumno = per.id_persona
        JOIN grupos grup ON grup.id_grupo = g_a.id_grupo
        JOIN grupos_tutores g_t ON g_t.id_grupo = grup.id_grupo
        WHERE p.revisado_tutor = 1 AND g_t.id_tutor = %s""", (idtutor,))
    datoscons = cur.fetchall()
    cur.close()
    return datoscons

#consultar permisos aceptados del tutor
def permisos_aceptados_tutor():
    idtutor = session['id_persona']
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.id_permiso, p.fecha_solicitud, p.fechas_solicitadas, per.nombre AS nombre_alumno, 
        per.apellidos, ets.nombre AS nombre_estatus, p.revisado_tutor, grup.nombre AS nombre_grupo FROM permisos p
        JOIN personas per ON per.id_persona = p.id_persona
        JOIN estatus ets ON p.revisado_tutor = ets.id_estatus
        JOIN grupos_alumnos g_a ON g_a.id_alumno = per.id_persona
        JOIN grupos grup ON grup.id_grupo = g_a.id_grupo
        JOIN grupos_tutores g_t ON g_t.id_grupo = grup.id_grupo
        WHERE p.revisado_tutor = 2 AND g_t.id_tutor = %s""", (idtutor,))
    datoscons = cur.fetchall()
    cur.close()
    return datoscons

#consultar permisos rechazados del tutor
def permisos_rechazados_tutor():
    idtutor = session['id_persona']
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.id_permiso, p.fecha_solicitud, p.fechas_solicitadas, per.nombre AS nombre_alumno, 
        per.apellidos, ets.nombre AS nombre_estatus, p.revisado_tutor, grup.nombre AS nombre_grupo FROM permisos p
        JOIN personas per ON per.id_persona = p.id_persona
        JOIN estatus ets ON p.revisado_tutor = ets.id_estatus
        JOIN grupos_alumnos g_a ON g_a.id_alumno = per.id_persona
        JOIN grupos grup ON grup.id_grupo = g_a.id_grupo
        JOIN grupos_tutores g_t ON g_t.id_grupo = grup.id_grupo
        WHERE p.revisado_tutor = 3 AND g_t.id_tutor = %s""", (idtutor,))
    datoscons = cur.fetchall()
    cur.close()
    return datoscons

#consultar permisos pendientes del tutor para el modal
def permisos_pendientes_tutor_modal():
    idtutor = session['id_persona']
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.id_permiso, p.fecha_solicitud, p.fechas_solicitadas, per.nombre AS nombre_alumno, car.nombre AS nombre_carrera, divs.nombre AS nombre_division,
        per.apellidos, ets.nombre AS nombre_estatus, p.revisado_tutor, grup.nombre AS nombre_grupo, p.nombre_archivo FROM permisos p
        JOIN personas per ON per.id_persona = p.id_persona
        JOIN carreras car ON car.id_carrera = per.id_carrera
        JOIN estatus ets ON p.revisado_tutor = ets.id_estatus
        JOIN grupos_alumnos g_a ON g_a.id_alumno = per.id_persona
        JOIN grupos grup ON grup.id_grupo = g_a.id_grupo
        JOIN grupos_tutores g_t ON g_t.id_grupo = grup.id_grupo
        JOIN divisiones divs ON divs.id_division = car.id_division
        WHERE p.revisado_tutor = 1 AND g_t.id_tutor = %s""", (idtutor,))
    datoscons = cur.fetchall()
    cur.close()
    return datoscons

#lanzar aplicacion
if __name__ == '__main__':
    app.secret_key="ruben_dc"
    app.run(debug=True, host='0.0.0.0', port=5000, threaded = True)