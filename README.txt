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
            

3. Look at some stats within CKAN

  Once your GA account has gathered some data, you can see some basic
  information about the most popular packages at:
  http://localhost:5000/analytics/package/top

TODO
====

* Turn the access-package-data-from-analytics-within-ckan
functionality into something resembling an API
* Understand the standard way to do caching in CKAN
