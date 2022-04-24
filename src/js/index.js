const sectionsArr = document.querySelectorAll("section");

let i = 0;

sectionsArr[0].style.top = "0px"

//scroll section bottom/top
document.addEventListener("keydown", function(event){
    if (event.keyCode === 40){
        if (i === sectionsArr.length - 1) return;
        i = animBottom(i);
    }
    if (event.keyCode === 38) i = animTop(i);
})

//click to links then scroll to need section
const smoothLinks = document.querySelectorAll('a[href^="#"]');
for (let smoothLink of smoothLinks) {
    smoothLink.addEventListener('click', function (e) {
        e.preventDefault();
        const id = Number(smoothLink.getAttribute('href')[1]);

        console.log(id);

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
};