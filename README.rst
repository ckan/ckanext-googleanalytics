A CKAN extension for doing things with Google Analytics:

* It puts the relevant tracking code in your templates for you
  (including tracking code for external resource download links)

* It provides a page showing top packages and resources

* It inserts download stats onto individual package pages

Installation
============

1. Install the extension as usual, e.g.

    ::

    $ pip install -e  hg+https://bitbucket.org/sebbacon/ckanext-googleanalytics#package=/ckanext-googleanalytics

2. Edit your development.ini (or similar) with:

   ::

      googleanalytics.id = UA-1010101-1
      googleanalytics.username = googleaccount@gmail.com
      googleanalytics.password = googlepassword
      googleanalytics.show_downloads = true
      # the following *must* match profile name in GA dashboard
      googleanalytics.profile_name = mydomain.com

   That last comment is worth emphasising.  Due to the strange
   relationship between tracking IDs and profiles, you need to get
   that right.  It's the relevant value in the "Name" column for the
   list of "Website Profiles" that you see when you click on an
   Analytics Account link in the Google Analytics homepage.
   E.g. you'll need two clicks from the analytics home page to see the
   profile name.  Sometimes your profile name might have a trailing
   slash; you need to include that, too, if so.

   Note also that your password will probably be readable by other
   people; so you may want to set up a new gmail account specifically
   for accessing your gmail profile.

   If ``show_downloads`` is set, a download count for resources will
   be displayed on individual package pages.
            
3. Wait a day or so for some stats to be recorded in Google

4. Import Google stats by running the following command from 
   ``src/ckanext-googleanalytics``::

	paster loadanalytics --config=../ckan/development.ini

   (Of course, pointing config at your specific site config)

5. Look at some stats within CKAN

   Once your GA account has gathered some data, you can see some basic
   information about the most popular packages at:
   http://mydomain.com/analytics/package/top

   By default the only data that is injected into the public-facing
   website is on the package page, where number of downloads are
   displayed next to each resource.

6. Consider putting the import command as a daily cron job, or
   remember to run it by hand!

Testing
=======

There are some very high-level functional tests that you can run using::

  (pyenv)~/pyenv/src/ckan$ nosetests --ckan ../ckanext-googleanalytics/tests/

(note -- that's run from the CKAN software root, not the extension root)

Future
======

This is a bare-bones, first release of the software.  There are
several directions it could take in the future.

Because we use Google Analytics for recording statistics, we can hook
into any of its features.  For example, as a measure of popularity, we
could record bounce rate, or new visits only; we could also display
which datasets are popular where, or highlight packages that have been
linked to from other locations.
