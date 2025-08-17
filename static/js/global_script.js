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

