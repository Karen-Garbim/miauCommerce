import secrets
from flask import Flask, make_response, render_template, request, url_for, redirect, flash
#from flask_uploads import UploadSet, configure_uploads, IMAGES
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import (current_user, LoginManager, login_user, logout_user, login_required)
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField, FileRequired
from wtforms import Form, StringField, PasswordField, BooleanField, validators
import hashlib
from flask import session
#import json
#import pdfkit


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root@localhost:3306/miauCommerce"
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://karengarbim:6959Ck1n@@karengarbim.mysql.pythonanywhere-services.com:3306/karengarbim$miauCommerce"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
 


#INSTANCIAR OBJETO
miauCommerce = SQLAlchemy(app)

# para salvar imagens
app.config["UPLOADED_PHOTOS_DEST"] = os.path.join(basedir,"static/img")
app.config["SECRET_KEY"] = 'whatever'
#photos = UploadSet('photos', IMAGES)
#configure_uploads(app, photos)

app.secret_key = "mi87542"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

#PARA CADA TABELA DO BANCO CRIAR UMA CLASSE

#class UploadForm(FlaskForm):
#    file = FileField(validators=[FileRequired])


class Endereco():
    pass


class Usuario(miauCommerce.Model):
    __tablename__ = "usuario"
    id = miauCommerce.Column("usuario_id", miauCommerce.Integer, primary_key=True)
    nome = miauCommerce.Column("usuario_nome",miauCommerce.String(256))
    email = miauCommerce.Column("usuario_email",miauCommerce.String(256))
    cpf = miauCommerce.Column("usuario_cpf",miauCommerce.String(256))
    senha = miauCommerce.Column("usuario_senha",miauCommerce.String(256))
    endereco = miauCommerce.Column("usuario_endereco",miauCommerce.String(256))
    tipoCliente = miauCommerce.Column("tipo_cliente", miauCommerce.String(15))

    def __init__(self, nome, email, cpf, senha, endereco, tipo_cliente):
        self.nome = nome
        self.email = email
        self.cpf = cpf
        self.senha = senha
        self.endereco = endereco
        self.tipoCliente = tipo_cliente

#INTEGRAR A CLASSE COM O LOGIN MANAGER
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return str(self.id)

    def __str__(self):
        return f'({self.nome},{self.email},{self.cpf}, {self.senha}, {self.endereco})'

class Categoria(miauCommerce.Model):
    __tablename__ = "categoria"
    id = miauCommerce.Column("categ_id", miauCommerce.Integer, primary_key=True)
    nome = miauCommerce.Column("categ_nome",miauCommerce.String(256))
    descricao = miauCommerce.Column("categ_descricao",miauCommerce.String(256))

    def __init__(self, nome, descricao):
        self.nome = nome
        self.descricao = descricao

class Anuncio(miauCommerce.Model):
    __tablename__ = "anuncio"
    id = miauCommerce.Column("anuncio_id", miauCommerce.Integer, primary_key=True)
    status = miauCommerce.Column("anuncio_status",miauCommerce.Boolean)
    nome = miauCommerce.Column("anuncio_nome",miauCommerce.String(256))
    descricao = miauCommerce.Column("anuncio_descricao",miauCommerce.String(256))
    qtde = miauCommerce.Column("anuncio_qtde",miauCommerce.Integer)
    preco = miauCommerce.Column("anuncio_preco",miauCommerce.Float(10,2))
    categ_id = miauCommerce.Column("categ_id",miauCommerce.Integer, miauCommerce.ForeignKey("categoria.categ_id"))
    usuario_id = miauCommerce.Column("usuario_id",miauCommerce.Integer, miauCommerce.ForeignKey("usuario.usuario_id"))
    comprador_id = miauCommerce.Column("comprador_id", miauCommerce.Integer, miauCommerce.ForeignKey("usuario.usuario_id", ))
    imagem = miauCommerce.Column("anuncio_img",miauCommerce.String(150),  default='imagem.jpg')
    status_venda = miauCommerce.Column("anuncio_status_vendido",miauCommerce.Boolean)
    status_oferta = miauCommerce.Column("anuncio_status_oferta",miauCommerce.Boolean)


    def __init__(self, status, nome, descricao, qtde, preco, categ_id, usuario_id, comprador_id, imagem, status_venda, status_oferta) :
        self.status = status
        self.nome = nome
        self.descricao = descricao
        self.qtde = qtde
        self.preco = preco
        self.categ_id = categ_id
        self.usuario_id = usuario_id
        self.comprador_id = comprador_id
        self.imagem = imagem
        self.status_venda = status_venda
        self.status_oferta = status_oferta


class Favoritos(miauCommerce.Model):
    __tablename__ = "favoritos"
    id = miauCommerce.Column("favoritos_id", miauCommerce.Integer, primary_key=True)
    usuario_id = miauCommerce.Column("usuario_id",miauCommerce.Integer, miauCommerce.ForeignKey("usuario.usuario_id"))
    anuncio_id = miauCommerce.Column("anuncio_id",miauCommerce.Integer, miauCommerce.ForeignKey("anuncio.anuncio_id"))

    def __init__(self, usuario_id, anuncio_id):
        self.usuario_id = usuario_id
        self.anuncio_id = anuncio_id


class Pergunta(miauCommerce.Model):
    __tablename__ = "pergunta"
    id = miauCommerce.Column("pergunta_id", miauCommerce.Integer, primary_key=True)
    usuario_id = miauCommerce.Column("usuario_id",miauCommerce.Integer, miauCommerce.ForeignKey("usuario.usuario_id"))
    anuncio_id = miauCommerce.Column("anuncio_id",miauCommerce.Integer, miauCommerce.ForeignKey("anuncio.anuncio_id"))
    per_pergunta = miauCommerce.Column("per_pergunta",miauCommerce.String(256))
    per_resposta = miauCommerce.Column("per_resposta",miauCommerce.String(256))


    def __init__(self, usuario_id, anuncio_id, per_pergunta, per_resposta):
        self.usuario_id = usuario_id
        self.anuncio_id = anuncio_id
        self.per_pergunta = per_pergunta
        self.per_resposta = per_resposta


@app.errorhandler(404)
def paginanaoencontrada(error):
    return render_template('pagnaoencontrada.html')

#CHAMADA PARA CARREGAR O USUARIO
@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(id)


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()
        
        user = Usuario.query.filter_by(email=email, senha=senha).first()
        print("Teste nome usuario", user)
        #GERENCIADOR DE LOGIN
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash("Dados Inv??lidos!")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/")
def index():
    anuncio = Anuncio.query.filter(Anuncio.status == True, Anuncio.status_venda == False)
    categoria = Categoria.query.all()
    if current_user.is_authenticated:
        categoria = Categoria.query.all()
        favorito = Favoritos.query.filter_by(usuario_id = current_user.id).all()
        return render_template("index.html", anuncios = anuncio, favoritos = favorito, categoria = categoria)
    return render_template("index.html", anuncios = anuncio, categoria = categoria)

@app.route("/ofertas")
def ofertas():
    anuncio = Anuncio.query.filter(Anuncio.status_oferta == True, Anuncio.status == True, Anuncio.status_venda == False)
    return render_template("ofertas.html", anuncios = anuncio )


@app.route("/cadastro/usuario")
def usuario():
    return render_template("usuario.html", usuarios = Usuario.query.all(), titulo="Cadastro de Usu??rio")



@app.route("/usuario/novo", methods=["POST"])
def novousuario():
    hash = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()
    usuario = Usuario(request.form.get("nome"), request.form.get("email"), request.form.get("cpf"), hash, request.form.get("endereco"), "cliente")
    flash(f'Usu??rio cadastrado com sucesso!', 'success')
    miauCommerce.session.add(usuario)
    miauCommerce.session.commit()
    return redirect(url_for('usuario'))

@app.route("/usuario/detalhes/<int:id>")
def buscausuario(id):
    usuario = Usuario.query.get(id)
    return usuario.nome

@app.route("/usuario/editar/<int:id>", methods = ['GET', 'POST'])
def editarusuario(id):
    usuario = Usuario.query.get(id)
    if request.method == 'POST':
        usuario.nome = request.form.get('nome')
        usuario.email = request.form.get('email')
        usuario.cpf = request.form.get('cpf')
        usuario.senha = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()
        usuario.endereco = request.form.get('endereco')
        miauCommerce.session.add(usuario)
        miauCommerce.session.commit()
        return redirect(url_for('usuario'))
    return render_template("editusuario.html", usuario = usuario, titulo=" Usu??rio")

@app.route("/usuario/deletar/<int:id>")
def deletarusuario(id):
    usuario = Usuario.query.get(id)
    miauCommerce.session.delete(usuario)
    miauCommerce.session.commit()
    return redirect(url_for('usuario'))

@app.route("/cadastro/anuncio")
@login_required
def anuncio():
    return render_template("anuncios.html", anuncios = Anuncio.query.all(), categorias = Categoria.query.all(), titulo="Cadastro de An??ncio")

@app.route("/anuncio/novo", methods=["POST"])
def novouanuncio():
    anuncio = Anuncio(True, request.form.get("nome"), request.form.get("descricao"), request.form.get("qtde"), 
        request.form.get("preco"), request.form.get("categ_id"), current_user.id, None, request.form.get("imagem"),
        False, False)
    miauCommerce.session.add(anuncio)
    miauCommerce.session.commit()
    return redirect(url_for('anuncio'))

@app.route("/anuncio/editar/<int:id>", methods = ['GET', 'POST'])
def editaranuncio(id):
    anuncio = Anuncio.query.get(id)
    if request.method == 'POST':
        if request.form.get('status') == None:
            anuncio.status = False
        else:
            anuncio.status = True
        anuncio.nome = request.form.get('nome')
        anuncio.descricao = request.form.get('descricao')
        anuncio.qtde = request.form.get('qtde')
        anuncio.preco = request.form.get('preco')
        anuncio.categ_id = request.form.get('categ_id')
        anuncio.usuario_id = current_user.id
        anuncio.comprador_id = None
        anuncio.status_venda = False
        if request.form.get('status_oferta') == None:
            anuncio.status_oferta = False
        else:
            anuncio.status_oferta = True
        miauCommerce.session.add(anuncio)
        miauCommerce.session.commit()
        return redirect(url_for('anuncio'))
    return render_template("editanuncio.html", anuncio = anuncio, categorias = Categoria.query.all(), titulo=" Anuncio")

@app.route("/anuncio/detalhesAnuncio/<int:id>")
def detalhesAnuncio(id):
    anuncio = Anuncio.query.get_or_404(id)
    return render_template("detalhesAnuncio.html", anuncio = anuncio)

@app.route("/anuncio/deletar/<int:id>")
def deletaranuncio(id):
    anuncio = Anuncio.query.get(id)
    miauCommerce.session.delete(anuncio)
    miauCommerce.session.commit()
    return redirect(url_for('anuncio'))

@app.route("/anuncio/meusAnuncios")
@login_required
def meusAnuncios():
    return render_template("meusAnuncios.html", anuncios = Anuncio.query.filter_by(usuario_id = current_user.id).all())

@app.route("/anuncio/compras/<int:id>")
@login_required
def comprar(id):
    anuncio = Anuncio.query.get(id)
    anuncio.status_venda = True
    anuncio.comprador_id = current_user.id
    miauCommerce.session.add(anuncio)
    miauCommerce.session.commit()
    return redirect(url_for('relCompras'))

@app.route("/anuncios/pergunta/<int:id>", methods = ["GET"])
def pergunta(id):
    if current_user.is_authenticated:
        anuncio = Anuncio.query.get_or_404(id)
        pergunta = miauCommerce.session.query(Pergunta, Usuario)\
            .add_columns(Usuario.nome, Pergunta.per_pergunta, Pergunta.per_resposta)\
            .filter(Usuario.id == Pergunta.usuario_id, Pergunta.anuncio_id == id).all()
        return render_template("pergunta.html", anuncio = anuncio, pergunta = pergunta)

@app.route("/anuncios/gravarpergunta/", methods = ['POST'])
def gravarPergunta():
    anuncio = Anuncio.query.get(request.form.get('id_anuncio'))
    if current_user.is_authenticated:    
        if current_user.id == anuncio.usuario_id:
            pergunta = Pergunta(current_user.id, request.form.get('id_anuncio'), request.form.get('per_pergunta'), None)
            miauCommerce.session.add(pergunta)
            miauCommerce.session.commit()
        else:
            pergunta = Pergunta(current_user.id, request.form.get('id_anuncio'), None, request.form.get('per_pergunta'))
            miauCommerce.session.add(pergunta)
            miauCommerce.session.commit()
        return redirect(url_for('pergunta', id = anuncio.id))
        

@app.route("/anuncio/favoritos/<int:id>", methods=["POST", "GET"])
@login_required
def addFavoritos(id):
    consulta = Favoritos.query.filter_by(usuario_id = current_user.id, anuncio_id = id).first()
    favorito = Favoritos(current_user.id, id)
    if consulta is None:
        flash(f'An??ncio adicionado aos favoritos!', 'success')
        miauCommerce.session.add(favorito)
    else:
        flash(f'An??ncio removido dos favoritos!', 'success')
        miauCommerce.session.delete(consulta)
    miauCommerce.session.commit()
    return redirect(url_for('index'))

@app.route("/anuncios/favoritos")
@login_required
def favoritos():
    anunciosFavoritos = miauCommerce.session.query(Anuncio, Favoritos)\
        .add_columns(Anuncio.nome, Anuncio.preco, Anuncio.id)\
        .filter(Anuncio.id == Favoritos.anuncio_id, Favoritos.usuario_id == current_user.id).all()
    return render_template("favoritos.html", anuncios = anunciosFavoritos)

@app.route("/config/categoria")
@login_required
def categoria():
    return render_template("categoria.html", categorias = Categoria.query.all(), categoria = categoria, titulo="Categoria")

@app.route("/categoria/novo", methods=["POST"])
@login_required
def novacategoria():
    categoria = Categoria(request.form.get("nome"), request.form.get("descricao"))
    miauCommerce.session.add(categoria)
    miauCommerce.session.commit()
    return redirect(url_for('categoria'))

@app.route("/categoria/editar/<int:id>", methods = ['GET', 'POST'])
@login_required
def editarcategoria(id):
    categoria = Categoria.query.get(id)
    if request.method == 'POST':
        categoria.nome = request.form.get('nome')
        categoria.descricao = request.form.get('descricao')
        miauCommerce.session.add(categoria)
        miauCommerce.session.commit()
        return redirect(url_for('categoria'))
    return render_template("editcategoria.html", categoria = categoria, titulo=" Categoria")

@app.route("/categoria/deletar/<int:id>")
def deletarcategoria(id):
    categoria = Categoria.query.get(id)
    miauCommerce.session.delete(categoria)
    miauCommerce.session.commit()
    return redirect(url_for('categoria'))

@app.route("/categoria/<int:id>")
def get_categoria(id):
    AnuncioCategoria = Anuncio.query.filter_by(categ_id = id)
    return render_template('index.html', anunciocategoria = AnuncioCategoria)

@app.route("/relatorio/admin")
@login_required
def relAdmin():
    return render_template("relatorios.html", usuarios = Usuario.query.all(), categorias = Categoria.query.all(), anuncios = Anuncio.query.all())

@app.route("/relatorio/vendas")
@login_required
def relVendas():
    anuncio = Anuncio.query.filter(Anuncio.status_venda == True, Anuncio.usuario_id == current_user.id)
    return render_template("vendas.html", anuncios = anuncio )


@app.route("/relatorio/compras")
@login_required
def relCompras():
    anuncio = Anuncio.query.filter(Anuncio.status_venda == True, Anuncio.comprador_id == current_user.id)
    return render_template("compras.html", anuncios = anuncio)


#if __name__ == 'app':
#    miauCommerce.create_all()

if __name__ == '__main__':
    app.run(debug=True)
    miauCommerce.create_all()