Meetup Union - a tool for meetup admins
=======================================


This is a quick script I started building for the Bristol [Codehub](http://codehub.org.uk/) meetup
to help us find whether there was attendee crossover from another meetup
in a given event.

Installation
------------

This script was build on python 3.6.5 but will probably work on most python 3.x.x.

Here are the installation steps:

- [Create and activate a virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtualenv/#creating-a-virtualenv)
- Install the requirements:
    ```bash
    pip install -r requirements.txt
    ```
- Create Meetup API key if you don't have one. You can do that [here](https://secure.meetup.com/meetup_api/key/).
- Expose your key in your shell's environment.

```bash
export MEETUP_API_KEY=xxxxxxxx
```


Example Usage
-------------

The script takes 3 arguments:

1. The url string identifier of your event's meetup
1. The url string identifier of your target meetup
1. The url int identifier of your event

**Example:**

```bash
python meetup_union.py 'CodeHub-Bristol' 'python-dbbug' 251030267
```


Massive Disclaimer
------------------

This is as quick 'n dirty as it can get.

The api client library will easily bomb out at any the little
random failures that the meetup API can have.

Feel free to use/improve/further build upon, eg this could be extended
to fetch other stats (meetup-wide instead of event-specific or to
perform completely different lookups).
