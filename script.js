function validateForm() {
    let inputs = document.querySelectorAll("input");
    for (let i = 0; i < inputs.length; i++) {
        if (inputs[i].value === "") {
            alert("All fields are required");
            return false;
        }
    }
    return true;
}
