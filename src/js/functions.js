const classes = "d-flex align-items-center justify-content-center scrollAnimBottom"

function animBottom(i){
    sectionsArr[i + 1].className = classes;
    sectionsArr[i + 1].style.top = "0px";

    return ++i;
}

function animTop(i){
    if (i === 0){
        return 0;
    }
    sectionsArr[i].className = classes;
    sectionsArr[i].style.top = "-1000px";
    
    return --i;
}

function active(item){
    item.className = "activated nav-link text-white";
    item.style.borderBottom = "2px solid #fff"
}

function disActivated(item){
    item.style.borderBottom = "none"
}