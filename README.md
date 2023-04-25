# feedmaker

Quickly generate an RSS feed from any website

Read the [introductory blog post](https://www.kschaul.com/post/2023/04/16/feedmaker-quickly-generate-an-rss-feed-from-any-website/)

## Development

Installation:

    pyenv virtualenv feedmaker
    pyenv activate
    pip install -r requirements.txt
    cp .env.template .env

Run locally:

    ./manage.py runserver

Run tests:

    ./manage.py test

## Deploy

    fly deploy

