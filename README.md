# Сайт доставки еды Star Burger

Это сайт сети ресторанов Star Burger. Здесь можно заказать превосходные бургеры с доставкой на дом.

Ознакомиться с работой сайта можно [здесь](https://starburger.jmuriki.ru) и [здесь](https://starburger.docker.jmuriki.ru).

![скриншот сайта](https://dvmn.org/filer/canonical/1594651635/686/)


Сеть Star Burger объединяет несколько ресторанов, действующих под единой франшизой. У всех ресторанов одинаковое меню и одинаковые цены. Просто выберите блюдо из меню на сайте и укажите место доставки. Мы сами найдём ближайший к вам ресторан, всё приготовим и привезём.

На сайте есть три независимых интерфейса. Первый — это публичная часть, где можно выбрать блюда из меню, и быстро оформить заказ без регистрации и SMS.

Второй интерфейс предназначен для менеджера. Здесь происходит обработка заказов. Менеджер видит поступившие новые заказы и первым делом созванивается с клиентом, чтобы подтвердить заказ. После оператор выбирает ближайший ресторан и передаёт туда заказ на исполнение. Там всё приготовят и сами доставят еду клиенту.

Третий интерфейс — это админка. Преимущественно им пользуются программисты при разработке сайта. Также сюда заходит менеджер, чтобы обновить меню ресторанов Star Burger.


Далее будет описано, как настроить и запустить сайт тремя способами:

- без использования `Docker`
- с помощью `Docker` и/или `Docker-compose`
- с помощью деплойного скрипта `Docker-compose`

Некоторые инструкции из первой части пригодятся при выборе любого из вариантов деплоя. В конце файла есть разделы, посвящённые настройке `systemd`, `nginx` и `PostgreSQL`.


## Как запустить dev-версию сайта

Для запуска сайта нужно запустить **одновременно** бэкенд и фронтенд, в двух терминалах.

### Собрать бэкенд

Скачайте код:
```sh
git clone https://github.com/jmuriki/star-burger.git star-burger_docker
```

Перейдите в каталог проекта и переключитесь на ветку `Docker_lesson2`:
```sh
cd star-burger_docker
git checkout Docker_lesson2
```

[Установите Python](https://www.python.org/), если этого ещё не сделали.

Проверьте, что `python` установлен и корректно настроен. Запустите его в командной строке:
```sh
python --version
```
**Важно!** Версия Python должна быть не ниже 3.6. Рекомендуется остановиться на версии 3.8.

Возможно, вместо команды `python` здесь и в остальных инструкциях этого README придётся использовать `python3`. Зависит это от операционной системы и от того, установлен ли у вас Python старой (второй) версии. 

В каталоге проекта создайте виртуальное окружение:
```sh
python -m venv venv
```
Активируйте его. На разных операционных системах это делается разными командами:

- Windows: `.\venv\Scripts\activate`
- MacOS/Linux: `source venv/bin/activate`


Установите зависимости в виртуальное окружение:
```sh
pip install -r requirements.txt
```
Установите PostgreSQL (по необходимости) и создайте новую БД. Используйте переменную окружения `DB_URL` для передачи параметров БД. Формат переменной: `postgres://USER:PASSWORD@HOST:PORT/NAME`. Заменять следует только uppercase параметры. Разделители `:` и `@` указывать не нужно в том случае, если предшествующие параметры пусты, но следует всегда указывать все `/`.

Определите переменные окружения `SECRET_KEY`, `YANDEX_API_KEY`.
`ROLLBAR_ACCESS_TOKEN` и `ENVIRONMENT` - опционально.
Создайте файл `.env` в корневом каталоге и положите туда такой код:
```sh
SECRET_KEY=django-insecure-0if40nf4nf93n4
YANDEX_API_KEY=API_ключ_разработчика_Yandex

DB_URL=URL_c_параметрами_настройки_БД_PostgreSQL
ROLLBAR_ACCESS_TOKEN=access_token_Rollbar_для_мониторинга_исключений
ENVIRONMENT=если_используете_Rollbar,_укажите_"development"_для_dev-версии
```
Получить API ключ YANDEX можно в [кабинете разработчика](https://developer.tech.yandex.ru/):
Самые важные ответы на вопросы при регистрации:
- В открытом. Ваш код будет публично опубликован, это открытая система.
- В бесплатном. Вы пишете код в образовательных целях.
- Буду отображать данные на карте.

Для получения access token Rollbar достаточно [зарегистрироваться](https://rollbar.com), создать новый проект и в SDK выбрать Django.

Отмигрируйте файл базы данных следующей командой (если вы решили не использовать PostgreSQL, или не прописали `DB_URL` в переменных окружения, данная команда автоматически cоздаст и отмигрирует файл базы данных SQLite):

```sh
python manage.py migrate
```

Запустите сервер Django:

```sh
python manage.py runserver
```

Откройте сайт в браузере по адресу [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Если вы увидели пустую белую страницу, то не пугайтесь, выдохните. Просто фронтенд пока ещё не собран. Переходите к следующему разделу README.

### Собрать фронтенд

**Откройте новый терминал**. Для работы сайта в dev-режиме необходима одновременная работа сразу двух программ `runserver` и `parcel`. Каждая требует себе отдельного терминала. Чтобы не выключать `runserver` откройте для фронтенда новый терминал и все нижеследующие инструкции выполняйте там.

[Установите Node.js](https://nodejs.org/en/), если у вас его ещё нет.

Проверьте, что Node.js и его пакетный менеджер корректно установлены. Если всё исправно, то терминал выведет их версии:

```sh
nodejs --version
# v16.16.0
# Если ошибка, попробуйте node:
node --version
# v16.16.0

npm --version
# 8.11.0
```

Версия `nodejs` должна быть не младше `10.0` и не старше `16.16`. Лучше ставьте `14.21.3` или `16.16.0`, их тестировали. Версия `npm` не важна. Как обновить Node.js читайте в статье: [How to Update Node.js](https://phoenixnap.com/kb/update-node-js-version).

Перейдите в каталог проекта и установите пакеты Node.js:

```sh
cd star-burger_docker
npm ci --dev
```

Команда `npm ci` создаст каталог `node_modules` и установит туда пакеты Node.js. Получится аналог виртуального окружения как для Python, но для Node.js.

Помимо прочего будет установлен [Parcel](https://parceljs.org/) — это упаковщик веб-приложений, похожий на [Webpack](https://webpack.js.org/). В отличии от Webpack он прост в использовании и совсем не требует настроек.

Теперь запустите сборку фронтенда и не выключайте. Parcel будет работать в фоне и следить за изменениями в JS-коде:

```sh
./node_modules/.bin/parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
```

Если вы на Windows, то вам нужна та же команда, только с другими слешами в путях:

```sh
.\node_modules\.bin\parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
```

Дождитесь завершения первичной сборки. Это вполне может занять 10 и более секунд. О готовности вы узнаете по сообщению в консоли:

```
✨  Built in 10.89s
```

Parcel будет следить за файлами в каталоге `bundles-src`. Сначала он прочитает содержимое `index.js` и узнает какие другие файлы он импортирует. Затем Parcel перейдёт в каждый из этих подключенных файлов и узнает что импортируют они. И так далее, пока не закончатся файлы. В итоге Parcel получит полный список зависимостей. Дальше он соберёт все эти сотни мелких файлов в большие бандлы `bundles/index.js` и `bundles/index.css`. Они полностью самодостаточно и потому пригодны для запуска в браузере. Именно эти бандлы сервер отправит клиенту.

Теперь если зайти на страницу  [http://127.0.0.1:8000/](http://127.0.0.1:8000/), то вместо пустой страницы вы увидите:

![](https://dvmn.org/filer/canonical/1594651900/687/)

Каталог `bundles` в репозитории особенный — туда Parcel складывает результаты своей работы. Эта директория предназначена исключительно для результатов сборки фронтенда и потому исключёна из репозитория с помощью `.gitignore`.

**Сбросьте кэш браузера <kbd>Ctrl-F5</kbd>.** Браузер при любой возможности старается кэшировать файлы статики: CSS, картинки и js-код. Порой это приводит к странному поведению сайта, когда код уже давно изменился, но браузер этого не замечает и продолжает использовать старую закэшированную версию. В норме Parcel решает эту проблему самостоятельно. Он следит за пересборкой фронтенда и предупреждает JS-код в браузере о необходимости подтянуть свежий код. Но если вдруг что-то у вас идёт не так, то начните ремонт со сброса браузерного кэша, жмите <kbd>Ctrl-F5</kbd>.

## Как запустить prod-версию сайта

Потребуется настройка сервисов `systemd` для `gunicorn` и `node`.
Потребуется настройка конфигурации `nginx`.
Ближе к концу `README.md` будет раздел с инструкциями по настройке `systemd` и `gunicorn` на Ubuntu.

### Настроить бэкенд

Cоздать в корневом каталоге проекта файл `.env` со следующими настройками:

- `DB_URL` - подставьте значения параметров по форме: `postgres://USER:PASSWORD@HOST:PORT/NAME`.
- `DEBUG` — поставьте `False` или закомментируйте/удалите переменную.
- `SECRET_KEY` — секретный ключ проекта. Он отвечает за шифрование на сайте. Например, им зашифрованы все пароли на вашем сайте.
- `ALLOWED_HOSTS` — [см. документацию Django](https://docs.djangoproject.com/en/3.1/ref/settings/#allowed-hosts).
- `ROLLBAR_ACCESS_TOKEN` - укажите access token Rollbar, если захотите подключить мониторинг исключений.

### Cобрать фронтенд

Используйте bash-скрипт `deploy_star-burger.sh`, который можно найти в папке `scripts` в корне проекта:

```sh
./scripts/deploy_star-burger.sh
```

## Как быстро обновить код на сервере

Вам потребуется всё тот же bash-скрипт `deploy_star-burger.sh`:

```sh
./deploy_star-burger.sh
```

Bash-скрипт на сервере сделает следующее:

- Обновит код репозитория
- Выберет нужную ветку
- Установит библиотеки для Python и Node.js
- Пересоберёт фронтенд
- Пересоберёт статику Django
- Накатит миграции
- Перезапустит сервисы systemd
- Сообщит об успешном завершении деплоя
- Упадёт в случае ошибки и дальше не пойдёт


## Как запустить сайт с помощью Docker

Должен быть установлен [Docker](https://docs.docker.com).
Далее будут описаны этапы создания образов и запуска контейнеров, но для быстрого запуска можно сразу перейти к разделу Docker-compose.
Все команды следует вводить, находясь в основной директории проекта.


### Docker-image

```sh
docker build -f Dockerfile_frontend -t star-burger_frontend .
```
Будет произведена сборка образа фронтенда, в котором останутся только файлы статики.


```sh
export COMMIT_HASH=$(git rev-parse Docker_lesson2)
docker build --build-arg COMMIT_HASH=$COMMIT_HASH -f Dockerfile_backend -t star-burger_backend .
```
Будет произведён сбор файлов статики Django и создание образа бэкенда, который сможет запускаться в 2х различных режимах - `runserver` и `gunicorn`. Образ получит метку LABEL "last_commit_hash" со значением хэша последнего коммита в `git` ветке, чтобы затем передать этот хэш в `Rollbar` при запуске деплойного скрипта.


### Docker-container

```sh
docker run -v ./staticfiles:/var/www/frontend --rm jmuriki/star-burger_frontend
```
Будет произведено копирование собранных в образе файлов статики в предварительно созданную в контейнере директорию `frontend`, в которую будет вмонтирована локальная папка `staticfiles`, а в конце - удаление отработавшего контейнера.

Далее, убедившись в том, что в основной директории содержится наполненный файл `.env` (инструкции по `.env` смотрите выше), введите команду, подставив вместо `10101:` желаемый номер порта.

Для запуска dev-версии на локальной машине:
```sh
docker run -d --env-file .env -v ./staticfiles:/star-burger/bundles -v ./media:/var/www/media/ -p 10101:8000 -e COMMAND=runserver jmuriki/star-burger_backend
```
В предварительно созданную в контейнере директорию `bundles` будет вмонтирована локальная папка `staticfiles`, а затем запущен сервер Django.

Для запуска prod-версии на сервере с `nginx`:
```sh
docker run --restart always -d --env-file .env -v ./staticfiles:/var/www/static -v ./media:/var/www/media/ -p 10101:8080 -e COMMAND=gunicorn jmuriki/star-burger_backend
```
Будет произведено копирование собранных в образе файлов статики в предварительно созданную в контейнере директорию `static`, в которую будет вмонтирована локальная папка `staticfiles` вместе со всеми содержащимися в ней файлами статики фронтенда.

Если захотите использовать определённый порт внутри контейнера, то его нужно будет поменять не только в команде, но и в скрипте `runserver.sh` / `gunicorn.sh`, а затем пересобрать образ.


### Docker-compose

По умолчанию в `.yaml` файлах прописано использование образов из DockerHub `jmuriki`. В обоих `.yaml` файлах есть закомментированные варианты, позволяющие собрать образы на месте или использовать уже имеющиеся локальные образы.

Скачайте свежие образы, если выберете вариант по умочанию.
При первом использовании можете пропустить этот шаг и сразу перейти к команде `docker compose up` - она автоматически скачает свежие образы.
```sh
docker compose -f docker-compose_runserver.yaml pull
docker compose -f docker-compose_gunicorn.yaml pull
```

dev-версия:
```sh
docker compose -f docker-compose_runserver.yaml up -d
```

prod-версия:
```sh
docker compose -f docker-compose_gunicorn.yaml up -d
```

При выборе варината `gunicorn` потребуется настройка конфигурации `nginx` (далее будет раздел с инструкцией для Ubuntu).


## Деплойный скрипт Docker-compose

Должен быть установлен [Docker](https://docs.docker.com).
Находясь в корневой директории проекта и убедившись, что в ней содержится наполненный файл `.env` (инструкции по заполнению находятся выше), введите команду:
```sh
./scripts/deploy_star-burger_docker-compose.sh
```
Данный скрипт скачает необходимые образы и запустит контейнеры. Для полноценной работы в prod-режиме останется настроить и запустить/перезапустить `nginx` и `systemd`.

Bash-скрипт на сервере сделает следующее:

- Остановит работающий стэк (если он есть)
- Обновит образы
- Запустит стэк с обновлёнными образами
- Перезапустит nginx
- Сообщит об успешном завершении деплоя
- Удалит отработавший контейнер
- Упадёт в случае ошибки и дальше не пойдёт


## systemd

Создайте демона, если хотите, чтобы сервис автоматически поднимался в случае перезагрузки сервера (далее инструкция для Ubuntu):

```sh
cd /etc/systemd/system/
```

```sh
vim star-burger_gunicorn.service
```

```
[Unit]
Description=gunicorn server for star-burger
After=network.target
Requires=postgresql.service

[Service]
WorkingDirectory=/opt/star-burger_docker/
ExecStart=/opt/star-burger_docker/venv/bin/gunicorn -w 3 -b 127.0.0.1:8080 star_burger.wsgi:application
Restart=always
[Install]
WantedBy=multi-user.target
```

```sh
vim star-burger_node.service
```

```
[Service]
WorkingDirectory=/opt/star-burger_docker/
ExecStart=/opt/star-burger_docker/node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
Restart=always
[Install]
WantedBy=multi-user.target
```

```sh
vim star-burger_docker-compose.service
```

```
[Unit]
Description=Docker Compose Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/star-burger_docker/
ExecStart=/usr/libexec/docker/cli-plugins/docker-compose -f docker-compose_gunicorn.yaml up -d
ExecStop=/usr/libexec/docker/cli-plugins/docker-compose -f docker-compose_gunicorn.yaml down

[Install]
WantedBy=multi-user.target
```

Настройте запуск демонов при перезагрузке системы и активируйте их:

```sh
systemctl enable star-burger_gunicorn.service
systemctl start star-burger_gunicorn.service
systemctl enable star-burger_node.service
systemctl start star-burger_node.service
```

```sh
systemctl enable star-burger_docker-compose.service
systemctl start star-burger_docker-compose.service
```


## nginx

Должен быть установлен `nginx`.

```sh
cd /etc/nginx/sites-available/
```

Создать файл конфигурации:
```sh
vim starburger.***.ru
```

```
server {
    server_name starburger.jmuriki.ru;
    location /media/ {
        alias /opt/star-burger_docker/media/;
    }
    location /static/ {
        alias  /opt/star-burger_docker/staticfiles/;
    }
    location / {
      include '/etc/nginx/proxy_params';
      proxy_pass http://127.0.0.1:8080/;
    }
}
```

Активировать конфигурацию:
```
ln -s /etc/nginx/sites-available/starburger.***.ru /etc/nginx/sites-enabled/
```


Создать файл конфигурации для docker версии:
```sh
vim starburger.docker.***.ru
```

```
server {
    server_name starburger.docker.***.ru;
    location /media/ {
        alias /opt/star-burger_docker/media/;
    }
    location /static/ {
        alias  /opt/star-burger_docker/staticfiles/;
    }
    location / {
      include '/etc/nginx/proxy_params';
      proxy_pass http://127.0.0.1:10101/;
    }
}
```

Активировать конфигурацию:
```
ln -s /etc/nginx/sites-available/starburger.docker.***.ru /etc/nginx/sites-enabled/
```


## PostgreSQL и Docker на Ubuntu и macOS

Для того, чтобы подключить к Docker установленную на хосте БД PostgreSQL, необходимо пройти несколько шагов.

### Доступ к порту PostgreSQL

Если у вас на хосте установлен `ufw`, выполните следующие команды, чтобы разрешить подключение к БД по стандартному порту PostgreSQL:
```sh
sudo ufw allow 5432
sudo ufw allow 5432/tcp
sudo ufw disable && sudo ufw enable
```

Перезагрузите сервер PostgreSQL:
```sh
sudo service postgresql restart
```

### Настройки доступа к PostgreSQL

Укажите адреса, которые PostgreSQL будет слушать (дополните команду в зависимости от установленной версии PostgreSQL):

Linux:
```sh
vim /etc/postgresql/***/main/postgresql.conf
```

macOS:
```sh
vim /usr/local/var/postgresql***/postgresql.conf
```

```
listen_addresses = '*'
```

Пропишите параметры подключения к БД PostgreSQL в поле `IPv4 local connections` файла `pg_hba.conf` (дополните команду в зависимости от установленной версии PostgreSQL):

Linux:
```sh
vim /etc/postgresql/***/main/pg_hba.conf
```

macOS:
```sh
vim /usr/local/var/postgresql***/pg_hba.conf
```

Если хотите разрешить подключение к БД с любого IP c паролем:
```
host    <db_name>   <login>     0.0.0.0/0   md5
```
Если хотите разрешить подключение к БД с любого IP без пароля:
```
host    <db_name>   <login>     0.0.0.0/0   trust
```
Если хотите разрешить подключение к БД с определённого IP c паролем:
```
host	<db_name>	<login>		<IPAddress>/0	md5
```
Если хотите разрешить подключение к БД с определённого IP без пароля:
```
host	<db_name>	<login>		<IPAddress>/0	trust
```

Узнать IPAddress вашего контейнера можно с помощью следующих команд:
```
docker ps -a
docker inspect <container-id>
```

Перезагрузите сервер PostgreSQL, чтобы изменения наверняка вступили в силу.

### Передача параметров БД в docker-контейнер

Узнать локальный IP-адрес - HOST, можно следующей командой:
```
ifconfig | grep "inet " | grep -Fv 127.0.0.1 | awk '{print $2}'
````

PORT - порт PostgreSQL.

Составьте переменную окружения с параметрами БД и добавьте её в `.env`:

```
DB_URL=postgres://USER:PASSWORD@HOST:PORT/NAME
```


## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org). За основу был взят код проекта [FoodCart](https://github.com/Saibharath79/FoodCart).

Где используется репозиторий:

- Второй и третий урок [учебного курса Django](https://dvmn.org/modules/django/)
- Второй урок [учебного курса Docker](https://dvmn.org/modules/docker-v2/)
