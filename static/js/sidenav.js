/* Open the sidenav */
function openNav() {
    $("#sideList").css({
        "width": "100%"
    });
}

/* Close/hide the sidenav */
function closeNav() {
    $("#sideList").css({
        "width": "0"
    });
}

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
    $("#sideList").animate({
        scrollTop: 0
    });
}