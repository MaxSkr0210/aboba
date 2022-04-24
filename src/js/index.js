const sectionsArr = document.querySelectorAll("section");
const links = document.querySelectorAll(".nav-link");

links[0].className = "activated nav-link text-white"
links[0].style.borderBottom = "2px solid #fff"

let i = 0;

sectionsArr[0].style.top = "0px"

//scroll section bottom/top
document.addEventListener("keydown", function(event){
    if (event.keyCode === 40){
        if (i === sectionsArr.length - 1) return;
        i = animBottom(i);
        disActivated(links[i - 1]);
        active(links[i]);
    }
    if (event.keyCode === 38) {
        i = animTop(i);
        disActivated(links[i + 1]);
        active(links[i]);
    }
})


//click to links then scroll to need section
const smoothLinks = document.querySelectorAll('a[href^="#"]');
let prev = smoothLinks[0];
smoothLinks.forEach((item) => {
    item.addEventListener('click', function (e) {
        e.preventDefault();
        const id = Number(item.getAttribute('href')[1]);

        active(item);
        disActivated(prev);
        prev = item;

        if (id < i && i !== 0){
            while (id < i){
                i = animTop(i);
            }

            return;
        }
        if (id > i){
            while (id > i){
                i = animBottom(i);
            }

            return;
        }
    });
})