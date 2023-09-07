# Wiki Top 25 By Date - Simple

## Task

> Given a date in a string format, retrieve the top 25 pages of the ~~day~~ week

## The Setup

*Ok, not sure how this will go but I am going to try and narrate my process here. This will be basically a stream of conscious as I go through the tasks.*

I came up with this idea after clicking around [Wikipedia](https://en.wikipedia.org/). Obviously lots of traffic, so I figured you could somehow see a list of top pages for the day. So I added this to my task list. I am going to talk about how I walked through the project and toss out thoughts and ideas as I do it.

## The Breakdown

### Live in reality, not the idea.

Many times in my career I have been handed an idea and have been asked to turn it into something that exists. The best thing to do is to take that idea and test it out to make sure it's a viable idea.

In this case, my quest had already taken a stumble because I was pulling a project from my head not reality. I was cruising Wikipedia and discovered what I was looking for, [Wikipedia: Top 25 Report](https://en.wikipedia.org/wiki/Wikipedia:Top_25_Report) and promptly ran into my first problem. There was a page that listed the top 25 pages, but not for a specific date, but a date range. So record-scratch and all that, time to update my project plan from ~~day~~ to week.

If I had started with my original idea, I would already have a refactor on my hands, so crisis avoided. Then I noticed something interesting about the dates.

### What's a week?

In development, it's imperative everyone involved is on the same page. Even using the same words like "a range of a week" can be very dangerous when assumptions are made regarding when a "week" occurs. In my Wikipedia case, I clicked the "Last Week's Report" to get an idea of the URL structure I would be working with to dynamically call content from week's past. Turns out the week according to Wikipedia runs from Sunday to Saturday, now while this is not a wildly deviant schedule it could have been different, like Wed to Wed. Doing a little bit of research up front will save you in the end.

### We can build it!

Ok, lets architect a rough solution:

```mermaid
graph TD;
    Date-->|"(string)"|get[Establish Week Range];
    get-->|"(string)"|call[Request Page from Week];
    call-->|"(url)"|grab[Get Page data];
    grab-->|"(json)"|parse[Parse the JSON and return the list];
``````

We will get our string date, use Python to convert the date string to a parseable date object so we can figure out the start and end of the week. Eventually we will need format that start/end date into a string to build the url to parse. As a caveat, if the date given is within the current week, we need a default return since the currently active week does not have a date range in the url.

Once we will build the full url, make the request via Python and then collect the returned JSON. Read through the json, collect the list of page titles in order and return a list with the page order intact.

### BUILDME

So we build our Python script against the 3.11.X version. There are plenty of [naming conventions](https://365datascience.com/tutorials/python-tutorials/python-naming-conventions/) to choose from and still fit within [PEP8 style guides](https://peps.python.org/pep-0008/). Whatever you choose, be consistent. Chances are your workgroup already has a set style and if not, pick one. I usually use camelCase or snake_case.

In this script the command line structure will be `python topPages.py "2023-06-08"` to make it a little easier on ourselves. We should always think about what is going to be consuming/using our script so using a good format for the inputs will help us later. Using `June 8th, 2023` is going to give us troubles with the `th` ordinal and interpreting the `,` likewise in the other direction `june 6 8` is going to be clunky and might be awkward in use.

So with that setup, we are using argparse to grab those arguments from the command line. If we don't include the date, we should provide some help to show our users what flags/format to use. In our project:

```
❯ python topPages.py
usage: topPages.py [-h] YYYY-MM-DD
topPages.py: error: the following arguments are required: YYYY-MM-DD
```

### Time is an arrow and pendulum.

Python's DateTime module has come a very long way over the years. Howerver dealing with time zone conversion especially will make a Python Dev go insane. Helper libraries like Arrow and Pendulum can be really cool additions but both are getting a bit behind in updates with Arrow's last release in Jan/2022 and Pendulum even longer at July/2020. So for now, we will just use datetime since we do not need to worry about timezones.

### Your Request will be Returned in the Order it was Received

[Python Requests](https://requests.readthedocs.io/en/latest/) has to be one of the longest running, most popular libraries around. It just makes web calls easy and human usable. So we are going to use [Poetry](https://python-poetry.org/) and add it to our project.

The wiki page will come to use via the API as JSON, but the data we actually need will come as the page html. So we are going to use Beautiful Soup to turn the html data into useful data. We need to confirm the table we will be getting has a reliable tag or class or id we can use to find it. Using just the `<table>` tag is not a great idea as there is more than 1 table but thankfully the table we need is using a unique class `<table class="wikitable">`.

### I Didn't think Soup was that pretty.

[Real Python](https://realpython.com/beautiful-soup-web-scraper-python/) has a nice tutorial for BS4. Since we have a unique class id, we are going to use the `find` method for the table tag. Then we have BS4 parse the content to dig through the table rows and parse out each `<td>` as text so we can collect the info we would like. We are only interested in the following columns: Rank, Article and Views. So we just need the first, second and fourth columns. With a quick print out of our results, we need to clean it up a little and remove extra `\n` and it would be nice to our future selves to convert our rank and views from a string to actual numbers as well as the url for the page since we already have it in hand.

### Tada!

We have our list of dictionaries with the ranks of the pages from a given date. Now moving forward, we would most likely want to keep this preserved as a list especially if we are passing it onto other things. But for now, we want to see the fruit of our labors so lets iterate it and spit it out for all to see with a little pizzazz!

```
python topPages.py 2023-06-03

 Top 25 Pages for the week: 05/28/2023 to 06/03/2023  

1. Spider-Man: Across the Spider-Verse - 1756037 views
2. The Little Mermaid (2023 film) - 1699397 views
3. ChatGPT - 1354094 views
4. Fast X - 1115810 views
5. Tina Turner - 1027003 views
6. Deaths in 2023 - 930877 views
7. Succession (TV series) - 917926 views
8. Ted Lasso - 617121 views
9. Al Pacino - 607104 views
10. Danny Masterson - 587101 views
11. The Super Mario Bros. Movie - 578641 views
12. Memorial Day - 578470 views
13. Guardians of the Galaxy Vol. 3 - 578046 views
14. Elizabeth Holmes - 556697 views
15. Phillip Schofield - 554067 views
16. Chennai Super Kings - 528717 views
17. Nikola Jokić - 524143 views
18. MS Dhoni - 521268 views
19. Jimmy Butler - 520140 views
20. Ravindra Jadeja - 517284 views
21. Spider-Man: Into the Spider-Verse - 509922 views
22. Bijou Phillips - 504596 views
23. Rivaba Jadeja - 496491 views
24. Premier League - 487274 views
25. Halle Bailey - 460661 views
```

## Conclusion

Well that was fun! Hopefully you had fun too!