A CKAN extension for doing things with Google Analytics:

* It sticks tracking code in your templates for you
* It provides a way for your controllers to access data from GA

The second item is all hard-coded, rough-and-ready, proof-of-concept
at the moment.

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
      # the following *must* match profile name in GA dashboard
      googleanalytics.profile_name = mydomain.com/  
            
3. Wait a day or so for some stats to be recorded in Google

4. Import Google stats by running the following command from 
   ``src/ckanext-googleanalytics``::

	paster loadanalytics --config=../ckan/development.ini

   (Of course, pointing config at your specific site config)

5. Look at some stats within CKAN

  Once your GA account has gathered some data, you can see some basic
  information about the most popular packages at:
  http://localhost:5000/analytics/package/top

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

TODO
====

* Turn the access-package-data-from-analytics-within-ckan
functionality into something resembling an API
* Understand the standard way to do caching in CKAN
