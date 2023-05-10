import os
import datetime
import requests
import unittest
from unittest.mock import patch

import lxml
from requests_file import FileAdapter
from requests_html import Element, HTMLSession, user_agent
from django.test import TestCase
from django.utils.text import slugify
from ..utils import get_feed_items, get_metadata, parse_item

"""
Run tests with:

    ./manage.py test

If you need to save fixtures first for a given test, run:

    SAVE_FIXTURES=1 ./manage.py test -k TestGetMetadata

The tests will likely fail, but all requested urls will be saved as fixutres.
Then, run the tests as normal to test against the fixtures:

    ./manage.py test
"""


script_dir = os.path.dirname(__file__)

SAVE_FIXTURES = os.environ.get("SAVE_FIXTURES", False)
fixture_urls = []


def url_to_filename(url):
    """
    Convert a url to a valid filename
    """
    slugged = slugify(url)
    path = os.path.join(script_dir, "fixtures", f"{slugged}.html")
    return path


def save_fixture(url):
    """
    Save the contents of url to the fixtures directory
    """
    path = url_to_filename(url)
    r = requests.get(url, headers={"User-Agent": user_agent()})
    with open(path, "w") as f:
        f.write(r.text)


def mock_get(url, *args, **kwargs):
    """
    Replaces requests.get() with a function that returns the results from reading a local file instead
    """
    fixture_urls.append(url)
    path = url_to_filename(url)
    url = f"file://{path}"
    session = HTMLSession()
    session.mount("file://", FileAdapter())
    r = session.get(url)
    return r


def make_element(html, url):
    """
    Helper to return requests_html.Element with the given html and url
    """
    return Element(element=lxml.html.fromstring(html), url=url)


class TestGetFeedData(unittest.TestCase):
    def tearDown(self):
        if SAVE_FIXTURES:
            for url in fixture_urls:
                save_fixture(url)

    @patch("maker.utils.requests.get")
    def test_wapo(self, mock_requests):
        mock_requests.side_effect = mock_get

        url = "https://www.washingtonpost.com"
        selector_item = 'div[data-link-group="most-read"] h2'
        expected = [
            {
                "title": "What key players at Fox News said about the network and its viewers",
                "description": None,
                "link": "https://www.washingtonpost.com/media/2023/03/10/fox-news-lawsuit-key-players/",
                "uniqueid": "https://www.washingtonpost.com/media/2023/03/10/fox-news-lawsuit-key-players/",
            },
            {
                "title": "Kevin McCarthy joins the insurrection",
                "description": None,
                "link": "https://www.washingtonpost.com/opinions/2023/03/10/kevin-mccarthy-i-know-nothing-insurrection-questions/",
                "uniqueid": "https://www.washingtonpost.com/opinions/2023/03/10/kevin-mccarthy-i-know-nothing-insurrection-questions/",
            },
            {
                "title": "Russia’s hypersonic missile attack on Ukraine highlights Western vulnerability",
                "description": None,
                "link": "https://www.washingtonpost.com/world/2023/03/10/russia-hypersonic-missiles-western-vulnerability/",
                "uniqueid": "https://www.washingtonpost.com/world/2023/03/10/russia-hypersonic-missiles-western-vulnerability/",
            },
            {
                "title": "Ron DeSantis’s book ban mania targets Jodi Picoult — and she hits back",
                "description": None,
                "link": "https://www.washingtonpost.com/opinions/2023/03/10/ron-desantis-book-bans-martin-county-jodi-picoult/",
                "uniqueid": "https://www.washingtonpost.com/opinions/2023/03/10/ron-desantis-book-bans-martin-county-jodi-picoult/",
            },
            {
                "title": "Silicon Valley Bank closed in second-biggest bank failure in U.S. history",
                "description": None,
                "link": "https://www.washingtonpost.com/technology/2023/03/09/silicon-valley-bank-shares/",
                "uniqueid": "https://www.washingtonpost.com/technology/2023/03/09/silicon-valley-bank-shares/",
            },
        ]

        actual = get_feed_items(url, selector_item, get_items_metadata=False)
        self.maxDiff = None
        self.assertEqual(actual, expected)

    @patch("maker.utils.requests.get")
    def test_reckless(self, mock_requests):
        mock_requests.side_effect = mock_get

        expected = [
            {
                "title": 'FACS\nStill Life In Decay ("crimson Crush" Color Vinyl)',
                "link": "https://www.reckless.com",
                "description": 'FACS\nStill Life In Decay ("crimson Crush" Color Vinyl)\nTrouble in Mind\nThe always reliable FACS are back with a new one in 2023. After a few albums with a lot of studio trickery & manipulation, this one is mostly pretty straight forward recording-wise. The result is probably the most accurate documentation of what a force they are as a live band. Driving & repetitive THIS HEAT esque rhythms with sparse & brittle guitar from Brian. His voice is also way on top here which also gives this record a different feel. Another great one from these local heroes. RECOMMENDED.\nAvailable at: Belmont and Milwaukee Ave\nNew LP $17.99',
                "uniqueid": 'FACS\nStill Life In Decay ("crimson Crush" Color Vinyl)',
            },
        ]

        actual = get_feed_items(
            "https://www.reckless.com",
            selector_item="td.main .item",
            selector_title="tr",
            selector_description="table",
            get_items_metadata=False,
        )
        self.maxDiff = None
        self.assertEqual(len(actual), 10)
        self.assertEqual(actual[0], expected[0])


class TestGetMetadata(unittest.TestCase):
    def tearDown(self):
        if SAVE_FIXTURES:
            for url in fixture_urls:
                save_fixture(url)

    @patch("maker.utils.requests.get")
    def test_wapo_article(self, mock_requests):
        mock_requests.side_effect = mock_get

        actual = get_metadata(
            "https://www.washingtonpost.com/arts-entertainment/2020/02/06/oscars-what-should-have-won-best-picture/"
        )
        expected = {
            "title": "Perspective | The Oscars always get it wrong. Here are the real best pictures of the past 47 years.",
            "description": "With the perspective of time, we can now now discern what movie was actually the best. So here we go, year by year...",
            "categories": ["Movies"],
            "pubdate": datetime.datetime(2020, 2, 6, 14, 0, 5),
            "updateddate": datetime.datetime(2023, 3, 11, 17, 35, 15),
        }
        self.assertEqual(actual, expected)

    @patch("maker.utils.requests.get")
    def test_nyt_article(self, mock_requests):
        mock_requests.side_effect = mock_get

        actual = get_metadata(
            "https://www.nytimes.com/2023/03/10/realestate/duluth-minnesota-climate-change.html"
        )
        expected = {
            "title": "Out-of-Towners Head to ‘Climate-Proof Duluth’",
            "description": "The former industrial town in Minnesota is coming to terms with its status as a refuge for people moving from across the country because of climate change.",
            "categories": [
                "Real Estate",
                "Real Estate and Housing (Residential)",
                "Population",
                "Temperature",
                "Global Warming",
                "Duluth (Minn)",
            ],
            "pubdate": datetime.datetime(2023, 3, 10, 10, 0, 28),
            "updateddate": datetime.datetime(2023, 3, 12, 18, 46, 3),
        }
        self.assertEqual(actual, expected)


class TestParseItem(unittest.TestCase):
    def test_relative_href(self):
        url = "https://daily.bandcamp.com/best-jazz"
        actual = parse_item(
            make_element(
                '<a href="/best-jazz/the-best-jazz-on-bandcamp-february-2023"><a>', url
            ),
            url,
            "a",
            None,
            "a",
            False,
            False,
        )["link"]

        expected = "https://daily.bandcamp.com/best-jazz/the-best-jazz-on-bandcamp-february-2023"
        self.assertEqual(actual, expected)

    def test_absolute_href(self):
        url = "https://daily.bandcamp.com/best-jazz"
        actual = parse_item(
            make_element(
                '<a href="https://daily.bandcamp.com/best-jazz/the-best-jazz-on-bandcamp-february-2023"><a>',
                url,
            ),
            url,
            "a",
            None,
            "a",
            False,
            False,
        )["link"]

        expected = "https://daily.bandcamp.com/best-jazz/the-best-jazz-on-bandcamp-february-2023"
        self.assertEqual(actual, expected)

    def test_strip_url_params_false(self):
        url = "https://daily.bandcamp.com/best-jazz"
        actual = parse_item(
            make_element(
                '<a href="https://daily.bandcamp.com/best-jazz/the-best-jazz-on-bandcamp-february-2023?some-query=exists"><a>',
                url,
            ),
            url,
            "a",
            None,
            "a",
            False,
            False,
        )["link"]

        expected = "https://daily.bandcamp.com/best-jazz/the-best-jazz-on-bandcamp-february-2023?some-query=exists"
        self.assertEqual(actual, expected)

    def test_strip_url_params_true(self):
        url = "https://daily.bandcamp.com/best-jazz"
        actual = parse_item(
            make_element(
                '<a href="https://daily.bandcamp.com/best-jazz/the-best-jazz-on-bandcamp-february-2023?some-query=exists"><a>',
                url,
            ),
            url,
            "a",
            None,
            "a",
            False,
            True,
        )["link"]

        expected = "https://daily.bandcamp.com/best-jazz/the-best-jazz-on-bandcamp-february-2023"
        self.assertEqual(actual, expected)

    def test_title_and_description_required(self):
        url = "https://www.mbta.com/news"
        item = parse_item(
            make_element(
                """
                    <div class="news-entry-hr-row news-entry-hr-col news-entry-item">
                        <p>April 21, 2023</p>
                        <p>
                            <a class="news-entry-title" href="/news/2023-04-21/mbta-announces-additional-blue-line-schedule-revisions">MBTA Announces Additional Blue Line Schedule Revisions</a>
                        </p>
                        <p>The Blue Line evening weekday shuttle bus diversions will begin at 8 PM on April 24-27 and May 1-4. The work taking place on the Blue Line will focus on lifting speed restrictions.</p>
                    </div>
                    """,
                url,
            ),
            url,
            "a",
            None,
            "a",
            False,
            False,
        )

        self.assertEqual(item["title"], "MBTA Announces Additional Blue Line Schedule Revisions")
        self.assertEqual(item["description"], None)
