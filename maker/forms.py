from django import forms


class FeedForm(forms.Form):
    url = forms.URLField(label="URL")
    feed_title = forms.CharField(label="Feed title")
    selector_item = forms.CharField(label="CSS selector for the feed items")
    selector_title = forms.CharField(label="CSS selector for the item title")
    selector_description = forms.CharField(
        label="CSS selector for the item description"
    )
    selector_link = forms.CharField(label="CSS selector for the item link")
    get_items_metadata = forms.BooleanField(label="Include metadata for each item?")
