# Сайт доставки еды Star Burger

Это сайт сети ресторанов Star Burger. Здесь можно заказать превосходные бургеры с доставкой на дом.

Ознакомиться с работой сайта можно [здесь](https://starburger.jmuriki.ru).

![скриншот сайта](https://dvmn.org/filer/canonical/1594651635/686/)


Сеть Star Burger объединяет несколько ресторанов, действующих под единой франшизой. У всех ресторанов одинаковое меню и одинаковые цены. Просто выберите блюдо из меню на сайте и укажите место доставки. Мы сами найдём ближайший к вам ресторан, всё приготовим и привезём.

На сайте есть три независимых интерфейса. Первый — это публичная часть, где можно выбрать блюда из меню, и быстро оформить заказ без регистрации и SMS.

Второй интерфейс предназначен для менеджера. Здесь происходит обработка заказов. Менеджер видит поступившие новые заказы и первым делом созванивается с клиентом, чтобы подтвердить заказ. После оператор выбирает ближайший ресторан и передаёт туда заказ на исполнение. Там всё приготовят и сами доставят еду клиенту.

Третий интерфейс — это админка. Преимущественно им пользуются программисты при разработке сайта. Также сюда заходит менеджер, чтобы обновить меню ресторанов Star Burger.

## Как запустить dev-версию сайта

Для запуска сайта нужно запустить **одновременно** бэкенд и фронтенд, в двух терминалах.

### Как собрать бэкенд

Скачайте код:
```sh
git clone https://github.com/jmuriki/star-burger.git
```

Перейдите в каталог проекта:
```sh
cd star-burger
```

[Установите Python](https://www.python.org/), если этого ещё не сделали.

Проверьте, что `python` установлен и корректно настроен. Запустите его в командной строке:
```sh
python --version
```
**Важно!** Версия Python должна быть не ниже 3.6. Рекомендуется остановиться на версии 3.8.

Возможно, вместо команды `python` здесь и в остальных инструкциях этого README придётся использовать `python3`. Зависит это от операционной системы и от того, установлен ли у вас Python старой второй версии. 

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

Определите переменные окружения `SECRET_KEY`, `YANDEX_API_KEY`. `ROLLBAR_ACCESS_TOKEN` и `ENVIRONMENT` - опционально. Создайте файл `.env` в каталоге `star_burger/` и положите туда такой код:
```sh
SECRET_KEY=django-insecure-0if40nf4nf93n4
YANDEX_API_KEY=поместите_API_ключ_разработчика_Yandex

DB_URL=поместите_URL_c_параметрами_настройки_базы_данных_если_используете_PostgreSQL
ROLLBAR_ACCESS_TOKEN=поместите_access_token_Rollbar,_если_захотите_подключить_мониторинг_исключений
ENVIRONMENT=если_используете_Rollbar,_укажите_"development"_для_dev-версии,_"production"_прописан_по-умолчанию
```
Получить API ключ YANDEX можно в [кабинете разработчика](https://developer.tech.yandex.ru/):

Самые важные ответы на вопросы:

- В открытом. Ваш код будет публично опубликован, это открытая система
- В бесплатном. Вы пишете код в образовательных целях
- Буду отображать данные на карте. По шагам урока вам предстоит это сделать

Для получения access token Rollbar достаточно [зарегистрироваться](https://rollbar.com), создать новый проект и в SDK выбрать Django.

Отмигрируйте файл базы данных следующей командой (если вы решили не использовать PostgreSQL, или не прописали `DB_URL` в переменных окружения, данная команда автоматически cоздаст и отмигрирует файл базы данных SQLite):

```sh
python manage.py migrate
```

Запустите сервер:

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
cd star-burger
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

Настроить бэкенд: создать файл `.env` в каталоге `star_burger/` со следующими настройками:

- `DB_URL` - подставьте значения параметров по форме: `postgres://USER:PASSWORD@HOST:PORT/NAME`.
- `DEBUG` — поставьте `False` или удалите переменную.
- `SECRET_KEY` — секретный ключ проекта. Он отвечает за шифрование на сайте. Например, им зашифрованы все пароли на вашем сайте.
- `ALLOWED_HOSTS` — [см. документацию Django](https://docs.djangoproject.com/en/3.1/ref/settings/#allowed-hosts).
- `ROLLBAR_ACCESS_TOKEN` - укажите access token Rollbar, если захотите подключить мониторинг исключений.

Чтобы собрать фронтенд, используйте bash-скрипт `deploy_star-burger.sh`, который можно найти в корне проекта:

```sh
./deploy_star-burger.sh
```

## Как быстро обновить код на сервере

Вам потребуется всё тот же bash-скрипт `deploy_star-burger.sh`:

```sh
./deploy_star-burger.sh
```

Bash-скрипт на сервере сделает следующее:

- Обновит код репозитория
- Установит библиотеки для Python и Node.js
- Пересоберёт фронтенд
- Пересоберёт статику Django
- Накатит миграции
- Перезапустит сервисы Systemd
- Сообщит об успешном завершении деплоя
- Упадёт в случае ошибки и дальше не пойдёт

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org). За основу был взят код проекта [FoodCart](https://github.com/Saibharath79/FoodCart).

Где используется репозиторий:

- Второй и третий урок [учебного курса Django](https://dvmn.org/modules/django/)
