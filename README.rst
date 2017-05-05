CKAN Google Analytics Extension
===============================

**Status:** Production

**CKAN Version:** >= 1.5.*

A CKAN extension that both sends tracking data to Google Analytics and
retrieves statistics from Google Analytics and inserts them into CKAN pages.

Features
--------

* Puts the Google Analytics asynchronous tracking code into your page headers
  for basic Google Analytics page tracking.

* Adds Google Analytics Event Tracking to resource download links, so that
  resource downloads will be displayed as Events in the Google Analytics
  reporting interface.

* Adds Google Analytics Event Tracking to some API calls so that usage of the
  API can be reported on via Google Analytics.

* Add Google Analytics Event Tracking function that can be used in any exstension
  to create your custom events tracking.

  ``ckanext.googleanalytics.plugin.ga_event_tracking``

  function arguments:

    - `user`: The user name.

    - `event_type`: Custom event type. For example "changed event".

    - `request_obj_type`: Custom request object type. For example "Resourse".

    - `request_function`: Custom request function. For example "Download".

    - `request_id`: Request id, can be dataset ID or resource ID for example.

* Adds Google Analytics Event Tracking to group links on the home page,
  user profile links, editing and saving user profiles, etc.

  *Only if* ``googleanalytics.track_events = true`` *is in your CKAN ini file.*

  *CKAN 1.x only*.

* Puts download stats into dataset pages, e.g. "[downloaded 4 times]".

  *CKAN 1.x only.*

* Provides a ``/analytics/dataset/top`` page that shows the most popular
  datasets and resources

  *CKAN 1.x only*

CKAN 1.x Support
----------------

To use ckanext-googleanalytics with CKAN 1.x, make sure you have
``ckan.legacy_templates = true`` in your CKAN ini file.

Installation
------------

1. Install the extension as usual, e.g. (from an activated virtualenv):

    ::

    $ pip install -e  git+https://github.com/ckan/ckanext-googleanalytics.git#egg=ckanext-googleanalytics
    $ pip install -r ckanext-googleanalytics/requirements.txt

2. Edit your development.ini (or similar) to provide these necessary parameters:

    ::

      googleanalytics.id = UA-1010101-1
      googleanalytics.account = Account name (i.e. data.gov.uk, see top level item at https://www.google.com/analytics)
      googleanalytics.username = googleaccount@gmail.com
      googleanalytics.password = googlepassword

   Note that your password will probably be readable by other people;
   so you may want to set up a new gmail account specifically for
   accessing your gmail profile.

3. Edit again your configuration ini file to activate the plugin
   with:

   ::

      ckan.plugins = googleanalytics

   (If there are other plugins activated, add this to the list.  Each
   plugin should be separated with a space).

4. If you are using this plugin with a version of CKAN < 2.0 then you should
   also put the following in your ini file::

       ckan.legacy_templates = true


5. Finally, there are some optional configuration settings (shown here
   with their default settings)::

      googleanalytics_resource_prefix = /downloads/
      googleanalytics.domain = auto
      googleanalytics.track_events = false
      googleanalytics.fields = {}

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

   If ``track_events`` is set, Google Analytics event tracking will be
   enabled. *CKAN 1.x only.* *Note that event tracking for resource downloads
   is always enabled,* ``track_events`` *enables event tracking for other
   pages as well.*

   ``fields`` allows you to specify various options when creating the tracker. See `Google's documentation <https://developers.google.com/analytics/devguides/collection/analyticsjs/field-reference>`.

Domain Linking
--------------

This plugin supports cross-domain tracking using Googles' site linking feature.

To use this, set the ``googleanalytics.linked_domains`` configuration option to a (comma seperated) list of domains to report for.

See `Googles' documentation<https://support.google.com/analytics/answer/1034342?hl=en>`_ for more information

Setting Up Statistics Retrieval from Google Analytics
-----------------------------------------------------

1. Run the following command from ``src/ckanext-googleanalytics`` to
   set up the required database tables (of course, altering the
   ``--config`` option to point to your site config file)::

       paster initdb --config=../ckan/development.ini

2. Optionally, add::

       googleanalytics.show_downloads = true

   to your CKAN ini file. If ``show_downloads`` is set, a download count for
   resources will be displayed on individual package pages.

3. Follow the steps in the *Authorization* section below.

4. Restart CKAN (e.g. by restarting Apache)

5. Wait a while for some stats to be recorded in Google

6. Import Google stats by running the following command from
   ``src/ckanext-googleanalytics``::

       paster loadanalytics credentials.json --config=../ckan/development.ini

   (Of course, pointing config at your specific site config and credentials.json at the
   key file obtained from the authorization step)
   Ignore warning `ImportError: file_cache is unavailable when using oauth2client >= 4.0.0`

7. Look at some stats within CKAN

   Once your GA account has gathered some data, you can see some basic
   information about the most popular packages at:
   http://mydomain.com/analytics/dataset/top

   By default the only data that is injected into the public-facing
   website is on the package page, where number of downloads are
   displayed next to each resource.

8. Consider running the import command reguarly as a cron job, or
   remember to run it by hand, or your statistics won't get updated.


Authorization
--------------

Before ckanext-googleanalytics can retrieve statistics from Google Analytics, you need to set up the OAUTH details which you can do by following the `instructions <https://developers.google.com/analytics/devguides/reporting/core/v3/quickstart/service-py>`_ the outcome of which will be a file with authentication key. These steps are below for convenience:

1. Visit the `Google APIs Console <https://code.google.com/apis/console>`_

2. Sign-in and create a project or use an existing project.

3. In the `Service accounts pane <https://console.developers.google.com/iam-admin/serviceaccounts>`_ choose your project and create new account. During creation check "Furnish a new private key" -> JSON type. Write down "Service account ID"(looks like email) - it will be used later.

4. Save downloaded file - it will be used by `loadanalytics` command(referenced as <credentials.json>)

5. Go to `GoogleAnalytics console <https://analytics.google.com/analytics/web/#management>`_ and chose ADMIN tab.

6. Find "User management" button in corresponding column. Add service account using Service account ID(email) generated in 3rd step and grant "Read" role to it.


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
