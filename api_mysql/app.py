from flask import Flask, Response, request
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/reservas'
app.config['SECRET_KEY'] = 'uma-chave-bem-segura'

db = SQLAlchemy(app)

class Reserva(db.Model):
    nome = db.Column(db.String(50))
    email = db.Column(db.String(100), primary_key = True)
    mesa = db.Column(db.Integer)
    data = db.Column(db.String(10))
    hora = db.Column(db.String(5))
    qtd_pessoas = db.Column(db.Integer)

    def to_json(self):
        return {"nome": self.nome, "email": self.email, "mesa": self.mesa,
                "data": self.data, "hora": self.hora, "qtd_pessoas": self.qtd_pessoas}

class Form_Reserva(FlaskForm):
    nome = StringField('nome', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    mesa = StringField('mesa', validators=[DataRequired()])
    data = StringField('data', validators=[DataRequired()])
    hora = StringField('hora', validators=[DataRequired()])
    qtd_pessoas = StringField('qtd_pessoas', validators=[DataRequired()])

    def to_json(self):
        return {"nome": self.nome, "email": self.email, "mesa": self.mesa,
                "data": self.data, "hora": self.hora, "qtd_pessoas": self.qtd_pessoas}

#seleciona reservas
@app.route("/reserva", methods=["GET"])
def listar_reserva():
    reservas_objetos = Reserva.query.all()
    reservas_json = [reserva.to_json() for reserva in reservas_objetos]
    print(reservas_json)

    return gera_response(200, "reservas", reservas_json, "Reservas listadas")

#seleciona reserva individual
@app.route("/reserva/<email>", methods=["GET"])
def seleciona_reserva(email):
    reserva_objeto = Reserva.query.filter_by(email=email).first()
    reserva_json = reserva_objeto.to_json()

    return gera_response(200, "reserva", reserva_json)   

#cadastro
@app.route("/", methods=["GET", "POST"])
def index():
    form = Form_Reserva.to_json()
    body = request.get_json()

    if("nome" not in body):
        return gera_response(400, "O par??metro nome ?? obrigat??rio!")

    if("email" not in body):
        return gera_response(400, "O par??metro email ?? obrigat??rio!")

    if("data" not in body):
        return gera_response(400, "O par??metro data ?? obrigat??rio!")

    if("hora" not in body):
        return gera_response(400, "O par??metro hora ?? obrigat??rio!")
    
    if("qtd_pessoas" not in body):
        return gera_response(400, "O par??metro qtd_pessoas ?? obrigat??rio!")
    
    if("mesa" not in body):
        return gera_response(400, "O par??metro mesa ?? obrigat??rio!")

    if request.method == 'POST' and form.validate_on_submit():
        reserva = Reserva(form.nome.data, form.email.data, form.mesa.data, form.data.data, 
                            form.hora.data, form.qtd_pessoas.data)
        db.session.add(reserva)
        db.session.commit()
        return gera_response(201, "reserva", reserva.to_json(), "Reserva realizada!")
    return render_template('romeu.html', form=form)
    
# Atualizar reserva
@app.route("/reserva/<email>", methods=["PUT"])
def atualiza_reserva(email):
    #pega a reserva
    reserva_objeto = Reserva.query.filter_by(email=email).first()
    #pega as modifica????es
    body = request.get_json()

    try:
        if('nome' in body):
            reserva_objeto.nome = body['nome']
        if('mesa' in body):
            reserva_objeto.mesa = body['mesa']
        if('data' in body):
            reserva_objeto.data = body['data']
        if('hora' in body):
            reserva_objeto.hora = body['hora']
        if('qtd_pessoas' in body):
            reserva_objeto.qtd_pessoas = body['qtd_pessoas']

        db.session.add(reserva_objeto)
        db.session.commit()
        return gera_response(200, "reserva", reserva_objeto.to_json(), "Atualizado com sucesso!")
    except Exception as e:
        print('Erro', e)
        return gera_response(400, "reserva", {}, "Erro ao atualizar!")

#Deleta reserva
@app.route("/reserva/<email>", methods=["DELETE"])
def deleta_reserva(email):
    reserva_objeto = Reserva.query.filter_by(email=email).first()

    try:
        db.session.delete(reserva_objeto)
        db.session.commit()
        return gera_response(200, "reserva", reserva_objeto.to_json(), "Deletado com sucesso!")
    except Exception as e:
        print('Erro', e)
        return gera_response(400, "reserva", {}, "Erro ao deletar!")


def gera_response(status, nome_do_conteudo, conteudo, mensagem=False):
    body = {}
    body[nome_do_conteudo] = conteudo

    if(mensagem):
        body["mensagem"] = mensagem

    return Response(json.dumps(body), status=status, mimetype="application/json")

app.run()