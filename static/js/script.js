// =================================================
// SKYKASH MASTER SCRIPT (Chrome + Edge Safe)
// =================================================

if ("scrollRestoration" in history) {
    history.scrollRestoration = "manual";
}

// HARD scroll reset (refresh + Edge cache)
window.addEventListener("load", () => {
    setTimeout(() => window.scrollTo(0, 0), 50);
});

document.addEventListener("DOMContentLoaded", () => {

    console.log("✅ Skykash JS Loaded");

    // =================================================
    // FLASH MESSAGES
    // =================================================
    document.querySelectorAll(".flash-alert").forEach((flash, i) => {

        flash.querySelector(".btn-close")?.addEventListener("click", () => flash.remove());

        setTimeout(() => {
            flash.style.transition = "0.4s";
            flash.style.opacity = "0";
            setTimeout(() => flash.remove(), 400);
        }, 3500 + (i * 700));
    });

    // =================================================
    // PREDICT FORM
    // =================================================
    const form = document.getElementById("predictForm");
    if (!form) return;

    const source = form.querySelector('[name="source"]');
    const destination = form.querySelector('[name="destination"]');
    const depDate = form.querySelector('[name="dep_date"]');
    const depTime = form.querySelector('[name="dep_time"]');
    const arrDate = form.querySelector('[name="arr_date"]');
    const arrTime = form.querySelector('[name="arr_time"]');
    const btn = document.getElementById("predictBtn");
    const spinner = document.getElementById("spinner");

    // =================================================
    // DATE LIMIT (NO PAST)
    // =================================================
    const today = new Date().toISOString().split("T")[0];
    depDate.min = today;
    arrDate.min = today;

    // =================================================
    // SOURCE / DESTINATION LOCK
    // =================================================
    function syncLocations() {
        [...destination.options].forEach(o => o.disabled = o.value === source.value && o.value !== "");
        [...source.options].forEach(o => o.disabled = o.value === destination.value && o.value !== "");
    }

    // =================================================
    // DATE / TIME SYNC
    // =================================================
 function syncDateTime() {

if(!depDate.value || !depTime.value) return;

const dep = new Date(depDate.value + "T" + depTime.value);
dep.setMinutes(dep.getMinutes() + 70);

// LOCAL date parts (NOT UTC)
const yyyy = dep.getFullYear();
const mm = String(dep.getMonth()+1).padStart(2,"0");
const dd = String(dep.getDate()).padStart(2,"0");
const hh = String(dep.getHours()).padStart(2,"0");
const min = String(dep.getMinutes()).padStart(2,"0");

const arrCalculatedDate = `${yyyy}-${mm}-${dd}`;
const arrCalculatedTime = `${hh}:${min}`;

// Minimum arrival date
arrDate.min = arrCalculatedDate;

// Auto advance date
if(!arrDate.value || arrDate.value < arrCalculatedDate){
arrDate.value = arrCalculatedDate;
}

// Auto advance time
if(!arrTime.value || (arrDate.value===arrCalculatedDate && arrTime.value < arrCalculatedTime)){
arrTime.value = arrCalculatedTime;
}

// Same-day → restrict time
if(arrDate.value===arrCalculatedDate){
arrTime.min = arrCalculatedTime;
}else{
arrTime.min = "";
}

}




    // =================================================
    // VALIDATION ENGINE
    // =================================================
    function validate() {

    let ok = true;

    if (!source.value || !destination.value) ok = false;
    if (source.value === destination.value) ok = false;

    if (!depDate.value || !depTime.value || !arrDate.value || !arrTime.value) ok = false;

    if (ok) {

        const dep = new Date(depDate.value + "T" + depTime.value);
        const arr = new Date(arrDate.value + "T" + arrTime.value);

        const diffMinutes = (arr - dep) / 60000;

        // // Arrival must be AFTER departure
        // if (diffMinutes <= 0) ok = false;

        // Minimum 70 minutes flight gap
        if (diffMinutes < 70) ok = false;
    }

    btn.disabled = !ok;
}


    // INIT BUTTON STATE
    btn.disabled = true;

    // LISTENERS
    [source, destination].forEach(e => e.addEventListener("change", () => {
        syncLocations();
        validate();
    }));

    [depDate, depTime, arrDate, arrTime].forEach(e => e.addEventListener("change", () => {
        syncDateTime();
        validate();
    }));

    // =================================================
    // FORM SUBMIT
    // =================================================
    form.addEventListener("submit", e => {

        validate();

        if (btn.disabled) {
            e.preventDefault();
            document.getElementById("formErrors")?.classList.remove("d-none");
            window.scrollTo({ top: 0, behavior: "smooth" });
            return;
        }

        spinner?.classList.remove("d-none");
    });

    // =================================================
    // SCROLL TO RESULT AFTER POST
    // =================================================
    setTimeout(() => {
        const r = document.getElementById("prediction-result");
        if (r) r.scrollIntoView({ behavior: "smooth", block: "center" });
    }, 600);

});
