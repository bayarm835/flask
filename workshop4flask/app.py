from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from datetime import date

app = Flask(__name__)
app.secret_key = 'e6Be3kK34473v2Q3pQUPQxjDvCyjs39X'

# Configuration de la connexion à MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="20030701Ae.moon",
    database="blog"
)

# Initialisation de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Définition du modèle utilisateur
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

# Chargement de l'utilisateur
@login_manager.user_loader
def load_user(user_id):
    # Implémentez la logique pour récupérer l'utilisateur à partir de la base de données MySQL
    cursor = db.cursor()
    cursor.execute("SELECT * FROM utilisateur WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data:
        return User(user_data[0], user_data[1], user_data[2])  
    else:
        return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    # Récupérer le message de la requête
    message = request.args.get('message')

    if request.method == 'POST':
        # Récupérer les données du formulaire
        username = request.form['username']
        password = request.form['password']

        # Rechercher l'utilisateur dans la base de données
        cursor = db.cursor()
        cursor.execute("SELECT * FROM utilisateur WHERE NomUtilisateur = %s", (username,))
        user_data = cursor.fetchone()
        cursor.close()

        # Vérifier si l'utilisateur existe et que le mot de passe est correct
        if user_data and check_password_hash(user_data[2], password):  
            # Connecter l'utilisateur
            user = User(user_data[0], user_data[1], user_data[2])
            login_user(user)

            # Rediriger vers la page d'accueil après la connexion réussie
            return render_template('page.html')


        else:
            # Si les informations d'identification sont incorrectes, afficher un message d'erreur
            error_message = "Nom d'utilisateur ou mot de passe incorrect."
            return render_template('login.html', error_message=error_message)
    else:
        # Si la méthode de requête est GET, afficher simplement le formulaire de connexion
        return render_template('login.html')

from flask import request

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        username = request.form['username']
        password = request.form['password']

        # Hasher le mot de passe
        hashed_password = generate_password_hash(password)
        
        # Insérer les données dans la base de données MySQL
        cursor = db.cursor()
        cursor.execute("INSERT INTO utilisateur (NomUtilisateur, MotDePasse) VALUES (%s, %s)", (username, hashed_password))
        db.commit()  # Valider les changements dans la base de données
        cursor.close()

        # Rediriger vers la page de connexion avec un message de réussite
        return redirect(url_for('login', message_reussie='Inscription réussie. Vous pouvez maintenant vous connecter.'))
    
    # Si la méthode de requête est GET, afficher simplement la page d'inscription
    return render_template('inscription.html')

@app.route('/create_post', methods=['POST'])
@login_required
def create_post():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        title = request.form['title']
        content = request.form['content']
        
        # Récupérer l'ID de l'utilisateur connecté
        user_id = current_user.id

        # Récupérer la date
        publish_date = date.today().strftime("%Y-%m-%d")  # Récupérer la date du jour
        
        # Insérer les données dans la base de données MySQL
        cursor = db.cursor()
        cursor.execute("INSERT INTO article (Titre, Contenu, DatePublication, IDUtilisateur) VALUES (%s, %s, %s, %s)", (title, content, publish_date, user_id))
        db.commit()  # Valider les changements dans la base de données
        cursor.close()

        # Message à afficher dans le modèle
        message = "Le post a été créé avec succès !"
        
        # Rediriger vers la page d'accueil après la création du post
        return render_template('page.html', message_post=message)

@app.route('/my_posts')
def my_posts():
    user_id = current_user.id
    cursor = db.cursor()
    cursor.execute("SELECT * FROM article WHERE IDUtilisateur = %s", (user_id,))
    posts = cursor.fetchall()
    cursor.close()  # Fermeture du curseur après avoir récupéré les données
    return render_template('my_posts.html', posts=posts)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
