<!-- header -->
![Header](https://github.com/RomCodeman/news_parser_application/blob/master/static/programmer_image.png?raw=true)

# News parser application (Pet Project 1)
![GitHub release (python version)](https://img.shields.io/badge/python-3.8-informational)
![GitHub release (app version)](https://img.shields.io/badge/release-v0.5-blue)
![GitHub release (app size)](https://img.shields.io/github/repo-size/RomCodeman/news_parser_application)
![GitHub release (license)](https://img.shields.io/badge/license-GPL--3.0--only-green)

This application is my first Pet Project. The main goal of its writing was to obtain new knowledge in applied 
programming. This application was written for a self-educational purpose and as a project for a professional portfolio.

> Automated information collection is a complex process, that can be implemented by many tools and in different ways,
> that have their own advantages and disadvantages according to the specific situation.
> My choice of tools is based on my wish to try specific library/way, general recommendations from the Internet and my
> current programming skills. Sometimes I used not the most optimal solutions. So, I will bring this application in accordance with some software design patterns, the principles of the OOP and Zen of Python, as far as I improve my programming skills.
---
## Table of contents
* [Table of contents](#table-of-contents)
* [Why news parser application?](#why-news-parser-application)
* [Key features](#key-features)
* [Usage](#usage)
  * [Expected result](#expected-result)
* [Potential features](#potential-features)
* [Requirements](#requirements)
* [Was learned during work on the project?](#was-learned-during-work-on-the-project)
* [Contributing](#contributing)
* [License](#license)
* [Contact info](#contact-info)

---
## Why news parser application?
[(Back to top)](#table-of-contents)

I decided to make first steps towards an automated collection of information from Internet resources (Scraping /
Crawling / Parsing). As a source of information, I chose the online news portal [ukr.net](https://www.ukr.net/), which aggregates news from
different sources on different topics.

It is an interesting challenge for me, because it is necessary to understand the logic of a successful working project.
There is a high flow of data with several nesting levels that need to operate with the DB. The optimization process can
be almost endless. It contains many different technologies and requires various skills.

---
## Key features
[(Back to top)](#table-of-contents)

* to receive data from an open source by processing the web content (Selenium, Requests)
* operation with DB (Django, sqlite3)
    * "many to many" table relationship was used to attach several categories to the same news item
    * writing the received information to the DB
* application setting by editing values in the '.ini' file
    * number of news of the first level that need to be processed
    * categories of news for processing
    * visible or background launch of Internet browser driver option
* logging 
    * created catalogs and files inside the project, that are required for the application operation (start of application provides displaying of the names of created files and directories in the terminal window)
    * processed and written news
    * error massages of a specific level to a file, with auto-backup when specified file size is reached (works, but not configured)
    * displays the processed/written objects (the decorator that counts the message ID from the last parsing session, in a temporary .csv file)

The practical purpose of this program is the collection of news and related information (the date of publication,
category, news partner name, url to the original source, etc.). With this application the information is being
structured in the database and displayed in accordance to the user's settings for subsequent analytical processing.

---
## Installation & Usage
[(Back to top)](#table-of-contents)

> The application must be run in OS GNU/Linux (OS Windows temporary is not supported) in the terminal in the root folder
> of the project with activated virtual environment.

1. Download the project archive to the target folder.

2. Set the basic parsing settings in the 'PARSER_CONFIG_FILE.ini' file
   >**WARNING!** The first parsing operation time with settings CLUSTERS_QTY_LIMITER = 0 and CATEGORIES_FOR_PARSING = 0,
   > can take **more than 25 minutes** (2-7 minutes per category), as all news, published during last 7 days will be
   > processed.
   > 
   > *On average, during 7 days, more than 1000 news agencies publish more than 55000 articles (that have very different
   > level of importance). Only 7000 of them can be attributed to "more significant", as they were published by more
   > than one news agency.* 

3. Start of the parsing process of news categories and news:
    ```
    $ (venv) ./manage.py ukrnet
   ```
    
    3.1. *Not necessary.* It is possible to run the news categories parsing only, through an additional argument
   '--categories_only' or '--cats'. It may be convenient to save time, if new category of news was added on ukr.net
   news portal:
    ```
    $ (venv) ./manage.py ukrnet --categories_only
   ```

4. Review of collected news:
    > For news review, you can open a 'db_parsed_news.sqlite3' database file using any program that allows you to read
   > the '.sqlite3' format or use the Django admin panel, as in the example below.
    ```
    # create superuser
    $ (venv) ./manage.py createsuperuser
   
    # enter the data of the administrator account
   
    # run local server
    $ (venv) ./manage.py runserver
   ```
    The next step is follow the link http://127.0.0.1:8000 in the Internet browser window, enter the administrator name
   and password to enter the account (you can use the data from the example file named 'personal_data_settings.py' file).

---
### Expected result
[(Back to top)](#table-of-contents)

##### An example of displaying the main page of the admin panel
   <p align="center">
  <img  src="https://github.com/RomCodeman/news_parser_application/blob/master/static/django_admin_tables.png?raw=true">
</p>

---
##### An example of displaying the table with the collected news
   <p align="center">
  <img src="https://github.com/RomCodeman/news_parser_application/blob/master/static/django_admin_news_table.png?raw=true">
</p>

---

##### An example of displaying the page with a separate news.
   <p align="center">
  <img height="250" src="https://github.com/RomCodeman/news_parser_application/blob/master/static/django_admin_news_item.png?raw=true">
</p>

---
## Potential features
[(Back to top)](#table-of-contents)

Huge potential of this application consists in analytical processing of the collected data. Different operations with DB
and changes in data displaying allow to do the following: group news by different custom filters; mark news agencies
with the same topics or content and count these cases; process a metrics of the news agencies activities, etc. Also,
it is possible to implement simple analytical approaches to draw some conclusions about bias of news agencies and
published content.

You can automate parser start by using CRON daemon or more complex methods, if it is necessary.

Usage of the thematic modeling algorithms (Topic modeling) and the NLP libraries (NLTK, TextBlob, Gensim, spaCy etc.),
allows to specify "emotional context" of content and carry out its semantic analysis. That will significantly expand the
possibilities of analytical surveys.

It is possible to create a simple telegram bot, that send news selection, according to the user-defined settings.
It will make news browsing process more targeted and save time for main news events viewing.

---
## Requirements
[(Back to top)](#table-of-contents)

* django==3.1.3
* selenium==3.141.0
* requests==2.25.0
* pytz~=2020.4
* pyyaml==5.4.1

---
## Tools and libraries used during work on the project
[(Back to top)](#table-of-contents)

##### To complete the task, I used:
* [Django (high-level Web framework)](https://www.djangoproject.com/):
    * DB interaction
    * displaying the collected information in the admin panel
* [Selenium (tools for automating web browsers)](https://pypi.org/project/selenium/):
    * getting the news categories
    * *in a prospect: writing tests*
    * *in a prospect: processing specific news websites and additional related data*
* Python built-in packages:
    * [os](https://docs.python.org/3/library/os.html)
    * [logging](https://docs.python.org/3/library/logging.html#module-logging)
    * [subprocess](https://docs.python.org/3/library/subprocess.html)
    * [functools](https://docs.python.org/3/library/functools.html)
    * [csv](https://docs.python.org/3/library/csv.html)
    * [configparser](https://docs.python.org/3/library/configparser.html)
    * [datetime](https://docs.python.org/3/library/datetime.html)
    * [pathlib](https://docs.python.org/3/library/pathlib.html)
* Additional libraries:
    * [PyYAML](https://pypi.org/project/PyYAML/)
    * [requests](https://pypi.org/project/requests/)
    * [pytz](https://pypi.org/project/pytz/)

---
## Contributing
[(Back to top)](#table-of-contents)

Not provided at this moment

---
## License
[(Back to top)](#table-of-contents)

GPL-3.0-only

---
## Contact info
[(Back to top)](#table-of-contents)

**codemanners@gmail.com**