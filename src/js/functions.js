const classes = "d-flex align-items-center scrollAnimBottom"

function animBottom(i){
    sectionsArr[i + 1].className = classes;
    sectionsArr[i + 1].style.top = "72px";

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