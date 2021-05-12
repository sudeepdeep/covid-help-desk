const getStarted = () =>{
    const startBtn = document.querySelector('.first button');
    const firstScreen = document.querySelector('.first');
    const secondScreen = document.querySelector('.second');

    startBtn.addEventListener('click',() => {
        firstScreen.classList.add("fadeOut");
    });
};

getStarted();