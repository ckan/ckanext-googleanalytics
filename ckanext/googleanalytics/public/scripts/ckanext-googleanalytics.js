(function ($) {
  $(document).ready(function () {
    // Google Analytics event tracking

    // alert($(this).attr('href'));

    // group links on home page
    $('body.home div.group a').click(function() {
      _gaq.push(['_trackEvent', 'Home', 'Click: Group Link', $(this).attr('href')]);
    });

    // clicking on user name (go to profile)
    $('div.account span.ckan-logged-in a').first().click(function() {
      _gaq.push(['_trackEvent', 'User', 'Click: User Name', $(this).attr('href')]);
    });

    // In user profile, clicking on Edit Profile
    $('body.user div#minornavigation a')
      .filter(function(index) {return $(this).text() === "Edit Profile";})
      .click(function() {
      _gaq.push(['_trackEvent', 'User', 'Click: Tab', 'Edit Profile']);
    });

    // Clicking Save Changes on Edit Profile page
    $('body.user.edit input#save').click(function() {
      _gaq.push(['_trackEvent', 'User', 'Click: Button', 'Save Profile Changes']);
    });

    // Clicking on any dataset link on User Profile page
    $('body.user.read ul.datasets a').click(function() {
      _gaq.push(['_trackEvent', 'User', 'Click: Dataset Link', $(this).attr('href')]);
    });

    // Any of the group links on /group
    $('body.group.index table.groups a').click(function() {
      _gaq.push(['_trackEvent', 'Group', 'Click: Group Link', $(this).attr('href')]);
    });

    // Clicking any of the right hand sidebar tags on /group/X
    $('body.group.read div#sidebar h2')
      .filter(function(index) {return $(this).text() === "Tags";})
      .next('ul')
      .find('a')
      .click(function() {
      _gaq.push(['_trackEvent', 'Group', 'Click: Tag', $(this).attr('href')]);
    });

    // Visiting /group/history/X
    // Compare Button on /group/history/X
    // Compare Button on /dataset/history/X
    // Tags on right hand sidebar of /dataset/X
    // Download button on any /dataset/X/resource[> page
    // Data API button on any /dataset/X/resource[> page
  });
}(jQuery));
