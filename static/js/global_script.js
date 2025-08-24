if(document.body.classList.contains('Logo_body')){
    // After 5 seconds move to loading page.

    setTimeout(() => {
        window.location.href = "loading_page.html";
    }, 5000);
}


if(document.body.classList.contains('loading_page')){
    const START = document.querySelector(".start");
    const loader = document.querySelector(".loading_line");
    const privacy = document.querySelector(".privacy")
    const loader_line = document.querySelector(".internal_loading_line")

    START.addEventListener("click", () => {
        loader.style.display = "flex";
        privacy.style.display = "none";
        START.style.display = "none";
    })
    // when loading line width is 100% move to home page.

    loader_line.addEventListener("animationend", () => {
        window.location.href = "home_page.html";
    })

}
if(document.body.classList.contains('home_page')){
    const main = document.querySelector(".main");
    const forgotPassword = document.querySelector(".forgot_password");
    const loginForm = document.querySelector("#login_form");
    const password = document.querySelector("#forgotPassword_form");
    const Back_button = document.querySelector("#back_login");
    const loginButton = document.querySelector("#u_login");
    const signUpButton = document.querySelector(".sign_up");
    const signUpForm = document.querySelector("#signUp_form");
    const Back_button1 = document.querySelector("#back_login2");
    const signUpButton1 = document.querySelector("#signUp_button");
    
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
        const pass = document.querySelector("#pass1").value;

        if(email === "" || pass === ""){
            alert("Please fill email and password");
        }else{
        loginForm.style.display = "none";
        main.style.filter = "blur(0)";
        }
    })
    signUpButton.addEventListener("click", () => {
        loginForm.style.display = "none";
        signUpForm.style.display = "block";
    })
    Back_button1.addEventListener("click", () => {
        signUpForm.style.display = "none";
        loginForm.style.display = "block";
    })
    signUpButton1.addEventListener("click", () => {
        const email = document.querySelector("#email2").value;
        const pass = document.querySelector("#pass2").value;
        const firstName = document.querySelector("#first_name").value;
        const lastName = document.querySelector("#last_name").value;
        const username = document.querySelector("#username").value;



        if(email === "" || pass === "" || firstName === "" || lastName === "" || username === ""){
            alert("Please fill all required information!");
        }else{
        signUpForm.style.display = "none";
        main.style.filter = "blur(0)";
        }
    })
}
