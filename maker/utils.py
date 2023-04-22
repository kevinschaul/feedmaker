import datetime
import logging
from urllib.parse import urljoin

import requests
from requests_html import HTMLResponse, HTMLSession, user_agent
from django.core.cache import cache

ITEMS_LIMIT = 10


def cached_session_get(url, timeout=60 * 60 * 24):
    """
    Returns the parsed HTML of the given url, first checking the cache for the
    contents
    """
    session = HTMLSession()

    cached = cache.get(url)
    if not cached:
        cached = requests.get(url, headers={"User-Agent": user_agent()})
        cache.set(url, cached, timeout=timeout)

    return HTMLResponse._from_response(cached, session)


def get_metadata(url):
    r = cached_session_get(url, timeout=60 * 60 * 24)

    meta_standardized = {
        "og:title": "title",
        "og:description": "description",
        "article:section": "categories",
        "article:tag": "categories",
        "article:published_time": "pubdate",
        "article:modified_time": "updateddate",
    }

    metadata = {}
    for meta in r.html.find("meta"):
        key = meta.attrs.get("property")
        value = meta.attrs.get("content")
        standardized = meta_standardized.get(key)
        if standardized:
            if standardized in ["categories"]:
                if not standardized in metadata:
                    metadata[standardized] = []
                metadata[standardized].append(value)
            elif standardized in ["pubdate", "updateddate"]:
                metadata[standardized] = datetime.datetime.strptime(
                    value[:19], "%Y-%m-%dT%H:%M:%S"
                )
            else:
                metadata[standardized] = value
    return metadata


def parse_item(
    item_html,
    url,
    selector_title,
    selector_description,
    selector_link,
    get_items_metadata,
):
    #  Initialize the item with a title and description, which are required by Django feed generator
    item = {"title": None, "description": None}

    if selector_title:
        el_title = item_html.find(selector_title, first=True)
        if el_title:
            item["title"] = el_title.text

    if selector_description:
        el_description = item_html.find(selector_description, first=True)
        if el_description:
            item["description"] = el_description.text

    if selector_link:
        el_link = item_html.find(selector_link, first=True)
        if el_link:
            link = urljoin(url, el_link.attrs["href"])
            item["link"] = link
            item["uniqueid"] = link  # TODO optionally trim query parameters

            if get_items_metadata:
                try:
                    metadata = get_metadata(link)
                    item = item | metadata
                except Exception as e:
                    logging.warning(f"Could not get items metadata for {link}: {e}")
                    pass

    if "uniqueid" not in item:
        if "title" in item:
            item["uniqueid"] = item["title"]

    if "link" not in item:
        item["link"] = url

    return item


def get_feed_items(
    url,
    selector_item,
    selector_title="a",
    selector_description=None,
    selector_link="a",
    get_items_metadata=False,
):
    r = cached_session_get(url, timeout=60 * 5)

    items_raw = r.html.find(selector_item)
    items = [
        parse_item(
            i,
            url,
            selector_title,
            selector_description,
            selector_link,
            get_items_metadata,
        )
        for i in items_raw[:ITEMS_LIMIT]
    ]

    return items
