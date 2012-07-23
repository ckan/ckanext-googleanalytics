CKAN Google Analytics Extension
===============================

**Status:** Production

**CKAN Version:** 1.5.*


Overview
--------

A CKAN extension for doing things with Google Analytics:

* It puts the relevant tracking code in your templates for you
  (including tracking code for external resource download links)

* It provides a page showing top packages and resources

* It inserts download stats onto individual package pages

Installation
------------

1. Install the extension as usual, e.g. (from an activated virtualenv):

    ::

    $ pip install -e  git+https://github.com/okfn/ckanext-googleanalytics.git#egg=ckanext-googleanalytics

2. Edit your development.ini (or similar) to provide these necessary parameters:

    ::

      googleanalytics.id = UA-1010101-1
      googleanalytics.username = googleaccount@gmail.com
      googleanalytics.password = googlepassword

   Note that your password will probably be readable by other people;
   so you may want to set up a new gmail account specifically for
   accessing your gmail profile.


3. Run the following command from ``src/ckanext-googleanalytics`` to
   set up the required database tables (of course, altering the
   ``--config`` option to point to your site config file)::

       paster initdb --config=../ckan/development.ini

4. Edit again your configuration ini file to activate the extension
   with:

   ::

      ckan.plugins = googleanalytics

   (If there are other plugins activated, add this to the list.  Each
   plugin should be separated with a space)


   Finally, there are some optional configuration settings (shown here
   with their default settings)::

      googleanalytics.resource_prefix = /downloads/
      googleanalytics.domain = auto
      googleanalytics.show_downloads = true
      googleanalytics.track_events = false

   ``resource_prefix`` is an arbitrary identifier so that we can query
   for downloads in Google Analytics.  It can theoretically be any
   string, but should ideally resemble a URL path segment, to make
   filtering for all resources easier in the Google Analytics web
   interface.

   ``domain`` allows you to specify a domain against which Analytics
   will track users.  You will usually want to leave this as ``auto``;
   if you are tracking users from multiple subdomains, you might want
   to specify something like ``.mydomain.com``.
   See `Google's documentation
   <http://code.google.com/apis/analytics/docs/gaJS/gaJSApiDomainDirectory.html#_gat.GA_Tracker_._setDomainName>`_
   for more info.

   If ``show_downloads`` is set, a download count for resources will
   be displayed on individual package pages.

   If ``track_events`` is set, Google Analytics event tracking will be
   enabled.

5. Restart CKAN (e.g. by restarting Apache)

6. Wait a while for some stats to be recorded in Google

7. Import Google stats by running the following command from
   ``src/ckanext-googleanalytics``::

	paster loadanalytics --config=../ckan/development.ini

   (Of course, pointing config at your specific site config)

8. Look at some stats within CKAN

   Once your GA account has gathered some data, you can see some basic
   information about the most popular packages at:
   http://mydomain.com/analytics/dataset/top

   By default the only data that is injected into the public-facing
   website is on the package page, where number of downloads are
   displayed next to each resource.

9. Consider running the import command reguarly as a cron job, or
   remember to run it by hand, or your statistics won't get updated.

Testing
-------

There are some very high-level functional tests that you can run using::

  (pyenv)~/pyenv/src/ckan$ nosetests --ckan ../ckanext-googleanalytics/tests/

(note -- that's run from the CKAN software root, not the extension root)

Future
------

This is a bare-bones, first release of the software.  There are
several directions it could take in the future.

Because we use Google Analytics for recording statistics, we can hook
into any of its features.  For example, as a measure of popularity, we
could record bounce rate, or new visits only; we could also display
which datasets are popular where, or highlight packages that have been
linked to from other locations.

We could also embed extra metadata information in tracking links, to
enable reports on particular types of data (e.g. most popular data
format by country of origin, or most downloaded resource by license)
