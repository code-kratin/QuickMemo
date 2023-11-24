function func(){
    // console.log('Hello');
     var search= document.getElementsByClassName('search')[0].value;
    // var currentURL = window.location.href;

    // // Add the directory you want to append
    // var newDirectory = search;

    // // Construct the new URL by concatenating the current URL and the new directory
    // var newURL = currentURL + '/search/' + newDirectory;
    // console.log(newURL);
    // // Redirect to the new URL
    // window.location.href = newURL;
    
    var url= new URL(window.location.href);
    var search_params= url.searchParams;
    search_params.set('q', search);
    return url.toString();

}
// function filterurl(i){
//     var url= new URL(window.location.href);
//     var filtername= document.getElementsByClassName('filtername')[i].innerText;
//     console.log(typeof(filtername));
//     const selected = document.querySelectorAll('.test')[i].selectedOptions;
//     const values = Array.from(selected).map(el => el.value);
//     var search_params= url.searchParams;
//     search_params.set(filtername, values);
//     new_url=url.toString();
// }