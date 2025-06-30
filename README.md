Сервис управления продажами и аналитики

Django-приложение для управления клиентами, продуктами, заказами и генерации аналитических отчетов по продажам в формате PDF. Построено на Django REST Framework, PostgreSQL и WeasyPrint для надежной обработки заказов и создания отчетов.



Технологии

Python 3.10+
Django 4+
Django REST Framework
PostgreSQL
Jinja2 + WeasyPrint
Docker
uv



Чтобы установить и запустить приложение, пожалуйста, следуйте инструкциям ниже:

1. Установите Python 3.10+
2. Нужно установить UV пакетный менеджер pip install uv
3. Установите PostgreSQL
4. Установите зависимости WeasyPrint в зависимости от ОС (Например MAC ==> brew install pango cairo libffi gdk-pixbuf или brew install weasyprint)
для Windows нужно посмотреть в документации https://doc.courtbouillon.org/weasyprint/stable/first_steps.html
5. Установите Docker
6. Клонируйте проект git clone https://github.com/Nooruzbai/test_shop.git
7. До запуска проекта создайте .env в директории проекта выше source и заполните эти ключи

    SECRET_KEY=
    DEBUG=True
    POSTGRES_DB=shop
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=
    POSTGRES_PORT=5432
    POSTGRES_HOST=localhost или db через докер

8. Зайдите в папку проекта и введите команду uv sync
9. Перейдите в директорию source
10. Мигрируйте модели python3 manage.py migrate
11. В этой же директории введите python3 manage.py loaddata fixtures.json
12. Запустите проект python3 manage.py runserver



Перейдите http://localhost:8000/swagger/

Примечание:
Если нужно чтобы открывался дополнительный endpoint где отчет генерируется через TailwindCSS, то установите Node.js и в папке проекта введите npm install и в директории source введите npx @tailwindcss/cli -i static/src/input.css -o static/css/output.css --watch
http://localhost:8000/api/report/sales-html/


DJANGO_SUPERUSER_EMAIL=admin@gmail.com
DJANGO_SUPERUSER_PASSWORD=admin

(Внимание: если вы запускаете приложение в Docker, укажите "db" в настройках базы данных POSTGRES_HOST; для локального запуска укажите "localhost")

Если вы хотите запустить приложение в Docker, выполните следующую команду:

docker compose up --build
Для доступа к панели администратора перейдите по следующему URL: http://localhost:8000/admin
Примечание: Если применили фикстуры то email:admin@gmail.com и пароль: admin

Если у вас возникли проблемы при установке приложения, пожалуйста, свяжитесь со мной по адресу: nooruzbay@gmail.com

