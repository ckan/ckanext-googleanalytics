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

/*::::: SEO EVENTS :::::*/
$(document).ready(function() {
  var breadcrumbs = $('ul.breadcrumb').find('li');
  if (breadcrumbs.length < 2) {
    return;
  }
  // Only 2nd sector needed (3rd breadcrumb).
  var event_category = breadcrumbs[2].innerText;
  event_category = formatDataLayerValue(event_category);

  /* #3 Datasets search form (magnifying glass button). */
  // This form is at every page so no if needed.
  $("#search-block-form").submit(function() {
    // Only for datasets search.
    if ($('#edit-search-filter-ckan').is(':checked')) {
      var termino_busqueda = $('#edit-search-block-form--2').val();
      termino_busqueda = termino_busqueda === '' ? 'campo vacio' : formatDataLayerValue(termino_busqueda);
      dataLayer.push({
        'event_action': 'buscar',
        'event_category': event_category,
        'termino_busqueda': termino_busqueda,
        'event_label': termino_busqueda,
        'event': 'ev.buscar'
      });
    }
  });
  /* #6 Subscribe/unsubscribe newsletter. */
  // This form is at every page so no if needed.
  $("#simplenews-block-form-21").submit(function() {
    if ($('#edit-condiciones').is(':checked')) {
      var accionNewsletter = 'suscribirse';
      if ($('#edit-action2-unsubscribe').is(':checked')) {
        accionNewsletter = 'darse de baja';
      }
      dataLayer.push({
        'event_action': 'accion_newsletter',
        'event_category': event_category,
        'accionNewsletter': accionNewsletter,
        'event_label': accionNewsletter,
        'event': 'ev.accion_newsletter'
      });
    }
  });
  /* Events #1, #2 and #4. */
  if ($('#dataset-resources').length) {
    // Events #1 and #2.
    $('.resource-item').on('click', 'a.btn-primary', function() {
      var resource = $(this).closest('.resource-item');
      var nombre_distribucion = formatDataLayerValue(resource.find('.resource-item-name').find('strong')[0].innerText);
      var formato_distribucion = formatDataLayerValue(resource.find('.format')[0].innerText);
      var event_action, ev;
      var buttonIcon = $(this).find('i')[0];
      // #1 Download file click.
      if ($(buttonIcon).hasClass('icon-download')) {
        event_action = 'descargar';
        ev = 'ev.descargar_documento';
      }
      // #2 External link click.
      else if ($(buttonIcon).hasClass('icon-external-link')) {
        event_action = 'acceder';
        ev = 'ev.acceder_recurso';
      }
      dataLayer.push({
        'event_action': event_action,
        'event_category': event_category,
        'nombre_distribucion': nombre_distribucion,
        'formato_distribucion': formato_distribucion,
        'event_label': nombre_distribucion + '|' + formato_distribucion,
        'event': ev
      });
    });
    // Event #4 Add new dataset. When submit button is pressed it redirects to dataset page.
    if (localStorage.getItem('datasetAdded') != null) {
      var sectores = localStorage.getItem('sectores');
      if (sectores != null) {
        dataLayer.push({
          'event_action': 'subir_datos',
          'event_category': event_category,
          'sectores': sectores,
          'event_label': sectores,
          'event': 'ev.subir_datos'
        });
        localStorage.removeItem('sectores');
      }
      localStorage.removeItem('datasetAdded');
    }
  }
  /* #3 Datasets search form (catalog page). */
  else if ($('#dataset-search-form').length) {
    $('#dataset-search-form').submit(function() {
      var termino_busqueda = $('#dataset-search-form').find('input').val();
      termino_busqueda = termino_busqueda === '' ? 'campo vacio' : formatDataLayerValue(termino_busqueda);
      dataLayer.push({
        'event_action': 'buscar',
        'event_category': event_category,
        'termino_busqueda': termino_busqueda,
        'event_label': termino_busqueda,
        'event': 'ev.buscar'
      });
    });
  }
  /* #4 Add new dataset. */
  // First, get the values selected in dataset creation page.
  else if ($('#dataset-edit').length) {
    $('#dataset-edit').submit(function() {
      var options = $('#field-theme option:selected');
      var values = $.map(options, function(option) {
        return $(option).val();
      });

      var sectores = '';
      for (var i = 0; i < values.length; i++) {
        var uri = values[i].split('/');
        var sector = uri[uri.length - 1]; // Last item on URI.
        sector = sector.replace('-', ' '); // Replace separators.
        sectores += i < values.length - 1 ? sector + ':' : sector;
      }

      localStorage.setItem('sectores', sectores);
    });
  }
  // Then, add tracking for submit button pressed.
  else if ($('#resource-edit').length) {
    $('#resource-edit').submit(function() {
      if ($('.btn-primary')[0].name === 'save') {
        localStorage.setItem('datasetAdded', 'true');
      }
    });
  }
  /* #7 Run API query. */
  else if ($('#swagger-ui-container').length) {
    $('.site-content__wrapper').on('click', 'input.submit', function() {
      var endpoint = $(this).closest('.operations');
      var funcion_api = endpoint.find('span.path')[0].innerText;
      var formato_respuesta = endpoint.find('.response-content-type').find('select').val();
      dataLayer.push({
        'event_action': 'acceder_api',
        'event_category': event_category,
        'funcion_api': funcion_api,
        'formato_respuesta': formato_respuesta,
        'event_label': funcion_api + '|' + formato_respuesta,
        'event': 'ev.acceder_api'
      });
    });
  }
  /* #8 Download SPARQL query result. */
  else if ($('#yasqe').length) {
    $('.site-content__wrapper').on('click', 'button.yasr_downloadIcon', function() {
      var formato_descarga = formatDataLayerValue($('div.yasr_btnGroup').find('.selected')[0].innerText);
      dataLayer.push({
        'event_action': 'acceder_sparql',
        'event_category': event_category,
        'formato_descarga': formato_descarga,
        'event_label': formato_descarga,
        'event': 'ev.acceder_sparql'
      });
    });
  }
  /* #9 Click on 'Download as...' or 'Save as...' in public dashboard. */
  else if ($('.dge-dashboard').length) {
    // This object is needed to know in which chart is the button clicked.
    var chart = { div: '', export_main: '' };
    // When the mouse enters in a button area.
    $('.dge-dashboard').on('mouseenter', 'a', function() {
      // If it's a button from the main menu.
      if ($(this).parent().children('ul').length) {
        var exportMain = $(this).closest('.export-main');
        if (exportMain.length) {
          chart.export_main = chart.export_main[0];
          // To get the chart title it's necessary to get the parent.
          var chartDiv = $(exportMain).closest('.chartdiv');
          if (!chartDiv.length) {
            chartDiv = $(exportMain).closest('.smallchartdiv');
          }
          chart.div = $(chartDiv).parent('div')[0];
          chart.export_main = exportMain;
        }
      }
    });
    $(document).on('click', 'a', function() {
      // If this <a> is an .export-main children.
      if ($(this).closest('.export-main').length) {
        var menuOptions = $(chart.export_main).find('li');
        // Targets list are the 1st and 2nd menu (6th <li> element).
        var target = $([menuOptions[0], menuOptions[5]]).find('li.active')[0];
        // Check if <a> is in one of the menu targets.
        if (target !== undefined) {
          var formato_descarga = formatDataLayerValue(this.innerText);

          // If it's a half column chart.
          if ($(chart.div).hasClass('chartdiv2')) {
            // Two chart divs, get and compare first (for example).
            var divs = $(chart.div).parent().find('.chartdiv2');
            var column = $(divs[0]).is(chart.div) ? 0 : 1;
            // Half-size charts are in the same order (column) that divs.
            chart.div = $(chart.div).parent().find('.halfwidth')[column];
          }
          var titulo_grafica = formatDataLayerValue($(chart.div).find('strong')[0].innerText);

          dataLayer.push({
            'event_action': 'acceder_cuadro_mando',
            'event_category': event_category,
            'titulo_grafica': titulo_grafica,
            'formato_descarga': formato_descarga,
            'event_label': titulo_grafica + '|' + formato_descarga,
            'event': 'ev.acceder_cuadro_mando'
          });
        }
      }
    });
  }
});
