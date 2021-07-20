import sys

from django.core.management.base import BaseCommand

# Main parser operation methods
from parser_app.models import Category, Partner, News
from parser_app.selen import selenium_driver
from parser_app.categories_parsing import add_categories_to_db, cycling_categories
from parser_app.counting_csv import count_csv_values, clean_csv_count_files

import selenium.webdriver
import requests
from requests.exceptions import HTTPError

# Counters
from parser_app.decorators.decorators import add_processed_newsid_to_csv, add_created_newsid_to_csv

import datetime
from pytz import utc

# Logger for ukrnet.py
from loggers_my.logger_common import logger_ukrnet

# Parsing settings
from parser_app.config_parser import CLUSTERS_QTY_LIMITER, CATEGORIES_FOR_PARSING, BROWSER_HEADLESS


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        parser.add_argument('--categories_only', '--cats', action='store_true', help='Parse categories only from ukr.net ')

    def __get_categories_all(self, driver: selenium.webdriver) -> list[dict]:
        meta_firststruct_dict = driver.execute_script('return firstStruct')
        return meta_firststruct_dict['categories']

    def __parse_categories(self):
        # Get all table-names from DB
        import django.db
        all_tables = django.db.connection.introspection.table_names()

        # Check, whether the categories table is created. If not - creating DB file and parse categories.
        if 'parser_app_category' not in all_tables:
            from parser_app.bash_scripts.process_call import create_models
            try:
                # Create necessary models for a parser work
                create_models()
            except Exception as e:
                logger_ukrnet.error(f"Got an error, while models creating. Desc: {e}")
                raise

        logger_ukrnet.info('Beginning of the news category parsing process | https://ukr.net | \n')

        # Getting selenium-driver. For browser hidden start, change "headless" to a "False"
        with selenium_driver(headless=BROWSER_HEADLESS) as driver:
            driver.get("https://www.ukr.net/news/main.html")
            # Get a list of categories with meta data
            meta_categories_list: list[dict] = self.__get_categories_all(driver)

        try:
            # Add parsed categories to DB-file
            add_categories_to_db([Category(category_id=category_dict["Id"],
                                           seo_title=category_dict['SeoTitle'],
                                           title_ru=category_dict['TitleRu'],
                                           title_ua=category_dict['TitleUa'],
                                           title_genitive_ru=category_dict['TitleGenitiveRu'],
                                           title_genitive_ua=category_dict['TitleGenitiveUa'])
                                  for category_dict in meta_categories_list
                                  ])

            logger_ukrnet.info('The news category parsing process was successfully completed | https://ukr.net | \n')
        except Exception as e:
            logger_ukrnet.error(f"Got an error, while category adding to DB. Desc: {e}")
            raise e

    def __add_partner_to_db(self, cluster_or_dup: dict) -> Partner:
        """
        """
        try:
            partner, _ = Partner.objects.update_or_create(partner_id=cluster_or_dup['PartnerId'],
                                                          defaults={"partner_id": cluster_or_dup['PartnerId'],
                                                                    "title": cluster_or_dup['PartnerTitle']})
            return partner
        except Exception as e:
            logger_ukrnet.error(f"Got an error, while partner adding to DB. Desc: {e}")

    @add_processed_newsid_to_csv
    def __get_cluster(self, category: Category) -> dict:
        """
        A generator that, yields dict with all news in cluster and break's when the news are ends.

        :param category: instance of `django.db.models.Category`
        :type category: django.db.models.Category.objects instance

        :return: cluster with sub-news or dup-news
        :rtype: dict
        """

        page = 1
        while True:
            # Example: https://www.ukr.net/news/dat/main/1/
            url = f'https://www.ukr.net/news/dat/{category.seo_title}/{str(page)}/'

            try:
                page_response = requests.get(url)
            except HTTPError as e:
                logger_ukrnet.error(f"HTTPError. Url: {url}. Desc: {e}")
                raise

            data = page_response.json()  # mixin Body.json()

            for cluster in data['tops']:
                # Process cluster if it is not advertisement
                if not cluster.get('adsType', False):
                    logger_ukrnet.debug(f"cluster Id: {cluster['Id']} | "
                                        f"News Id of the cluster: {cluster['NewsId']}| <<PROCESSING>>")

                    self.total_processed_news_cnt += 1
                    self.total_processed_news_list.append(cluster['NewsId'])

                    yield cluster

            if data['more'] is False:
                break
            page += 1

    @add_created_newsid_to_csv
    def __add_first_cluster(self, cluster: dict, partner: Partner) -> tuple[News, bool]:
        try:
            # Get or create/update first news cluster
            first_cluster, first_cluster_created = News.objects.update_or_create(news_id=cluster["NewsId"],
                                                                                 defaults={
                                                                                     "news_id": cluster['NewsId'],
                                                                                     "cluster": None,
                                                                                     "seo_title": cluster[
                                                                                         'SeoTitle'],
                                                                                     "title": cluster['Title'],
                                                                                     "description": cluster[
                                                                                         'Description'],
                                                                                     "date_created": datetime.datetime.fromtimestamp(
                                                                                         cluster['DateCreated'],
                                                                                         tz=utc),
                                                                                     "url": cluster['Url'],
                                                                                     "partner": partner})

            # Depending on the event, incrementing news counter
            if first_cluster_created:
                self.total_created_news_cnt += 1
                self.total_created_news_set.add(first_cluster.news_id)

                logger_ukrnet.debug(f"first_cluster news_id: {first_cluster.news_id} | <<CREATED>>")
            else:
                logger_ukrnet.debug(f"first_cluster news_id: {first_cluster.news_id} | <<PROCESSED>>")

            return first_cluster, first_cluster_created

        except Exception as e:
            logger_ukrnet.error(f"Cluster ID: {cluster['Id']}, News Id: {cluster['NewsId']}, Desc: {e}")


    @add_processed_newsid_to_csv
    def __get_dups(self, cluster: dict) -> dict:
        """
        A generator that, yields dict with dup-news in cluster.

        :param cluster: instance of `django.db.models.Category`
        :type cluster: dict

        :return: The dup-news which are contained in a cluster
        :rtype: dict
        """

        for dup in cluster['Dups']:

            if dup.get('News', False):
                logger_ukrnet.warning(
                    f'\nAnomaly. The list of News is in the list of Dups | Dup NewsId: {dup["NewsId"]}')

            dups_count = len(cluster['Dups'])
            if dups_count > 80:
                logger_ukrnet.warning(
                    f'Anomaly. List of Dups, contains more then 80 Dups. Dup NewsID: {dup["NewsId"]}')

            yield dup

    @add_created_newsid_to_csv
    def __add_dup_to_db(self, category: Category = None, first_cluster: News = None, cluster: dict = None,
                        dup: dict = None, partner: Partner = None, original_item_object: News = None) -> tuple[News, bool]:
        # Get or create/update Dup news
        dup_item_object, dup_created = News.objects.update_or_create(news_id=dup["NewsId"],
                                                                     defaults={"news_id": dup['NewsId'],
                                                                               "cluster": first_cluster,
                                                                               "original": original_item_object,
                                                                               "seo_title": cluster['SeoTitle'],
                                                                               "title": dup['Title'],
                                                                               "description": dup['Description'],
                                                                               "date_created": datetime.datetime.fromtimestamp(
                                                                                   dup['DateCreated'], tz=utc),
                                                                               "url": dup['Url'],
                                                                               "partner": partner,
                                                                               })
        dup_item_object.category.add(category)

        return dup_item_object, dup_created

    @add_processed_newsid_to_csv
    def __get_one_news(self, cluster: dict) -> dict:
        for one_news in cluster.get('News', []):

            logger_ukrnet.debug(f"News item NewsId: {one_news['NewsId']} | <<PROCESSING>>")

            self.total_processed_news_cnt += 1
            self.total_processed_news_list.append(one_news['NewsId'])

            yield one_news

    @add_created_newsid_to_csv
    def __add_news_to_db(self, category: Category, first_cluster: News, cluster: dict, news_item: dict,
                         partner: Partner) -> tuple[News, bool]:
        # Get or create/update first news item
        news_item_object, news_created = News.objects.update_or_create(news_id=news_item["NewsId"],
                                                                       defaults={"news_id": news_item['NewsId'],
                                                                                 "cluster": first_cluster,
                                                                                 "seo_title": cluster['SeoTitle'],
                                                                                 "title": news_item['Title'],
                                                                                 "description": news_item[
                                                                                     'Description'],
                                                                                 "date_created": datetime.datetime.fromtimestamp(
                                                                                     news_item['DateCreated'],
                                                                                     tz=utc),
                                                                                 "url": news_item['Url'],
                                                                                 "partner": partner,
                                                                                 })

        news_item_object.category.add(category)

        if news_created:
            # Depending on the event, incrementing news counter
            self.total_created_news_cnt += 1
            self.total_created_news_set.add(news_item_object.news_id)

            logger_ukrnet.debug(
                f'News item news_id: {news_item_object.news_id} | <<CREATED>>')
        else:
            logger_ukrnet.debug(
                f'News item news_id: {news_item_object.news_id} | <<PROCESSED>>')

        return news_item_object, news_created

    @add_processed_newsid_to_csv
    # News items generator with json-response cycling
    def __get_news_from_big_cluster(self, cluster: dict, category: Category) -> dict:
        page = 1
        while True:
            try:
                page_response = requests.get(f'https://www.ukr.net/ua/news/dat/'
                                        f'{category.seo_title}/'
                                        f'{cluster["SeoTitle"]}/'
                                        f'{cluster["ClusterId"]}/1/'
                                        f'{str(page)}/')
            except Exception as e:
                raise e

            data = page_response.json()  # mixin Body.json()

            # Check for standard items quantity
            if data['ipp'] != 80:
                logger_ukrnet.warning(
                    f'\nAnomaly. Items per page (ipp) != 80. Title"{cluster["Title"]}\" | NewsId {cluster["NewsId"]}')

            news_list = data['cluster']['News']
            for news_item_cluster in news_list:

                self.total_processed_news_cnt += 1
                self.total_processed_news_list.append(news_item_cluster['NewsId'])

                logger_ukrnet.debug(f"cluster Id: {news_item_cluster['Id']} | "
                                    f"News Id of the cluster: {news_item_cluster['NewsId']}| <<PROCESSING>>")

                yield news_item_cluster

            if data["more"] is False:
                break
            page += 1

    def __parse_dups(self, category: Category = None, first_cluster: News = None, cluster: dict = None,
                     original_item_object: News = None, news_item_cluster: dict = None):

        cluster_for_parsing = news_item_cluster or cluster

        for dup in self.__get_dups(cluster_for_parsing):

            self.total_processed_news_cnt += 1
            self.total_processed_news_list.append(dup['NewsId'])

            # Add news-agency to db
            partner = self.__add_partner_to_db(dup)
            # Add dup-news item to db
            dup_item_object, dup_created = self.__add_dup_to_db(category=category, first_cluster=first_cluster,
                                                                cluster=cluster, dup=dup, partner=partner,
                                                                original_item_object=original_item_object)

            # Depending on the event, incrementing news counter
            if dup_created:
                self.total_created_news_cnt += 1
                self.total_created_news_set.add(dup_item_object.news_id)

    def __parse_news_item_cluster(self, news_item_cluster: dict = None, category: Category = None,
                                  first_cluster: News = None, cluster: dict = None) -> tuple[Partner, News, bool]:
        # Add news-agency to db
        partner = self.__add_partner_to_db(news_item_cluster)
        # Add sub-news item to db
        news_item_object, news_created = self.__add_news_to_db(category, first_cluster, cluster,
                                                               news_item_cluster, partner)

        if news_created:
            logger_ukrnet.debug(f"cluster Id: {news_item_cluster['Id']} | "
                                f"News Id of the cluster: {news_item_cluster['NewsId']}| <<CREATED>>")
        else:
            logger_ukrnet.debug(f"cluster Id: {news_item_cluster['Id']} | "
                                f"News Id of the cluster: {news_item_cluster['NewsId']}| <<PROCESSED>>")

        return partner, news_item_object, news_created

    def __init__(self):
        super().__init__()
        self.total_processed_news_cnt = 0
        self.total_processed_news_list = []
        self.total_created_news_cnt = 0
        self.total_created_news_set = set()
        self.total_processed_news_cnt_previous_loop = 0
        self.total_created_news_cnt_previous_loop = 0

    def handle(self, *args, **options):

        if options['categories_only']:
            self.__parse_categories()
            sys.exit()

        self.__parse_categories()

        # Clean csv files, which was filled of NewsId from previous parsing
        clean_csv_count_files()

        logger_ukrnet.info('Beginning of the news parsing process | https://ukr.net | \n')

        # Iteration over a categories from DB
        for category in cycling_categories(category_pks=CATEGORIES_FOR_PARSING):
            logger_ukrnet.info(f'News parsing from Category \"{category.title_ua}\".')

            # News clusters counter.
            clusters_limiter_cnt = 0

            # Iteration over a news clusters
            for cluster in self.__get_cluster(category):

                # Stops the parsing when the 'CLUSTERS_QTY_LIMITER' value is reached
                if CLUSTERS_QTY_LIMITER > 0:
                    if clusters_limiter_cnt - CLUSTERS_QTY_LIMITER == 0:
                        logger_ukrnet.info(f'Clusters limiter reached (current limiter value={CLUSTERS_QTY_LIMITER}). '
                                           f'Parsing complete.')
                        break
                clusters_limiter_cnt += 1

                # Adds to DB and receives News-partner
                partner = self.__add_partner_to_db(cluster)

                # The first cluster is always exist
                first_cluster, first_cluster_created = self.__add_first_cluster(cluster, partner)

                # Adds category to the first_cluster instance
                first_cluster.category.add(category)

                # Number of news according to the source data received from ukrnet
                news_count = cluster['NewsCount']

                # Parse a Dups of the First level of nesting (cluster/dups)
                if cluster.get('Dups', False):
                    self.__parse_dups(category=category, first_cluster=first_cluster, cluster=cluster,
                                      original_item_object=first_cluster)

                # Parse sub-news if they available in cluster
                elif cluster.get('News', False):
                    # If news count less than 10, we can parse them from cluster dict
                    if news_count <= 10:
                        for news_item_cluster in self.__get_one_news(cluster):

                            # Get or update/create news-partner and news_item_cluster in a DB
                            partner, news_item_object, _ = self.__parse_news_item_cluster(
                                news_item_cluster=news_item_cluster, category=category, first_cluster=first_cluster,
                                cluster=cluster)

                            # Parse dup-news if they available in sub-news_item_cluster of the cluster
                            if news_item_cluster.get('Dups', False):

                                self.__parse_dups(category=category, first_cluster=first_cluster, cluster=cluster,
                                                  original_item_object=news_item_object,
                                                  news_item_cluster=news_item_cluster)

                    # If news count greater than 10, for reducing requests to ukr.net, separate json processing required
                    if news_count > 10:
                        for news_item_cluster in self.__get_news_from_big_cluster(cluster, category):

                            # Add news-agency and news_item_cluster to DB
                            partner, news_item_object, _ = self.__parse_news_item_cluster(
                                news_item_cluster=news_item_cluster, category=category, first_cluster=first_cluster,
                                cluster=cluster)

                            # Parse dup-news if they available in sub-news_item_cluster of the cluster
                            if news_item_cluster.get('Dups', False):
                                self.__parse_dups(category=category, first_cluster=first_cluster, cluster=cluster,
                                                  original_item_object=news_item_object,
                                                  news_item_cluster=news_item_cluster)

            category_processed_news_counter = self.total_processed_news_cnt - self.total_processed_news_cnt_previous_loop
            category_created_news_counter = self.total_created_news_cnt - self.total_created_news_cnt_previous_loop

            logger_ukrnet.info(f'Number of news PROCESSED in Category "{category.title_ua}" (counter info):'
                               f' {category_processed_news_counter}.')
            logger_ukrnet.info(f'Number of news CREATED in Category "{category.title_ua}" (counter info):'
                               f' {category_created_news_counter}.\n')

            self.total_processed_news_cnt_previous_loop = self.total_processed_news_cnt
            self.total_created_news_cnt_previous_loop = self.total_created_news_cnt

        logger_ukrnet.info(f'Total news PROCESSED (csv info): {count_csv_values(file_count_type="processed")}. '
                           f'Total news CREATED (csv info): {count_csv_values(file_count_type="created")}\n')
