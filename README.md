# feedmaker

Quickly generate an RSS feed from any website

Read the [introductory blog post](https://www.kschaul.com/post/2023/04/16/feedmaker-quickly-generate-an-rss-feed-from-any-website/)

## Development

Installation:

    # Install uv if you haven't already: https://docs.astral.sh/uv/getting-started/installation/
    # curl -LsSf https://astral.sh/uv/install.sh | sh

    uv sync
    cp .env.template .env

Run locally:

    uv run ./manage.py runserver

Run tests:

    uv run ./manage.py test

## Deploy

    fly deploy

