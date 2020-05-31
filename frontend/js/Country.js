// hide until country data is loaded
$('main.main').hide();

var searchParams = new URLSearchParams(window.location.search);
var country_query = searchParams.get('country');
var countryPromise = Promise.resolve( $.get('/api/countries/'+country_query) )


countryPromise.then(function(data) {
    console.log('Country loaded:', data)
    $('main.main').show();
}, function(err) {
    console.log('ERR:', err.statusText)
})

