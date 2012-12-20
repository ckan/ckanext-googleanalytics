// Add Google Analytics Event Tracking to resource download links.
this.ckan.module('google-analytics', function(jQuery, _) {
  return {
    options: {
      googleanalytics_resource_prefix: ''
    },
    initialize: function() {
      jQuery('a.resource-url-analytics').on('click', function() {
          var resource_prefix = this.options.googleanalytics_resource_prefix;
          var resource_url = resource_prefix + encodeURIComponent(jQuery(this).prop('href'));
          if (resource_url) {
            _gaq.push(['_trackPageview', resource_url]);
          }
      });
    }
  }
});
