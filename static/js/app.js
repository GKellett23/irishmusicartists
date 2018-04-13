// Self calling function in order the jQuery parameter and avoid potential conflicts with other libraries
// https://stackoverflow.com/questions/1401349/how-to-avoid-conflict-between-jquery-and-prototype
(function($) {
    // Initialise the date picker for the create venue
    // Can be used in other pages so is in app.js
    $("#datepicker").datepicker({
      dateFormat: "dd/mm/yy"
    });
})(jQuery)