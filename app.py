import traceback
from flask import Flask, render_template, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from io import BytesIO
from base64 import b64encode
import qrcode
from flask_wtf import FlaskForm
from wtforms import SelectField

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db.init_app(app)


# Модель
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    who = db.Column(db.Text(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return '<Article %r>' % self.id


# Модель
class Cartridge(db.Model):
    id_card = db.Column(db.Integer, primary_key=True)
    unit_card = db.Column(db.String(50), nullable=False)
    model_card = db.Column(db.String(50), nullable=False)
    date_card = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return 'Claim %r' % self.id


# Модель
class Department(db.Model):
    id_depart = db.Column(db.Integer, primary_key=True)
    unit_depart = db.Column(db.String(70), nullable=False)

    def __repr__(self):
        return '<Department %r>' % self.id


# Модель
class ModelCartridge(db.Model):
    id_model = db.Column(db.Integer, primary_key=True)
    model_ = db.Column(db.String(70), nullable=False)

    def __repr__(self):
        return '<ModelCartridge %r>' % self.id


@app.route('/')
def index():
    """q = request.args.get('q')
    if q:
        posts = claim.query.filter(claim.title.constains(q) | claim.body.constains(q)).all()
    else:
        posts = claim.query.all()"""
    return render_template("index.html")


@app.route('/qr_code', methods=['GET', 'POST'])  #главная страница
def qr_code():
    memory = BytesIO()
    data = request.form.get('link')
    img = qrcode.make(data)
    img.save(memory)
    memory.seek(0)

    base64_img = "data:image/png;base64," + \
                 b64encode(memory.getvalue()).decode('ascii')

    return render_template("qr_code.html", data=base64_img)


#________________________________________Картриджи______________________________________________________________

@app.route('/create_claim', methods=['POST', 'GET'])  # стр заявки
def create_claim():
    # modelcartridges = ModelCartridge.query.all()
    departments = Department.query.all()
    if request.method == "POST":
        unit_card = request.form['unit_card']
        model_card = request.form['model_card']
        cartridge = Cartridge(unit_card=unit_card, model_card=model_card)
        try:
            db.session.add(cartridge)  #добавляем объект
            db.session.commit()  #  сохраняем объект

            return redirect('/claim')
        finally:
            traceback.format_exc()
    else:
        return render_template("create_claim.html", departments=departments)


@app.route('/claim/<int:id_card>/update', methods=['POST', 'GET'])  # редактирование заявки
def claim_update(id_card):
    cartridge = Cartridge.query.get(id_card)  # нашли нужный объект
    if request.method == "POST":
        cartridge.unit_card = request.form['unit_card']  # для этого объекта меняем значение
        cartridge.model_card = request.form['model_card']

        try:
            db.session.commit()  #  обновляем объекты бд
            return redirect('/claim')
        except:
            return "При редактировании произошла ошибка :("
    else:
        return render_template("claim_update.html", cartridge=cartridge)


@app.route('/claim')
def claim():
    cartridges = Cartridge.query.order_by()
    
    """ .first() только первая запись отображается/
        метод order_by отображает все записи, внутри метода стоит сортировка по дате
    """
    return render_template("claim.html", cartridges=cartridges)
    # про вывод: в первый шаблон articles передается список со второго =articles


@app.route('/claim/<int:id_card>')  # Обработка адреса для кнопки "обзор"
def claim_detail(id_card):
    cartridge = Cartridge.query.get(id_card)  # получаем объект по его айди
    return render_template("claim_detail.html", cartridge=cartridge)


@app.route('/claim/<int:id_card>/delete')  # редактировние заявок
def claim_delete(id_card):
    cartridge = Cartridge.query.get_or_404(id_card)  # редактируем, удаляем и тд объекты
    try:  # для работ с бд эта функция больше всего подходит
        db.session.delete(cartridge)
        db.session.commit()
        return redirect('/claim')
    except:
        return "При удалении произошла ошибка :("


#___________________________________________Заявки_________________________________________________________________


@app.route('/create_application', methods=['POST', 'GET'])  # стр заявки создания и тд
def create_application():
    if request.method == "POST":
        unit = request.form['unit']
        model = request.form['model']
        who = request.form['who']

        article = Article(unit=unit, model=model, who=who)
        try:
            db.session.add(article)  #добавляем объект
            db.session.commit()  #  сохраняем объект
            return redirect('/application')
        finally:
            traceback.format_exc()
    else:
        return render_template("create_application.html")


@app.route('/application/<int:id>/update', methods=['POST', 'GET'])  # редактирование заявки
def application_update(id):
    article = Article.query.get(id)  # нашли нужный объект
    if request.method == "POST":
        article.unit = request.form['unit']  # для этого объекта меняем значение
        article.model = request.form['model']
        article.who = request.form['who']

        try:
            db.session.commit()  #  обновляем объекты бд
            return redirect('/application')
        except:
            return "При редактировании произошла ошибка :("
    else:
        return render_template("application_update.html", article=article)


@app.route('/application')
def application():
    articles = Article.query.order_by(Article.date.desc())
    """ .first() только первая запись отображается/
        метод order_by отображает все записи, внутри метода стоит сортировка по дате
    """
    return render_template("application.html", articles=articles)
    # про вывод: в первый шаблон articles передается список со второго =articles


@app.route('/application/<int:id>')  # Обработка адреса для кнопки "обзор"
def application_detail(id):
    article = Article.query.get(id)  # получаем объект по его айди
    return render_template("application_detail.html", article=article)


@app.route('/application/<int:id>/delete')  # редактировние заявок
def application_delete(id):
    article = Article.query.get_or_404(id)  # редактируем, удаляем и тд объекты
    try:  # для работ с бд эта функция больше всего подходит
        db.session.delete(article)
        db.session.commit()
        return redirect('/application')
    except:
        return "При удалении произошла ошибка :("


if __name__ == '__main__':
    app.run(debug=True)
    # from waitress import server на будущее испл настройки для сервера
    # serve(app, host="0.0.0.0", port=8080)
