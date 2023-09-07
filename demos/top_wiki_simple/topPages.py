import argparse  # for command line parsing
from datetime import datetime, timedelta  # for date parsing. timedelta is for date math
from bs4 import BeautifulSoup  # for parsing html
import requests  # for making http requests

# Yes all this could be tighter/cleaner, but I wanted to show some different things as well as talk about it on the way through


def parse_datestamp(
    datestamp: str,
):  # datestamp is a string, so it's type is str. This is a type hint, not a type check. If we wanted to enforce the type, we could use a library like mypy
    # This is a docstring. It's a good idea to include these to document what a function does
    """
    Take the given datestamp string and return it as a date object.
    """
    return datetime.strptime(
        datestamp, "%Y-%m-%d"
    )  # convert the datestamp string to a date object %Y = YYYY, %m = MM, %d = DD and return it


def get_week_range(datestamp: datetime):
    """
    Take a date object and return a tuple of the start and end dates for the week that date is in.
    """
    start = datestamp - timedelta(
        days=datestamp.weekday() + 1
    )  # get the start of the week but subtract the weekday number + 1 since the library considers Monday to be the first day of the week
    end = start + timedelta(days=6)
    current_sunday = (
        datetime.today() - timedelta(days=datestamp.weekday() + 1)
    ).date()  # get the current Sunday this week to make sure its not the date we have requested. We would need a different url if it is
    return (
        start,
        end,
        current_sunday == start.date(),
    )  # compare the current Sunday to the start of the week. If they are the same, we are in the current week. If not, we are in a previous week. Additionally we could return this as a dictionary.


def build_url(week_range: tuple):
    """
    Take a tuple of start and end dates and build a url to get the top pages for that week. If the date is this week, use an alternate page name.
    """
    # example target url = https://en.wikipedia.org/w/api.php?action=parse&format=json&page=Wikipedia%3ATop_25_Report%2FAugust_20_to_26%2C_2023&formatversion=2
    base_url = "https://en.wikipedia.org/w/api.php?action=parse&format=json&formatversion=2&page="
    # Wikipedia%3ATop_25_Report%2FAugust_20_to_26%2C_2023
    (
        start,
        end,
        is_current_week,
    ) = week_range  # unpack the tuple into start and end variables and I like to add a boolean to indicate if we are in the current week and the variable named as a question
    if is_current_week:
        return f"{base_url}Wikipedia%3ATop_25_Report"  # return the url for the current week since it doesn't have a date range
    else:
        # If it's not the current week, we need to build the date range.
        # Unfortunately, the date range is not consistent. If the date range is within the same month, it's `Month_D_to_D,_YYYY`. If it's not, it's `Month_D_to_Month_D,_YYYY`. So we need to check for that. Also the day is not zero padded, so we need to check for that as well.
        if start.month == end.month:
            return f"{base_url}Wikipedia%3ATop_25_Report%2F{start.strftime('%B_%-d_to_')}{end.strftime('%-d,_%Y')}"  # if it's the same month, we don't need to include the month in the end date
        else:
            return f"{base_url}Wikipedia%3ATop_25_Report%2F{start.strftime('%B_%-d_to_')}{end.strftime('%B_%-d,_%Y')}"  # if it's not the same month, we need to include the month in the end date


def get_page(url: str):
    """
    Take a url and return the page as a BeautifulSoup object.
    """
    try:
        result = requests.get(url)  # try and make the request
    except (
        requests.exceptions.RequestException
    ) as e:  # catch any exceptions and print them
        print(e)
        raise SystemExit(e)
    content = result.json()  # get json format from our request
    return content.get("parse").get("text")  # return the text from the json response


def extract_top_table(page_content: str):
    """
    Take the page content and return the top table as a BeautifulSoup object.
    """
    soup = BeautifulSoup(page_content, "html.parser")  # parse the html
    return soup.find(
        "table", class_="wikitable"
    )  # find the table we want (it has a class of wikitable)


def parse_top_table(top_table: BeautifulSoup):
    """
    Take the top table and parse it.
    """
    table_items = []
    rows = top_table.find_all("tr")  # find all the rows in the table
    for row in rows[
        1:
    ]:  # loop through the rows, skipping the first one (it's the header)
        cells = row.find_all("td")  # find all the cells in the row
        rank = cells[0].text.strip()  # get the text from the first cell (the rank)
        title = cells[1].text.strip()  # get the text from the second cell (the title)
        url = cells[1].find("a").get("href")  # get the url from the title
        views = cells[3].text.strip()  # get the text from the third cell (the views)
        table_items.append(
            {
                "rank": int(rank),
                "title": title,
                "url": url,
                "views": int(
                    views.replace(",", "")
                ),  # remove the comma from the views and convert to an int, now we could get fancy and use locale to do this, but I'm not going to do that here since we will always use the same locale
            }
        )  # append a dictionary to the table_items list, this will help us reference things in the future when we reference the list items by key
    return table_items


def display_table_items(table_items: list, week_range: tuple):
    """
    Take the table items and display them.
    """
    start_range, end_range, is_current_week = week_range  # unpack the tuple
    start_range = start_range.strftime("%m/%d/%Y")  # format the start date
    end_range = end_range.strftime("%m/%d/%Y")  # format the end date
    week = ""
    if is_current_week:
        week = "which is this week"  # let us know if it's the current week
    print(
        "\n",
        f"Top 25 Pages for the week: {start_range} to {end_range} {week}",
        "\n",
    )  # print the week range
    for item in table_items:
        print(
            f"{item.get('rank')}. {item.get('title')} - {item.get('views')} views"
        )  # print the rank, title, and views from the table_items list. We are using the get method to get the value from the dictionary. We could also use item['rank'] but if the key doesn't exist, it will throw an exception. Using the get method will return None if the key doesn't exist and is nicer way to handle it.


if __name__ == "__main__":
    # So this could be in a separate method, but it's here for simplicity
    parser = argparse.ArgumentParser(
        description="Get top pages from Wikipedia."
    )  # create parser object
    parser.add_argument(
        "datestamp",
        metavar="YYYY-MM-DD",
        type=str,
    )  # add argument. since it is positional, we don't need a flag

    args = parser.parse_args()  # parse arguments from the command line

    # If our string will be '2023-06-08' for our Week Range, it should be 2023-06-04 to 2023-06-10
    stamp_obj = parse_datestamp(
        args.datestamp
    )  # call parse_datestamp with the datestamp argument (which is a string)

    week_range = get_week_range(
        stamp_obj
    )  # call get_week_range with the date object. We are going to get a tuple back vs building a string since we will most likely want to do more with the dates. It will be more difficult to do that if we build a string.

    url = build_url(week_range)  # build the url

    page_content = get_page(url)  # make the request

    top_table = extract_top_table(page_content)  # extract the top table using BS4

    table_items = parse_top_table(top_table)  # parse the top table using BS4

    display_table_items(table_items, week_range)  # display the table items
