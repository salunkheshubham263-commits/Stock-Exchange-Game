if(document.body.classList.contains('Logo_body')){
    // After 5 seconds move to loading page.

    setTimeout(() => {
        window.location.href = "/loading";
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
        window.location.href = "/form  ";
    })

}
if(document.body.classList.contains('privacyPolicy')){
    const back = document.querySelector(".back");

    back.addEventListener("click", () => {
        window.location.href = "/loading"
    })
}
if(document.body.classList.contains('form_page')){
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
    signUpForm.addEventListener("submit", (event) => {
        const email = document.querySelector("#email2").value;
        const pass = document.querySelector("#pass2").value;
        const firstName = document.querySelector("#first_name").value;
        const lastName = document.querySelector("#last_name").value;
        const username = document.querySelector("#username").value;



        if(email === "" || pass === "" || firstName === "" || lastName === "" || username === ""){
            alert("Please fill all required information!");
            event.preventDefault();
        }
    })

}
if(document.body.classList.contains('home_page')){
    const leaderBoard = document.querySelector(".leaderboard");
    const digital_clock = document.querySelector(".digital-clock");
    const help = document.querySelector(".help");

    help.addEventListener("click", () => {
        window.location.href = "/help"
    })
    

    leaderBoard.addEventListener("click", () => {
        window.location.href = "/leaderboard";
    })

    function updateClock(){
        const now = new Date();
        let hours = now.getHours();
        const minutes = String(now.getMinutes()).padStart(2,'0');
        const ampm = hours >= 12 ? 'Pm' : 'Am';

        hours = hours % 12;
        hours = hours ? hours : 12; // "0" should be "12"

        digital_clock.textContent = `${hours}:${minutes}${ampm}`;
    }

    setInterval(updateClock, 1000); //refresh every srconds
    updateClock(); //run once at start
}
if(document.body.classList.contains('leaderBoard_page')){
    const back = document.querySelector(".back_png");

    back.addEventListener("click", () => {
        window.location.href = "/home";
    })
}
if(document.body.classList.contains('help_page')){
    const back = document.querySelector("#back_png");

    back.addEventListener("click", () => {
        window.location.href = "/home";
    })
}

async function loadCompanies() {
  const res = await fetch("/api/stocks/list");
  const data = await res.json();
  const table = document.getElementById("companyTable");

  // clear old rows except headers
  table.querySelectorAll("tr:not(:first-child):not(:nth-child(2))").forEach(tr => tr.remove());

  data.forEach(stock => {
    let row = document.createElement("tr");
    row.innerHTML = `
      <td>${stock.symbol}</td>
      <td>₹${stock.price}</td>
      <td>
        <button onclick="buyStock('${stock.symbol}')">Buy</button>
        <button onclick="sellStock('${stock.symbol}')">Sell</button>
      </td>
    `;
    table.appendChild(row);
  });
}

async function buyStock(symbol) {
  const qty = prompt(`Enter quantity of ${symbol} to buy:`);
  if (!qty) return;
  const res = await fetch("/api/stocks/buy", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({symbol, qty})
  });
  const result = await res.json();
  alert(result.message);
  loadCompanies();
}

async function sellStock(symbol) {
  const qty = prompt(`Enter quantity of ${symbol} to sell:`);
  if (!qty) return;
  const res = await fetch("/api/stocks/sell", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({symbol, qty})
  });
  const result = await res.json();
  alert(result.message);
  loadCompanies();
}

setInterval(loadCompanies, 5000); // refresh prices every 5s
loadCompanies();

