from ast import If
from flask import Flask, make_response, render_template, request, url_for, redirect, flash
#from flask_uploads import UploadSet, configure_uploads, IMAGES 
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import (current_user, LoginManager, login_user, logout_user, login_required)
import hashlib

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config["UPLOADED_PHOTOS_DEST"] = "static/img"
app.config["SECRET_KEY"] = os.urandom(24)
#photos = UploadSet('photos', IMAGES)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root@localhost:3306/miauCommerce"
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://karengarbim:6959Ck1n@@karengarbim.mysql.pythonanywhere-services.com:3306/karengarbim$miauCommerce"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
 


#INSTANCIAR OBJETO
miauCommerce = SQLAlchemy(app)

app.secret_key = "mi87542"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

#PARA CADA TABELA DO BANCO CRIAR UMA CLASSE

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

    def __init__(self, nome, email, cpf, senha, endereco):
        self.nome = nome
        self.email = email
        self.cpf = cpf
        self.senha = senha
        self.endereco = endereco

#INTEGRAR A CLASSE COM O LOGIN MANAGER
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return str(self.id)

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
    preco = miauCommerce.Column("anuncio_preco",miauCommerce.Float)
    categ_id = miauCommerce.Column("categ_id",miauCommerce.Integer, miauCommerce.ForeignKey("categoria.categ_id"))
    usuario_id = miauCommerce.Column("usuario_id",miauCommerce.Integer, miauCommerce.ForeignKey("usuario.usuario_id"))
    imagem = miauCommerce.Column("anuncio_img",miauCommerce.String(256))
    status_venda = miauCommerce.Column("anuncio_status_vendido",miauCommerce.Boolean)
    status_oferta = miauCommerce.Column("anuncio_status_oferta",miauCommerce.Boolean)


    def __init__(self, status, nome, descricao, qtde, preco, categ_id, usuario_id, imagem, status_venda, status_oferta) :
        self.status = status
        self.nome = nome
        self.descricao = descricao
        self.qtde = qtde
        self.preco = preco
        self.categ_id = categ_id
        self.usuario_id = usuario_id
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
        
        #GERENCIADOR DE LOGIN
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash("Dados Inválidos!")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/")
def index():
    anuncio = Anuncio.query.filter(Anuncio.status == True)
    return render_template("index.html", anuncios = anuncio )

@app.route("/ofertas")
def ofertas():
    anuncio = Anuncio.query.filter(Anuncio.status_oferta == True)
    if Anuncio.status == True and Anuncio.status_venda == False:
        return render_template("ofertas.html", anuncios = anuncio )
    return render_template("ofertas.html", anuncios = anuncio )

@app.route("/cadastro/usuario")
def usuario():
    return render_template("usuario.html", usuarios = Usuario.query.all(), titulo="Cadastro de Usuário")

@app.route("/usuario/novo", methods=["POST"])
def novousuario():
    hash = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()
    usuario = Usuario(request.form.get("nome"), request.form.get("email"), request.form.get("cpf"), hash, request.form.get("endereco"))
    flash(f'Usuário cadastrado com sucesso!', 'success')
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
    return render_template("editusuario.html", usuario = usuario, titulo=" Usuário")

@app.route("/usuario/deletar/<int:id>")
def deletarusuario(id):
    usuario = Usuario.query.get(id)
    miauCommerce.session.delete(usuario)
    miauCommerce.session.commit()
    return redirect(url_for('usuario'))

@app.route("/cadastro/anuncio")
@login_required
def anuncio():
    return render_template("anuncios.html", anuncios = Anuncio.query.all(), categorias = Categoria.query.all(), titulo="Cadastro de Anúncio")

@app.route("/anuncio/novo", methods=["POST"])
def novouanuncio():
    anuncio = Anuncio(True, request.form.get("nome"), request.form.get("descricao"), request.form.get("qtde"), 
        request.form.get("preco"), request.form.get("categ_id"), request.form.get("usuario_id"), request.form.get("imagem"),
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
        anuncio.usuario_id = request.form.get('usuario_id')
        anuncio.status_venda = False
        if request.form.get('status_oferta') == None:
            anuncio.status_oferta = False
        else:
            anuncio.status_oferta = True
        miauCommerce.session.add(anuncio)
        miauCommerce.session.commit()
        return redirect(url_for('anuncio'))
    return render_template("editanuncio.html", anuncio = anuncio, categorias = Categoria.query.all(), titulo=" Anuncio")

@app.route("/anuncio/deletar/<int:id>")
def deletaranuncio(id):
    anuncio = Anuncio.query.get(id)
    miauCommerce.session.delete(anuncio)
    miauCommerce.session.commit()
    return redirect(url_for('anuncio'))

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

@app.route("/relatorio/vendas")
@login_required
def relVendas():
    return render_template("relVendas.html")

@app.route("/relatorio/compras")
@login_required
def relCompras():
    return render_template("relCompras.html")

@app.route("/contato")
def contato():
    return render_template("contato.html")

@app.route("/anuncios/pergunta")
def pergunta():
    return render_template("pergunta.html")

@app.route("/anuncios/compra")
def compra():
    return render_template("anunciosCompra.html")

@app.route("/anuncios/favoritos")
def favoritos():
    return render_template("favoritos.html")


@app.route("/user/<username>")
def username(username):
# escape transformou a variavel username em texto
    print("O que foi passado ", username)
    cok = make_response("<h2>cookie criado</h2")
    cok.set_cookie("username", username)
    return cok

@app.route("/user2/")
@app.route("/user2/<username>")
def username2(username=None):
# render _template é a rota para a pagina html
    cokUsername = request.cookies.get("username")
    print(cokUsername)
    return render_template("user.html",username = username, cokUsername = cokUsername)

if __name__ == '__main__':
    app.run(debug=True)
    miauCommerce.create_all()


#servidor do heroku - publicação