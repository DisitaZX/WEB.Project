from wtforms.fields.html5 import EmailField
from wtforms.fields import PasswordField, SubmitField, BooleanField, StringField, IntegerField
from wtforms.validators import DataRequired
from data.users import User
from data.books import Book
from flask import Flask, render_template, redirect
from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_wtf import FlaskForm
import requests
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)
class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    age = StringField('Возраст', validators=[DataRequired()])
    position = StringField('Должность', validators=[DataRequired()])
    speciality = StringField('Специальность', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    submit = SubmitField('Отправить')
class BookForm(FlaskForm):
    name = StringField('Название книги', validators=[DataRequired()])
    author = StringField('Имя Автора', validators=[DataRequired()])
    language = StringField('Язык', validators=[DataRequired()])
    pages = IntegerField('Количество страниц', validators=[DataRequired()])
    submit = SubmitField('Отправить')
class Search(FlaskForm):
    text = StringField("Текст", validators=[DataRequired()])
    submit = SubmitField('Найти')
@app.route('/')
def index():
    session = db_session.create_session()
    books = [i.name for i in session.query(Book)]
    return render_template('base.html', title="Библиотека", books=books)
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            email=form.email.data,
            hashed_password=form.password.data,
            surname=form.surname.data,
            name=form.name.data,
            age=form.name.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")
@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        if session.query(Book).filter(Book.name == form.name.data).first():
            return render_template('book.html', title='Добавление книги',
                                   form=form,
                                   message="Такая книга уже есть")
        book = Book(
            name=form.name.data,
            author=form.author.data,
            language=form.language.data,
            pages=form.pages.data
        )
        session.add(book)
        session.commit()
        return redirect('/')
    return render_template('book.html', title='Добавление книги', form=form)
@app.route('/search', methods=["POST", "GET"])
@login_required
def search():
    names = []
    form = Search()
    if form.validate_on_submit():
        value = form.text.data
        apikey = "AIzaSyCDl8mvUuZt74ht0gc_ul00ChzarQqSg5M"
        parms = {"q": value, 'key': apikey}
        r = requests.get(url="https://www.googleapis.com/books/v1/volumes", params=parms).json()
        for i in r["items"]:
            title = i["volumeInfo"]["title"]
            names.append(title)
    return render_template('search.html', names=names, form=form)
@app.route('/book/<book>')
@login_required
def bookname(book):
    apikey = "AIzaSyCDl8mvUuZt74ht0gc_ul00ChzarQqSg5M"
    href = f"https://www.googleapis.com/books/v1/volumes?q={book}&download=epub&key={apikey}"
    r = requests.get(url=href).json()
    try:
        download = r["items"][0]["accessInfo"]["epub"]["downloadLink"]
    except KeyError as e:
        try:
            download = r["items"][0]["saleInfo"]["buyLink"]
        except KeyError:
            download = '/'
    return redirect(download)
if __name__ == '__main__':
    db_session.global_init('db/blogs.db')
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
