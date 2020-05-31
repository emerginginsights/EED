'use strict'

let menuBlock = document.querySelector('.menu__block');
let burger = document.querySelector('.burger');

burger.addEventListener('mouseover', () => {
	menuBlock.classList.toggle('menu__block__active');
})

