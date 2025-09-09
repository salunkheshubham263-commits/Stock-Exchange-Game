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

let isTrading = false;
let chartPaused = false;
let datasetMap = {};
let latestData = []; // cache to reuse API result

// ================== FETCH STOCK LIST ==================
async function fetchStockList() {
    if (isTrading || chartPaused) return; // skip while trading
    try {
        const res = await fetch("/api/stocks/list");
        latestData = await res.json();
    } catch (err) {
        console.error("Error fetching stock list:", err);
    }
}

// ================== LOAD COMPANIES ==================
function loadCompanies() {
    if (isTrading || chartPaused || latestData.length === 0) return;
    const table = document.querySelector(".list_of_companies");
    table.querySelectorAll("tr:not(:first-child):not(:nth-child(2))").forEach(tr => tr.remove());

    latestData.forEach(stock => {
        let row = document.createElement("tr");
        row.innerHTML = `
            <td>${stock.symbol}</td>
            <td>$${stock.price}</td>
            <td style="display: flex;">
                <button class="buy" onclick="buyStock('${stock.symbol}')">Buy</button>
                <button class="sell" onclick="sellStock('${stock.symbol}')">Sell</button>
            </td>
        `;
        table.appendChild(row);
    });
}

// ================== CHART ==================
// Make sure your HTML has: <canvas id="stockchart"></canvas>
let ctx = document.querySelector("#stockchart").getContext("2d");
let stockChart = new Chart(ctx, {
  type: "line",
  data: {
    labels: [],
    datasets: [] // datasets will be added dynamically
  },
  options: {
    responsive: true,
    interaction: {
        mode: 'nearest',
        axis: 'x',
        intersect: false
    },
    plugins: {
        zoom: {
            zoom: {
                wheel: {
                    enabled: true // zoom with mouse wheel
                },
                pinch: {
                    enabled: true
                },
                mode: 'xy', // zoom with X and Y
                onZoom: ({chart}) => {
                    console.log("Zooming...", chart);
                }
            },
            pan: {
                enabled: true,
                mode: 'xy',
                threshold: 0,
                onPan: ({chart}) => {
                    console.log("Panning...", chart);
                },
                onPanComplete: ({chart}) => {
                    console.log("pan complete", chart);
                }
            }
        }
    }
  }
});

// Random colors for chart lines
function getRandomColor() {
    return `hsl(${Math.floor(Math.random() * 360)}, 70%, 50%)`;
}

// Update chart with cached data
function updateChart() {
    if (isTrading || chartPaused || latestData.length === 0) return;

    let currentTime = new Date().toLocaleTimeString();
    if (
        stockChart.data.labels.length === 0 ||
        stockChart.data.labels[stockChart.data.labels.length - 1] !== currentTime
    ) {
        stockChart.data.labels.push(currentTime);
    }

    latestData.forEach(stock => {
        if (!datasetMap[stock.symbol]) {
            let newDataset = {
                label: stock.symbol,
                data: [],
                borderColor: getRandomColor(),
                borderWidth: 2,
                fill: false
            };
            datasetMap[stock.symbol] = newDataset;
            stockChart.data.datasets.push(newDataset);
        }
        datasetMap[stock.symbol].data.push(stock.price);
    });

    stockChart.update();
}

// ================== BUY FUNCTION ==================
async function buyStock(symbol) {
    const qty = prompt(`Enter quantity of ${symbol} to buy:`);
    if (!qty) return;

    isTrading = true;
    chartPaused = true;
    try {
        const res = await fetch("/api/stocks/buy", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({symbol, qty})
        });
        const result = await res.json();
        alert(result.message);
    } catch (err) {
        console.error("Buy request failed: ", err);
    } finally {
        isTrading = false;
        chartPaused = false;
        await fetchStockList();
        loadCompanies();
    }
}

// ================== SELL FUNCTION ==================
async function sellStock(symbol) {
    const qty = prompt(`Enter quantity of ${symbol} to sell:`);
    if (!qty) return;

    isTrading = true;
    chartPaused = true;
    try {
        const res = await fetch("/api/stocks/sell", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({symbol, qty})
        });
        const result = await res.json();
        if (!res.ok) { alert(result.message); return; }
        alert(result.message);
        document.querySelector(".money").textContent = `+$ ${parseFloat(result.new_balance).toFixed(2)}`;
        if(document.querySelector(".total_shares")) 
            document.querySelector(".total_shares").textContent = result.total_shares;
    } catch (err) {
        console.error("Sell request failed: ", err);
    } finally {
        isTrading = false;
        chartPaused = false;
        await fetchStockList();
        loadCompanies();
    }
}

// ================== AUTO REFRESH ==================
// Every 5s fetch once and refresh everything
setInterval(async () => {
    await fetchStockList();
    loadCompanies();
    updateChart();
}, 5000);

// Initial load
(async () => {
    await fetchStockList();
    loadCompanies();
})();

// ================== ZOOM CONTROLS ==================
function zoomIn(){
    stockChart.zoom(1.2); // zoom in by 20%
}
function zoomOut(){
    stockChart.zoom(0.8); // zoom out by 20%
}
function resetZoom(){
    stockChart.resetZoom();
}
