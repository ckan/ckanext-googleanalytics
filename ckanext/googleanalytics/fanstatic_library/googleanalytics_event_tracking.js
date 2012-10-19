// Add Google Analytics Event Tracking to resource download links.
this.ckan.module('google-analytics', function(jQuery, _) {
  return {
    options: {
      googleanalytics_resource_prefix: ''
    },
    initialize: function() {
      resource_prefix = this.options.googleanalytics_resource_prefix;
      jQuery('a.resource-url-analytics').on('click', function(){
          resource_url = resource_prefix + encodeURIComponent(this.href);
          _gaq.push(['_trackPageview', resource_url]);
      });
    }
  }
});
