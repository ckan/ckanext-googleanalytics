/*
* Copyright (C) 2025 Entidad Pública Empresarial Red.es
*
* This file is part of "dge-ga (datos.gob.es)".
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 2 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
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
  var seccion_s2 = breadcrumbs[2].innerText;
  seccion_s2 = formatDataLayerValue(seccion_s2);


  $("#search-block-form").submit(function() {
    // Only for datasets search.
      var termino_busqueda = $('#edit-search-block-form--2').val();
      termino_busqueda = termino_busqueda === '' ? 'campo vacio' : formatDataLayerValue(termino_busqueda);
      dataLayer.push({
        'seccion_s2': seccion_s2,
        'category': 'Buscador',
        'element': 'Buscar',
        'termino_busqueda': termino_busqueda,
        'event': 'click_buscar'
      });

  });
  /* Events #1, #2 and #4. */
  if ($('#dataset-resources').length) {
    // Events #1 and #2.
    $('.accordion-button').on('click', 'a.btn-primary-resource', function() {
      var resource = $(this).closest('.accordion-item');
      var nombre_distribucion = formatDataLayerValue(resource.find('.accordion-header-title')[0].innerText);
      var formato_distribucion = formatDataLayerValue(resource.find('.text-truncate')[0].innerText);
      // #1 Download file click.
      if ($(this).hasClass('resource-download')){
        var literal_boton = formatDataLayerValue(resource.find('.download-icon')[0].alt);
        var download_url = formatDataLayerValue(resource.find('a.btn-primary-resource')[0].href);
        dataLayer.push({
          'seccion_s2': seccion_s2,
          'category': 'Download',
          'element': literal_boton,
          'context': nombre_distribucion,
          'formato_descarga': formato_distribucion,
          'download_url': download_url,
          'event': 'click_download'
        });
      }
      // #2 External link click.
      if ($(this).hasClass('resource-external-link')){
        var literal_boton = formatDataLayerValue(resource.find('.external-icon')[0].alt);
        var exit_url = formatDataLayerValue(resource.find('a.btn-primary-resource')[0].href);
        dataLayer.push({
          'seccion_s2': seccion_s2,
          'category': 'Exit button',
          'element': 'Acceder',
          'exit_url': exit_url,
          'context': nombre_distribucion,
          'formato_descarga': formato_distribucion,
          'event': 'exit_link'
        });
      }
    });
    // Event #4 Add new dataset. When submit button is pressed it redirects to dataset page.
    if (localStorage.getItem('datasetAdded') != null) {
      var sectores = localStorage.getItem('sectores');
      if (sectores != null) {
        dataLayer.push({
          'seccion_s2': seccion_s2,
          'category': 'Form',
          'element': 'Terminar',
          'categoria_datos': sectores,
          'event': 'subir_datos'
        });
        localStorage.removeItem('sectores');
      }
      localStorage.removeItem('datasetAdded');
    }
  }
  /* #3 Datasets search form (catalog page). */
  else if ($('#dataset-filters-search-form').length) {
    $('#dataset-filters-search-form').submit(function() {
      var termino_busqueda = $('#dataset-filters-search-form').find('input').val();
      termino_busqueda = termino_busqueda === '' ? 'campo vacio' : formatDataLayerValue(termino_busqueda);
      dataLayer.push({
        'seccion_s2': seccion_s2,
        'category': 'Buscador',
        'element': 'Buscar',
        'termino_busqueda': termino_busqueda,
        'event': 'click_buscar'
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
    $('#resource-edit').submit(function(event) {
      clicked_button = event.originalEvent.submitter
      if ($(clicked_button).hasClass('btn-save-resource')) {
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
      var titulo_context = formatDataLayerValue($(this).closest('.endpoints').prev('.heading').find('a')[0].innerText);
      dataLayer.push({
        'seccion_s2': 'Api',
        'category': 'test api',
        'element': 'pruebalo',
        'context': titulo_context,
        'funcion_api': funcion_api,
        'formato_respuesta': formato_respuesta,
        'event': 'click_api'
      });
    });
  }
  /* #8 Download SPARQL query result. */
  else if ($('#yasqe').length) {
    $('.site-content__wrapper').on('click', 'button.yasr_downloadIcon', function() {
      var formato_descarga = formatDataLayerValue($('div.yasr_btnGroup').find('.selected')[0].innerText);
      var title_boton = formatDataLayerValue($(this).attr('title'));
      dataLayer.push({
        'seccion_s2': seccion_s2,
        'category': 'Download',
        'element': title_boton,
        'context': 'queryResults',
        'formato_descarga': formato_descarga,
        'event': 'click_download'
      });
    });
  }
});
