// PASSWORD GENERATOR BELOW

function copyToClipboard() {
    var copyText = document.getElementById("generated-password").textContent.trim();

    navigator.clipboard.writeText(copyText)
        .then(function() {
            alert("Copied the password: " + copyText);
        })
        .catch(function(error) {
            console.error("Failed to copy text: ", error);
        });
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

// PASSWORD MANAGER BELOW

function toggleVisibility(index) {
    var passwordElement = document.querySelectorAll(".user-password")[index];
    var button = document.querySelectorAll(".toggle-visibility")[index];

    var visiblePassword = passwordElement.querySelector('.visible-password');
    var hiddenPassword = passwordElement.querySelector('.hidden-password');
 
    if (visiblePassword.classList.contains("hidden")) {
        visiblePassword.classList.remove("hidden");
        hiddenPassword.classList.add("hidden");
        button.textContent = "Hide";
    } else {
        visiblePassword.classList.add("hidden");
        hiddenPassword.classList.remove("hidden");
        button.textContent = "Show";
    }
}

// Initialize Show/Hide button text on load
document.addEventListener("DOMContentLoaded", function() {
    var buttons = document.querySelectorAll(".toggle-visibility");
    buttons.forEach(function(button, index) {
        toggleVisibility(index);
    });
});

// Delete button functionality
function setDeleteValues(website) {
    
    // Select the span with data-password-id attribute
    const passwordIdSpan = document.querySelector(`button[data-website="${website}"] + span[data-password-id]`);
    
    if (passwordIdSpan) {
        const passwordId = passwordIdSpan.getAttribute("data-password-id");
        
        document.querySelector("#delete-website").value = website;
        document.querySelector("#delete-password-id").value = passwordId;

        // Submit the delete form
        document.getElementById("delete-password-form").submit();
    }
}
