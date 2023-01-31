# Project_10_REST_API
Conception à l'aide de Django d'une API REST de gestion pour la société SoftDesk. Elle permet de gérer une liste de projets, de leur associer des problèmes et de poster des commentaires dans ces derniers. Les utilisateurs sont vus comme des contributeurs ajoutés à certains projets, et un système de droit permet de s'assurer que l'accès en lecture et/ou en écriture est réservée aux contributeurs. De même, l'édition ou la suppression d'éléments est réservée à leurs auteurs.

***

### Installation et lancement
Se placer dans un dossier de travail vide et récupérer le code:
```
$ git clone https://github.com/martinschongauer/Project_10_REST_API
```

Créer et activer un environnement Python pour ce projet (testé sous Linux - Ubuntu):
```
$ python3 -m venv env
$ source env/bin/activate
```

Parfois les commandes varient légèrement. Sous Windows 10 nous avons exécuté les commandes suivantes:
```
$ python -m venv env
$ env\Scripts\activate
```

Installer ensuite les dépendances listées dans le fichier requirements.txt:
```
$ pip install -r requirements.txt
```

Lancer le programme:
```
$ python3 manage.py runserver
```

(ou "python" selon la configuration de la machine)

### Création d'une nouvelle base de données
Il est possible de supprimer la base de données et d'en recréer une à l'aide des commandes suivantes:

```
$ rm -f db.sqlite3
$ python manage.py makemigrations
$ python manage.py migrate
$ python3 manage.py init_api
```

Le script d'initialisation init_api se situe dans api/managment/commands et il permet de créer des données par défaut (quatre utilisateurs et deux projets).

### Usage général
Le site internet est ensuite accessible en local à l'adresse (pour inscrire un nouvel utilisateur):

http://127.0.0.1:8000/signup

Ainsi que sa zone d'administration:

http://127.0.0.1:8000/admin

Une base de données minimale est livrée avec l'application. Elle comprend quatre utilisateurs:

admin@oc.com - chucknorris@oc.com - paveldurov@oc.com - anonymous@oc.com

admin est le "superuser", et tous partagent le mot de passe : password

Une fois l'API lancée, ses endpoints peuvent être utilisés à l'aide de Postman. Leur documentation est accessible via les liens fournis dans le second livrable.
