// Add Google Analytics Event Tracking to resource download links.
ckan.module("google-analytics", function(jQuery, _) {
  "use strict";
  return {
    options: {
      googleanalytics_resource_prefix: ""
    },
    initialize: function() {
      jQuery("a.resource-url-analytics").on("click", function() {
        var resource_url = encodeURIComponent(jQuery(this).prop("href"));
        if (resource_url) {
          ga("send", "event", "Resource", "Download", resource_url);
        }
      });
    }
  };
});
