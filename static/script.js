function copyPassword() {
    /* Get the text field */
    var copyText = document.getElementById("generated-password");

    /* Select the text field */
    copyText.select();
    copyText.setSelectionRange(0, 99999); /* For mobile devices */

    /* Copy the text inside the text field */
    document.execCommand("copy");
}
function updateSliderValue(value) {
    document.getElementById("min_max_display").textContent = value;
    sessionStorage.setItem("min_max", value);
}

document.addEventListener("DOMContentLoaded", function() {
    var min_max = sessionStorage.getItem("min_max");
    if (min_max) {
        document.getElementById("min_max_display").textContent = min_max;
        document.getElementById("slider").value = min_max;
    }
});

function updateCheckboxState(checkboxID) {
    var checkbox = document.getElementById(checkboxID);
    var checkboxValue = checkbox.checked;

    sessionStorage.setItem(checkboxID, String(checkboxValue));
}

document.addEventListener("DOMContentLoaded", function() {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');

    checkboxes.forEach(function(checkbox) {
        var checkboxID = checkbox.id;
        var checkboxValue = sessionStorage.getItem(checkboxID);

        if (checkboxValue) {
            checkbox.checked = (checkboxValue === 'true');
        }
    });
});