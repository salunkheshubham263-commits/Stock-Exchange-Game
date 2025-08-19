if(document.body.classList.contains('loading_page')){
    const START = document.querySelector(".start");
    const loader = document.querySelector(".loading_line");
    const privacy = document.querySelector(".privacy")

    START.addEventListener("click", () => {
        loader.style.display = "flex";
        privacy.style.display = "none";
        START.style.display = "none";
    })
}
if(document.body.classList.contains('home_page')){
    const main = document.querySelector(".main");
    const forgotPassword = document.querySelector(".forgot_password");
    const loginForm = document.querySelector("#login_form");
    const password = document.querySelector("#forgotPassword_form");
    const Back_button = document.querySelector("#back_login");
    const loginButton = document.querySelector("#u_login");
    
    forgotPassword.addEventListener("click", () => {
        password.style.display = "block";
        loginForm.style.display = "none";
    })
    Back_button.addEventListener("click", () => {
        password.style.display = "none";
        loginForm.style.display = "block";
    })
    loginButton.addEventListener("click", () => {
        const email = document.querySelector("#email1").value;
        const pass = document.querySelector("pass1").value;

        if(email === "" || pass === ""){
            alert("Please fill email and password");
        }else{
        loginForm.style.display = "none";
        main.style.filter = "blur(0)";
        }
    })
}
