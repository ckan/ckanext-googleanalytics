/*
* Copyright (C) 2022 Entidad Pública Empresarial Red.es
*
* This file is part of "dge_ga (datos.gob.es)".
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 2 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program. If not, see <http://www.gnu.org/licenses/>.
*/

// Add Google Analytics Event Tracking to resource download links.
this.ckan.module('google-analytics', function(jQuery, _) {
  return {
    options: {
      googleanalytics_resource_prefix: ''
    },
    initialize: function() {
      jQuery('a.resource-url-analytics').on('click', function() {
          var resource_url = encodeURIComponent(jQuery(this).prop('href'));
          if (resource_url) {
            ga('send', 'event', 'Resource', 'Download', resource_url);
          }
      });
    }
  }
});
